
from PyQt4 import QtGui
from colors import *

def allShades(base_colors, shader):
    if shader is None:
        return base_colors
    else:
        all_colors = map(shader.shades, base_colors)
        return sum(all_colors, [])

def variate(x, step=1.0, dmin=1.0, dmax=None):
    if dmax is None:
        dmax = dmin
    return seq(x-dmin, x+dmax, step)

class Harmony(object):
    pass

class Shader(object):
    pass

class SimpleHarmony(Harmony):
    @classmethod
    def get(cls, color):
        l, c, h = color.getLCh()
        #print("Harmony for Hue: " + str(h))
        cs = [clip(x,0.0,100.0) for x in variate(c, 10, 10)]
        ls = [clip(x,0.0,100.0) for x in variate(l, 10, 10)]
        return [lch(l,c,h) for l in ls for c in cs]

class Opposite(Harmony):
    @classmethod
    def get(cls, color):
        h, s, v = color.getHSV()
        h = h + 0.5
        if h > 1.0:
            h -= 1.0
        return [color, hsv(h, s, v)]

def NHues(n):
    def circle(i, h):
        h += i*1.0/n
        if h > 1.0:
            h -= 1.0
        return h

    class Hues(Harmony):
        @classmethod
        def get(cls, color):
            h, s, v = color.getHSV()
            return [hsv(circle(i,h), s, v) for i in range(n)]

    return Hues

class Saturation(Shader):
    @classmethod
    def shades(cls, color):
        h, s, v = color.getHSV()
        ss = [clip(x) for x in variate(s, 0.3, 0.6)]
        return [hsv(h,s,v) for s in ss]


class Value(Shader):
    @classmethod
    def shades(cls, color):
        h, s, v = color.getHSV()
        vs = [clip(x) for x in variate(v, 0.2, 0.4)]
        return [hsv(h,s,v) for v in vs]


