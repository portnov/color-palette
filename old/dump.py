#!/usr/bin/python

from math import floor
from colorsys import rgb_to_hsv
from color import mixRYB

STEP=0.05

r = 0.
while r < 1.0:
    y = 0.
    while y < 1.0:
        b = 0.
        while b < 1.0:
            R,G,B = mixRYB(r,y,b)
            h,s,v = rgb_to_hsv(R,G,B)
            print floor(v*100),
#             print floor(R*255),floor(G*255),floor(B*255)
            b += STEP
        print ''
        y += STEP
#     print ''
    r += STEP
             
