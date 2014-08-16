
from PyQt4 import QtGui
from colors import *

def variate(x, step=1.0, dmin=1.0, dmax=None):
    if dmax is None:
        dmax = dmin
    return seq(x-dmin, x+dmax, step)

class SimpleHarmony(object):
    @classmethod
    def get(cls, color):
        l, c, h = color.getLCh()
        #print("Harmony for Hue: " + str(h))
        cs = [clip(x,0.0,100.0) for x in variate(c, 10, 10)]
        ls = [clip(x,0.0,100.0) for x in variate(l, 10, 10)]
        return [lch(l,c,h) for l in ls for c in cs]

class Opposite(object):
    @classmethod
    def get(cls, color):
        h, s, v = color.getHSV()
        h = h + 0.5
        if h > 1.0:
            h -= 1.0
        return [hsv(h, s, v)]

def NHues(n):
    def circle(i, h):
        h += i*1.0/n
        if h > 1.0:
            h -= 1.0
        return h

    class Hues(object):
        @classmethod
        def get(cls, color):
            h, s, v = color.getHSV()
            return [hsv(circle(i,h), s, v) for i in range(n)]

    return Hues

