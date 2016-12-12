#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import csv, sys
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import Circle

# -------------------------------------------------------------
# Pathpatch code from Till Hoffman, StackOverflow
# http://stackoverflow.com/questions/18228966/how-can-matplotlib-2d-patches-be-transformed-to-3d-with-arbitrary-normals
from mpl_toolkits.mplot3d import art3d

def rotation_matrix(d):
    """
    Calculates a rotation matrix given a vector d. The direction of d
    corresponds to the rotation axis. The length of d corresponds to 
    the sin of the angle of rotation.

    Variant of: http://mail.scipy.org/pipermail/numpy-discussion/2009-March/040806.html
    """
    sin_angle = np.linalg.norm(d)

    if sin_angle == 0:
        return np.identity(3)

    d /= sin_angle

    eye = np.eye(3)
    ddt = np.outer(d, d)
    skew = np.array([[    0,  d[2],  -d[1]],
                  [-d[2],     0,  d[0]],
                  [d[1], -d[0],    0]], dtype=np.float64)

    M = ddt + np.sqrt(1 - sin_angle**2) * (eye - ddt) + sin_angle * skew
    return M

def pathpatch_2d_to_3d(pathpatch, z = 0, normal = 'z'):
    """
    Transforms a 2D Patch to a 3D patch using the given normal vector.

    The patch is projected into they XY plane, rotated about the origin
    and finally translated by z.
    """
    if type(normal) is str: #Translate strings to normal vectors
        index = "xyz".index(normal)
        normal = np.roll((1.0,0,0), index)

    normal /= np.linalg.norm(normal) #Make sure the vector is normalised

    path = pathpatch.get_path() #Get the path and the associated transform
    trans = pathpatch.get_patch_transform()

    path = trans.transform_path(path) #Apply the transform

    pathpatch.__class__ = art3d.PathPatch3D #Change the class
    pathpatch._code3d = path.codes #Copy the codes
    pathpatch._facecolor3d = pathpatch.get_facecolor #Get the face color    

    verts = path.vertices #Get the vertices in 2D

    d = np.cross(normal, (0, 0, 1)) #Obtain the rotation vector    
    M = rotation_matrix(d) #Get the rotation matrix

    pathpatch._segment3d = np.array([np.dot(M, (x, y, 0)) + (0, 0, z) for x, y in verts])

def pathpatch_translate(pathpatch, delta):
    """
    Translates the 3D pathpatch by the amount delta.
    """
    pathpatch._segment3d += delta
# -------------------------------------------------------------

# Read delimited file to array (1 line per element)
def readfile(fn, arr):
        with open(fn) as tsv:
            for line in csv.reader(tsv, delimiter=' '):
                arr.append(line)

# Check args
narg = len(sys.argv)
if (narg !=  3):
    print('Error; Usage: ./tiriplot.py tirific_file.txt plotname') 
    exit()

# Read file
fn = sys.argv[1]
tfile = []
readfile(fn, tfile)

ofn = sys.argv[2]

size = int(tfile[0][0])
ids = [x for x in tfile[1] if x]
nids = len(ids)

# Extract data and convert to float, account for blank lines at end of file and extra spaces at end of lines
tdata = [ list(map(float, [ y for y in x if y ])) for x in tfile[2:] if len(x) >= nids ]
inc_idx = ids.index("INCL")
pa_idx = ids.index("PA")

# Check amount of data matches number of entries specified in file
if len(tdata) != size:
    print("Warning: Number of entries specified in line 1 of file: ",size,", number of entries found in data: ",len(tdata))
    size = len(tdata)

# Print some useful info
print("Plotting ", size, " entries of tirific file: ", fn)
print("Column IDs 0 to ",len(ids)-1,": ",ids)
print("Using INCL from column ",inc_idx," and PA from column ",pa_idx)
print("First record: ",tdata[0])
print("Last record: ",tdata[-1])

# Create axes
ax = plt.axes(projection = '3d') 
ax.set_xlim(0,1.5)                               
ax.set_ylim(0,1.5)                               
ax.set_zlim(0,1.5)

# Hide axis lines and panes
ax.set_xticks([])                               
ax.set_yticks([])                               
ax.set_zticks([])
ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0)) 
ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0)) 
ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0)) 
ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0)) 
ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

# Iterate through tirific records
for i in range(0,size):
	inc = np.radians(tdata[i][inc_idx])
	pa = np.radians(tdata[i][pa_idx])

	n = [0,0,1]
	# Inclination angle rotation
	m1_1 = [1,0,0]
	m1_2 = [0,np.cos(inc),-np.sin(inc)]
	m1_3 = [0,np.sin(inc),np.cos(inc)]

	# Position angle rotation
	m2_1 = [np.cos(pa),-np.sin(pa),0]
	m2_2 = [np.sin(pa),np.cos(pa),0]
	m2_3 = [0,0,1]

    # Rotate 
	n1 = [np.dot(m1_1,n),np.dot(m1_2,n),np.dot(m1_3,n)]
	n2 = [np.dot(m2_1,n1),np.dot(m2_2,n1),np.dot(m2_3,n1)]

    # Draw patch
	p = Circle((0,0), tdata[i][0]/tdata[size-1][0], facecolor = 'b', alpha = .05)
	ax.add_patch(p)
	pathpatch_2d_to_3d(p, z = 0, normal = n2)
	pathpatch_translate(p, 0.75)

# Create orbit
for angle in range(0, 90):
	ax.view_init(20, angle*4)
	plt.savefig(ofn+str("_%03d"%angle))

