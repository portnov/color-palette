
from math import sqrt, sin, cos
from PyQt5 import QtGui
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

def Opposite(space):
    class OppositeH(Harmony):
        uses_parameter = False

        @classmethod
        def get(cls, color, parameter=None):
            h, s, v = space.getCoords(color)
            h = h + 0.5
            if h > 1.0:
                h -= 1.0
            return [color, space.fromCoords((h, s, v))]
    return OppositeH

def SplitComplimentary(space):
    class SplitComplimentaryH(Harmony):
        uses_parameter = True
        @classmethod
        def get(cls, color, parameter):
            h, s, v = space.getCoords(color)
            h += (1.0 - 0.4*parameter)/2.0
            if h > 1.0:
                h -= 1.0
            c1 = space.fromCoords((h,s,v))
            h += 0.4*parameter
            if h > 1.0:
                h -= 1.0
            c2 = space.fromCoords((h,s,v))
            return [c1, color, c2]
    return SplitComplimentaryH

def circle(i, n, h, max=1.0):
    h += i*max/n
    if h > max:
        h -= max 
    return h

def Similar(space, n):
    class SimilarH(Harmony):
        uses_parameter = True
        @classmethod
        def get(cls, color, parameter):
            h, s, v = space.getCoords(color)
            step = 0.2*parameter
            hmin = h - (n//2)*step
            hmax = h + (n//2)*step
            return [space.fromCoords((dh % 1.0, s,v)) for dh in seq(hmin, hmax, step)]
    return SimilarH

def SimilarAndOpposite(space):
    class SimilarAndOppositeH(Harmony):
        uses_parameter = True
        @classmethod
        def get(cls, color, parameter):
            h, c, y = space.getCoords(color)
            h1 = h + 0.2*parameter
            if h1 > 1.0:
                h1 -= 1.0
            h2 = h - 0.2*parameter
            if h2 < 0.0:
                h2 += 1.0
            h3 = h + 0.5
            if h3 > 1.0:
                h3 -= 1.0
            return [space.fromCoords((h1,c,y)), color, space.fromCoords((h2,c,y)), space.fromCoords((h3,c,y))]
    return SimilarAndOppositeH

def Rectangle(space):
    class RectangleH(Harmony):
        uses_parameter = True
        @classmethod
        def get(cls, color, parameter):
            h, c, y = space.getCoords(color)
            h1 = (h + 0.2*parameter) % 1.0
            h2 = (h1 + 0.5) % 1.0
            h3 = (h + 0.5) % 1.0
            return [color, space.fromCoords((h1,c,y)), space.fromCoords((h2,c,y)), space.fromCoords((h3,c,y))]
    return RectangleH

def NHues(space, n):
    class Hues(Harmony):
        uses_parameter = False
        @classmethod
        def get(cls, color, parameter=None):
            h, s, v = space.getCoords(color)
            return [space.fromCoords((circle(i,n,h), s, v)) for i in range(n)]

    return Hues

def FiveColors(space):
    class Hues5(Harmony):
        uses_parameter = True
        @classmethod
        def get(cls, color, parameter):
            h0,s,v = space.getCoords(color)
            h1s = (h0 + oneThird) % 1.0
            h2s = (h1s + oneThird) % 1.0
            delta = 0.06*parameter
            h1 = (h1s - delta) % 1.0
            h2 = (h1s + delta) % 1.0
            h3 = (h2s - delta) % 1.0
            h4 = (h2s + delta) % 1.0
            return [color] + [space.fromCoords((h,s,v)) for h in [h1,h2,h3,h4]]
    return Hues5

class LabSimilar(Harmony):
    uses_parameter = True

    @classmethod
    def get(cls, color, parameter):
        l,a,b = color.getLab()
        rho = sqrt(a**2 + b**2)
        if rho < 0.01:
            return [color, color, color]
        delta = parameter * 80.0
        a1 = clip(a + delta*b/rho, -127.0, 127.0)
        b1 = clip(b - delta*a/rho, -127.0, 127.0)
        a2 = clip(a - delta*b/rho, -127.0, 127.0)
        b2 = clip(b + delta*a/rho, -127.0, 127.0)
        return [lab(l,a1,b1), color, lab(l,a2,b2)]

class SimilarAndOppositeLab(Harmony):
    uses_parameter = True

    @classmethod
    def get(cls, color, parameter):
        l,a,b = color.getLab()
        rho = sqrt(a**2 + b**2)
        if rho < 0.01:
            return [color, color, color]
        delta = parameter * 80.0
        a1 = clip(a + delta*b/rho, -127.0, 127.0)
        b1 = clip(b - delta*a/rho, -127.0, 127.0)
        a2 = clip(a - delta*b/rho, -127.0, 127.0)
        b2 = clip(b + delta*a/rho, -127.0, 127.0)
        return [lab(l,a1,b1), color, lab(l,a2,b2), lab(l, -a, -b)]

class Lab5(Harmony):
    uses_parameter = True

    @classmethod
    def get(cls, color, parameter):
        l,a,b = color.getLab()
        rho = sqrt(a**2 + b**2)
        if rho < 0.01:
            return [color, color, color, color, color]
        delta = parameter * 80.0
        delta_a = delta*a/rho
        delta_b = delta*b/rho
        a1 = clip(-a + delta_b, -127.0, 127.0)
        b1 = clip(-b - delta_a, -127.0, 127.0)
        a4 = clip(-a - delta_b, -127.0, 127.0)
        b4 = clip(-b + delta_a, -127.0, 127.0)
        a2 = clip(delta_b/2.0, -127.0, 127.0)
        b2 = clip(-delta_a/2.0, -127.0, 127.0)
        a3 = clip(-delta_b/2.0, -127.0, 127.0)
        b3 = clip(delta_a/2.0, -127.0, 127.0)
        return [lab(l,a1,b1), lab(l,a2,b2), color, lab(l,a3,b3), lab(l, a4,b4)]

class RectangleLab(Harmony):
    uses_parameter = True

    @classmethod
    def get(cls, color, parameter):
        l,a,b = color.getLab()
        alpha = 1.0 * parameter
        a1 = a*cos(alpha) - b*sin(alpha)
        b1 = a*sin(alpha) + b*cos(alpha)
        a1 = clip(a1, -127.0, 127.0)
        b1 = clip(b1, -127.0, 127.0)
        return [color, lab(l,a1,b1), lab(l, -a, -b), lab(l, -a1, -b1)]


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

