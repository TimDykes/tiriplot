# Tiriplot

A simple python script to plot TiRiFiC models in 3D

Usage: python tiriplot.py tirific_file.dat plotname

tirific_file.dat: input TiRiFiC model
plotname: output file name

The script generates 90 .PNG image frames, covering a 360 degree rotation of the model.

---

### To create a movie

Option 1: Quickly view the movie (using ImageMagick)

animate -delay 10 plotname*.png

Option 2: Produce a small .GIF of the movie (using ImageMagick)

convert -delay 10 -loop 0 -ordered-dither o8x8,23 +map *.png out.gif

Option 3: Produce a regular movie (using ffmpeg)

ffmpeg -r 10 -i plotname%03d.png plotname.avi

---

### Notes

Script uses **numpy,matplotlib**

Expects TiRiFiC format as follows, columns may be provided in any order

```
15
    RADI         VROT           Z0        INCL           PA       
+0.00000E+00 +1.50014E+02 +2.99412E+01 +2.36897E+01 +2.26656E+02 
...
```
---

[TiRiFiC: Tilted Ring Fitting Code](http://gigjozsa.github.io/tirific/)