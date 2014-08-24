
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


def circle(i, n, h, max=1.0):
    h += i*max/n
    if h > max:
        h -= max 
    return h

def NHues(n):
    class Hues(Harmony):
        @classmethod
        def get(cls, color):
            h, s, v = color.getHSV()
            return [hsv(circle(i,n,h), s, v) for i in range(n)]

    return Hues

class Similar(Harmony):
    @classmethod
    def get(cls, color):
        h, s, v = color.getHSV()
        h1 = h + 0.1
        if h1 > 1.0:
            h1 -= 1.0
        h2 = h - 0.1
        if h2 < 0.0:
            h2 += 1.0
        return [hsv(h1,s,v), color, hsv(h2,s,v)]

def NHuesRYB(n):
    class Hues_RYB(Harmony):
        @classmethod
        def get(cls, color):
            h, s, v = color.getRYB()
            return [ryb(circle(i,n,h), s, v) for i in range(n)]

    return Hues_RYB

def NHuesLCh(n):
    class Hues_LCh(Harmony):
        @classmethod
        def get(cls, color):
            l,c,h = color.getLCh()
            return [lch(l,c,circle(i,n,h, 360.0)) for i in range(n)]

    return Hues_LCh

class Cooler(Shader):
    @classmethod
    def shades(cls, color):
        h,s,v = color.getHSV()
        if h < 1.0/6.0:
            sign = -1.0
        elif h > 2.0/3.0:
            sign = -1.0
        else:
            sign = 1.0
        step = 0.05
        result = [color]
        for i in range(4):
            h += sign*step
            if h > 1.0:
                h -= 1.0
            elif h < 0.0:
                h += 1.0
            result.append(hsv(h,s,v))
        return result

class Warmer(Shader):
    @classmethod
    def shades(cls, color):
        h,s,v = color.getHSV()
        if h < 1.0/6.0:
            sign = +1.0
        elif h > 2.0/3.0:
            sign = +1.0
        else:
            sign = -1.0
        step = 0.05
        result = [color]
        for i in range(4):
            h += sign*step
            if h > 1.0:
                h -= 1.0
            elif h < 0.0:
                h += 1.0
            result.append(hsv(h,s,v))
        return result

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


