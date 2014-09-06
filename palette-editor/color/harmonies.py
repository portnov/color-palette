
from PyQt4 import QtGui
from color.colors import *

def allShades(base_colors, shader, parameter):
    if shader is None:
        return base_colors
    else:
        all_colors = [shader.shades(c, parameter) for c in base_colors]
        return sum(all_colors, [])

def variate(x, step=1.0, dmin=1.0, dmax=None):
    if dmax is None:
        dmax = dmin
    return seq(x-dmin, x+dmax, step)

class Harmony(object):
    pass

class Shader(object):
    pass

class Opposite(Harmony):

    uses_parameter = False

    @classmethod
    def get(cls, color, parameter=None):
        h, s, v = color.getHSV()
        h = h + 0.5
        if h > 1.0:
            h -= 1.0
        return [color, hsv(h, s, v)]

class TwoOpposite(Harmony):
    uses_parameter = True
    @classmethod
    def get(cls, color, parameter):
        h, s, v = color.getHSV()
        h += (1.0 - 0.4*parameter)/2.0
        if h > 1.0:
            h -= 1.0
        c1 = hsv(h,s,v)
        h += 0.4*parameter
        if h > 1.0:
            h -= 1.0
        c2 = hsv(h,s,v)
        return [c1, color, c2]

def circle(i, n, h, max=1.0):
    h += i*max/n
    if h > max:
        h -= max 
    return h

def NHues(n):
    class Hues(Harmony):
        uses_parameter = False
        @classmethod
        def get(cls, color, parameter=None):
            h, s, v = color.getHSV()
            return [hsv(circle(i,n,h), s, v) for i in range(n)]

    return Hues

class Similar(Harmony):
    uses_parameter = True
    @classmethod
    def get(cls, color, parameter):
        h, s, v = color.getHSV()
        h1 = h + 0.2*parameter
        if h1 > 1.0:
            h1 -= 1.0
        h2 = h - 0.2*parameter
        if h2 < 0.0:
            h2 += 1.0
        return [hsv(h1,s,v), color, hsv(h2,s,v)]

class SimilarAndOpposite(Harmony):
    uses_parameter = True
    @classmethod
    def get(cls, color, parameter):
        h, c, y = color.getHCY()
        h1 = h + 0.2*parameter
        if h1 > 1.0:
            h1 -= 1.0
        h2 = h - 0.2*parameter
        if h2 < 0.0:
            h2 += 1.0
        h3 = h + 0.5
        if h3 > 1.0:
            h3 -= 1.0
        return [hcy(h1,c,y), color, hcy(h2,c,y), hcy(h3,c,y)]

class Rectangle(Harmony):
    uses_parameter = True
    @classmethod
    def get(cls, color, parameter):
        h, c, y = color.getHCY()
        h1 = (h + 0.2*parameter) % 1.0
        h2 = (h1 + 0.5) % 1.0
        h3 = (h + 0.5) % 1.0
        return [color, hcy(h1,c,y), hcy(h2,c,y), hcy(h3,c,y)]

def NHuesRYB(n):
    class Hues_RYB(Harmony):
        uses_parameter = False
        @classmethod
        def get(cls, color, parameter=None):
            h, s, v = color.getRYB()
            return [ryb(circle(i,n,h), s, v) for i in range(n)]

    return Hues_RYB

def NHuesLCh(n):
    class Hues_LCh(Harmony):
        uses_parameter = False
        @classmethod
        def get(cls, color, parameter=None):
            l,c,h = color.getLCh()
            return [lch(l,c,circle(i,n,h, 360.0)) for i in range(n)]

    return Hues_LCh

class Cooler(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h,s,v = color.getHSV()
        if h < 1.0/6.0:
            sign = -1.0
        elif h > 2.0/3.0:
            sign = -1.0
        else:
            sign = 1.0
        step = 0.1*parameter
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
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h,s,v = color.getHSV()
        if h < 1.0/6.0:
            sign = +1.0
        elif h > 2.0/3.0:
            sign = +1.0
        else:
            sign = -1.0
        step = 0.1*parameter
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
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, s, v = color.getHSV()
        ss = [clip(x) for x in variate(s, 0.6*parameter, 1.2*parameter)]
        return [hsv(h,s,v) for s in ss]

class Value(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, s, v = color.getHSV()
        vs = [clip(x) for x in variate(v, 0.4*parameter, 0.8*parameter)]
        return [hsv(h,s,v) for v in vs]

class Chroma(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, c, y = color.getHCY()
        cs = [clip(x) for x in variate(c, 0.4*parameter, 0.8*parameter)]
        return [hcy(h,c,y) for c in cs]

class Luma(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, c, y = color.getHCY()
        ys = [clip(x) for x in variate(y, 0.3*parameter, 0.6*parameter)]
        return [hcy(h,c,y) for y in ys]

class Hue(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, c, y = color.getHCY()
        hs = [clip(x) for x in variate(h, 0.15*parameter, 0.3*parameter)]
        return [hcy(h,c,y) for h in hs]

class HueLuma(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, c, y = color.getHCY()
        hs = [clip(x) for x in variate(h, 0.15*parameter, 0.3*parameter)]
        ys = [clip(x) for x in variate(y, 0.3*parameter, 0.6*parameter)]
        return [hcy(h,c,y) for h,y in zip(hs,ys)]

class LumaPlusChroma(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, c, y = color.getHCY()
        cs = [clip(x) for x in variate(c, 0.4*parameter, 0.8*parameter)]
        ys = [clip(x) for x in variate(y, 0.3*parameter, 0.6*parameter)]
        return [hcy(h,c,y) for c,y in zip(cs,ys)]

class LumaMinusChroma(Shader):
    uses_parameter = True
    @classmethod
    def shades(cls, color, parameter):
        h, c, y = color.getHCY()
        cs = [clip(x) for x in variate(c, 0.4*parameter, 0.8*parameter)]
        ys = reversed( [clip(x) for x in variate(y, 0.3*parameter, 0.6*parameter)] )
        return [hcy(h,c,y) for c,y in zip(cs,ys)]

