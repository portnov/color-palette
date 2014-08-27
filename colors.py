
# coding: utf-8

from math import cos, acos, sqrt, pi
from PyQt4 import QtGui, QtCore
import colorsys

try:
    import lcms
    use_lcms = True
    print("LCMS is available")
except ImportError:
    print("LCMS is not available")
    lcms = None
    use_lcms = False


if use_lcms:
    xyz_profile = lcms.cmsCreateXYZProfile()
    D65 = lcms.cmsCIExyY()
    lcms.cmsWhitePointFromTemp(6504, D65)
    lab_profile = lcms.cmsCreateLabProfile(D65)
    rgb_profile = lcms.cmsCreate_sRGBProfile()

    xyz2rgb = lcms.cmsCreateTransform(xyz_profile, lcms.TYPE_XYZ_DBL,
                                      rgb_profile, lcms.TYPE_RGB_8,
                                      lcms.INTENT_PERCEPTUAL,
                                      0)

    rgb2xyz = lcms.cmsCreateTransform(rgb_profile, lcms.TYPE_RGB_8,
                                      xyz_profile, lcms.TYPE_XYZ_DBL,
                                      lcms.INTENT_PERCEPTUAL,
                                      0)

    lab2rgb = lcms.cmsCreateTransform(lab_profile, lcms.TYPE_Lab_DBL,
                                      rgb_profile, lcms.TYPE_RGB_8,
                                      lcms.INTENT_PERCEPTUAL,
                                      0)

    rgb2lab = lcms.cmsCreateTransform(rgb_profile, lcms.TYPE_RGB_8,
                                      lab_profile, lcms.TYPE_Lab_DBL,
                                      lcms.INTENT_PERCEPTUAL,
                                      0)

    def lab_to_rgb(l,a,b):
        lab = lcms.cmsCIELab(l,a, b)
        rgb = lcms.COLORB()
        rgb[0] = rgb[1] = rgb[2] = 0
        lcms.cmsDoTransform(lab2rgb, lab, rgb, 1)
#     return rgb
        return rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0

    def rgb_to_lab(r, g, b):
        rgb = lcms.COLORB()
        rgb[0] = r
        rgb[1] = g
        rgb[2] = b    
        lab = lcms.cmsCIELab(0, 0, 0)
        lcms.cmsDoTransform(rgb2lab, rgb, lab, 1)
        return lab.L, lab.a, lab.b

    def lch_to_rgb(l, c, h):
        lch = lcms.cmsCIELCh(l, c, h)
        #lch[0] = l
        #lch[1] = c
        #lch[2] = h
        lab = lcms.cmsCIELab(0, 0, 0)
        lcms.cmsLCh2Lab(lab, lch)
        return lab_to_rgb(lab.L,  lab.a, lab.b)

    def rgb_to_lch(r, g, b):
        l, a, b = rgb_to_lab(r, g, b)
        lab = lcms.cmsCIELab(l, a, b)
        lch = lcms.cmsCIELCh(0, 0, 0)
        lcms.cmsLab2LCh(lch, lab)
        return lch.L, lch.C, lch.h
    
#HCYwts = 0.299, 0.587, 0.114


## HCY colour space.
#
# Copy&Paste from https://raw.githubusercontent.com/mypaint/mypaint/master/gui/colors/uicolor.py
# Copyright (C) 2012-2013 by Andrew Chadwick <andrewc-git@piffle.org>
#

# Frequently referred to as HSY, Hue/Chroma/Luma, HsY, HSI etc.  It can be
# thought of as a cylindrical remapping of the YCbCr solid: the "C" term is the
# proportion of the maximum permissible chroma within the RGB gamut at a given
# hue and luma. Planes of constant Y are equiluminant.
# 
# ref https://code.google.com/p/colour-space-viewer/
# ref git://anongit.kde.org/kdelibs in kdeui/colors/kcolorspaces.cpp
# ref http://blog.publicfields.net/2011/12/rgb-hue-saturation-luma.html
# ref Joblove G.H., Greenberg D., Color spaces for computer graphics.
# ref http://www.cs.rit.edu/~ncs/color/t_convert.html
# ref http://en.literateprograms.org/RGB_to_HSV_color_space_conversion_(C)
# ref http://lodev.org/cgtutor/color.html
# ref Levkowitz H., Herman G.T., "GLHS: a generalized lightness, hue, and
#     saturation color model"

# For consistency, use the same weights that the Color and Luminosity layer
# blend modes use, as also used by brushlib's Colorize brush blend mode. We
# follow http://www.w3.org/TR/compositing/ here. BT.601 YCbCr has a nearly
# identical definition of luma.

_HCY_RED_LUMA = 0.299
_HCY_GREEN_LUMA = 0.587
_HCY_BLUE_LUMA = 0.114

def RGB_to_HCY(rgb):
    """RGB → HCY: R,G,B,H,C,Y ∈ [0, 1]

    :param rgb: Color expressed as an additive RGB triple.
    :type rgb: tuple (r, g, b) where 0≤r≤1, 0≤g≤1, 0≤b≤1.
    :rtype: tuple (h, c, y) where 0≤h<1, but 0≤c≤2 and 0≤y≤1.

    """
    r, g, b = rgb

    # Luma is just a weighted sum of the three components.
    y = _HCY_RED_LUMA*r + _HCY_GREEN_LUMA*g + _HCY_BLUE_LUMA*b

    # Hue. First pick a sector based on the greatest RGB component, then add
    # the scaled difference of the other two RGB components.
    p = max(r, g, b)
    n = min(r, g, b)
    d = p - n   # An absolute measure of chroma: only used for scaling.
    if n == p:
        h = 0.0
    elif p == r:
        h = (g - b)/d
        if h < 0:
            h += 6.0
    elif p == g:
        h = ((b - r)/d) + 2.0
    else: # p==b
        h = ((r - g)/d) + 4.0
    h /= 6.0

    # Chroma, relative to the RGB gamut envelope.
    if r == g == b:
        # Avoid a division by zero for the achromatic case.
        c = 0.0
    else:
        # For the derivation, see the GLHS paper.
        c = max((y-n)/y, (p-y)/(1-y))
    return h, c, y

def HCY_to_RGB(hcy):
    """HCY → RGB: R,G,B,H,C,Y ∈ [0, 1]

    :param hcy: Color expressed as a Hue/relative-Chroma/Luma triple.
    :type hcy: tuple (h, c, y) where 0≤h<1, but 0≤c≤2 and 0≤y≤1.
    :rtype: tuple (r, g, b) where 0≤r≤1, 0≤g≤1, 0≤b≤1.

    >>> n = 32
    >>> diffs = [sum( [abs(c1-c2) for c1, c2 in
    ...                zip( HCY_to_RGB(RGB_to_HCY([r/n, g/n, b/n])),
    ...                     [r/n, g/n, b/n] ) ] )
    ...          for r in range(int(n+1))
    ...            for g in range(int(n+1))
    ...              for b in range(int(n+1))]
    >>> sum(diffs) < n*1e-6
    True

    """
    h, c, y = hcy

    if c == 0:
        return y, y, y

    h %= 1.0
    h *= 6.0
    if h < 1:
        #implies (p==r and h==(g-b)/d and g>=b)
        th = h
        tm = _HCY_RED_LUMA + _HCY_GREEN_LUMA * th
    elif h < 2:
        #implies (p==g and h==((b-r)/d)+2.0 and b<r)
        th = 2.0 - h
        tm = _HCY_GREEN_LUMA + _HCY_RED_LUMA * th
    elif h < 3:
        #implies (p==g and h==((b-r)/d)+2.0 and b>=g)
        th = h - 2.0
        tm = _HCY_GREEN_LUMA + _HCY_BLUE_LUMA * th
    elif h < 4:
        #implies (p==b and h==((r-g)/d)+4.0 and r<g)
        th = 4.0 - h
        tm = _HCY_BLUE_LUMA + _HCY_GREEN_LUMA * th
    elif h < 5:
        #implies (p==b and h==((r-g)/d)+4.0 and r>=g)
        th = h - 4.0
        tm = _HCY_BLUE_LUMA + _HCY_RED_LUMA * th
    else:
        #implies (p==r and h==(g-b)/d and g<b)
        th = 6.0 - h
        tm = _HCY_RED_LUMA + _HCY_BLUE_LUMA * th

    # Calculate the RGB components in sorted order
    if tm >= y:
        p = y + y*c*(1-tm)/tm
        o = y + y*c*(th-tm)/tm
        n = y - (y*c)
    else:
        p = y + (1-y)*c
        o = y + (1-y)*c*(th-tm)/(1-tm)
        n = y - (1-y)*c*tm/(1-tm)

    # Back to RGB order
    if h < 1:   return (p, o, n)
    elif h < 2: return (o, p, n)
    elif h < 3: return (n, p, o)
    elif h < 4: return (n, o, p)
    elif h < 5: return (o, n, p)
    else:       return (p, n, o)

R=[c/255.0 for c in (254.0,39.0,18.0)]
Y=[c/255.0 for c in (254.0,255.0,51.0)]
B=[c/255.0 for c in (2.0, 81.0, 254.0)]

hR = 0.
hY = 0.16748366013071894
hB = 0.6144179894179894

oneThird = 1.0/3.0
twoThirds = 2.0/3.0

def RGB_to_RYBHCY(r,g,b):
    h,c,y = RGB_to_HCY((r,g,b))
    if h < hY:
        q = h/hY
        h = q * oneThird
    elif h < hB:
        q = (h-hY)/(hB-hY)
        h = oneThird + q*oneThird
    else: # h > hB
        q = (h-hB)/(1.0-hB)
        h = twoThirds + q*oneThird
    return (h, c, y)

def RYBHCY_to_RGB(h,c,y):
    if h < oneThird:
        q = h * 3.0
        h = q*hY
    elif h < twoThirds:
        q = (h-oneThird)*3.0
        h = hY + q*(hB-hY)
    else: # h > 2/3
        q = (h-twoThirds)*3.0
        h = hB + q*(1.0-hB)
    return HCY_to_RGB((h,c,y))

def seq(start, stop, step=1):
    n = int(round((stop - start)/float(step)))
    if n > 1:
        return([start + step*i for i in range(n+1)])
    else:
        return([])

class Color(QtGui.QColor):
    def __init__(self, *args):
        if len(args) == 3:
            r, g, b = args
            #print(r, g, b)
            QtGui.QColor.__init__(self, r, g, b)
            self._rgb = (r, g, b)
        elif len(args) == 1:
            qcolor = args[0]
            QtGui.QColor.__init__(self, qcolor)
            r, g, b, a = qcolor.getRgb()
            self._rgb = (r,g,b)
        else:
            QtGui.QColor.__init__(self, *args)
            self._rgb = None
    
    def getRGB(self):
        r, g, b, a = self.getRgb()
        return (r, g, b)
    
    def getRGB1(self):
        r, g, b, a = self.getRgb()
        return (r/255., g/255., b/255.)
    
    def setRGB1(self, rgb):
        r, g, b = rgb
        self.setRGB((255.0*r, 255.0*g, 255.0*b))
    
    def setRGB(self, rgb):
        r, g, b = rgb
        #print(r, g, b)
        self.setRgb(r, g, b)
        self._rgb = rgb
    
    def getHSV(self):
        r, g, b = self._rgb
        eps = 0.001
        if abs(max(r,g,b)) < eps:
            return (0,0,0)
        return colorsys.rgb_to_hsv(r/255., g/255., b/255.)
    
    def getHLS(self):
        r, g, b = self._rgb
        return colorsys.rgb_to_hls(r/255., g/255., b/255.)
    
    def setHSV(self, hsv):
        rgb = colorsys.hsv_to_rgb(*hsv)
        self.setRGB1(rgb)
    
    def setHLS(self, hls):
        r, g, b = colorsys.hls_to_rgb(*hls)
        self.setRGB((r*255, g*255, b*255))
    
    def setRYB(self, rybhcy):
        rgb = RYBHCY_to_RGB(*rybhcy)
        self.setRGB1(rgb)
    
    def getRYB(self):
        return RGB_to_RYBHCY(*self.getRGB1())
    
    def getCMYK(self):
        c, m, y, k, a = self.getCmykF()
        return (c, m, y, k)
    
    def setCMYK(self, cmyk):
        self.setCmykF(*cmyk)
        r, g, b, a = self.getRgb()
        self._rgb = (r, g, b)
    
    def getCMY(self):
        r, g, b = self.getRGB1()
        return (1.0-r, 1.0-g, 1.0-b)
    
    def setCMY(self, cmy):
        c, m, y = cmy
        self.setRGB1((1.0-c, 1.0-m, 1.0-y))
        
    def getLab(self):
        r, g, b = self.getRGB()
        return rgb_to_lab(r, g, b)
    
    def setLab(self, lab):
        r, g, b = lab_to_rgb(*lab)
        self.setRGB1((r, g, b))
        
    def getLCh(self):
        r, g, b = self.getRGB()
        return rgb_to_lch(r, g, b)
    
    def setLCh(self, lch):
        r, g, b = lch_to_rgb(*lch)
        self.setRGB1((r, g, b))

    def setHCY(self, hcy):
        rgb = HCY_to_RGB(hcy)
        self.setRGB1(rgb)

    def getHCY(self):
        rgb = self.getRGB1()
        return RGB_to_HCY(rgb)

    def invert(self):
        r, g, b = self._rgb
        return Color(255-r, 255-g, 255-b)
    
    def getVisibleColor(self):
        h,s,v = self.getHSV()
        return hsv(1-h,1.0,1-v)
    
    def hex(self):
        r,g,b = self.getRGB()
        return "#{:02x}{:02x}{:02x}".format(r,g,b)
    
    def verbose(self):
        r, g, b = self.getRGB1()
        rr, ry, rb = self.getRYB()
        h, s, l = self.getHLS()
        result = "RGB: {:.2f} {:.2f} {:.2f}\n".format(r, g, b)
        result += "HLS: {:.2f} {:.2f} {:.2f}\n".format(h, l, s)
        h, s, v = self.getHSV()
        result += "HSV: {:.2f} {:.2f} {:.2f}".format(h, s, v)
        return result
    
    def __str__(self):
        r, g, b = self.getRGB1()
        return "<RGB: {:.2f} {:.2f} {:.2f}>".format(r, g, b)

def clip(x, min=0.0, max=1.0):
    if x < min:
        #print("{:.2f} clipped up to {:.2f}".format(x, min))
        return min
    if x > max:
        #print("{:.2f} clipped down to {:.2f}".format(x, max))
        return max
    return x

def hls(h, l, s):
    color = Color()
    color.setHLS((h, l, s))
    return color

def hsv(h, s, v):
    color = Color()
    color.setHSV((h, s, v))
    return color

def ryb(r, y, b):
    color = Color()
    color.setRYB((r,y,b))
    return color

def lch(l, c, h):
    color = Color()
    color.setLCh((l,c,h))
    return color

def fromHex(s):
    t = s[1:]
    if len(t) == 3:
        rs,gs,bs = t[0]+t[0], t[1]+t[1], t[2]+t[2]
    else:
        rs,gs,bs = t[0:2], t[2:4], t[4:6]
    r,g,b = int(rs,16), int(gs,16), int(bs,16)
    return Color(r,g,b)

def darker(clr, q):
    h,s,v = clr.getHSV()
    v = clip(v-q)
    return hsv(h,s,v)

def lighter(clr, q):
    h,s,v = clr.getHSV()
    v = clip(v+q)
    return hsv(h,s,v)

def saturate(clr, q):
    h,s,v = clr.getHSV()
    s = clip(s+q)
    return hsv(h,s,v)

def desaturate(clr, q):
    h,s,v = clr.getHSV()
    s = clip(s-q)
    return hsv(h,s,v)

def increment_hue(clr, q):
    h,s,v = clr.getHSV()
    h += q
    if h > 1.0:
        h -= 1.0
    if h < 1.0:
        h += 1.0
    return hsv(h,s,v)

def contrast(clr, q):
    h,s,v = clr.getHSV()
    v = (v - 0.5)*(1.0 + q) + 0.5
    v = clip(v)
    return hsv(h,s,v)

def linear(x, y, q):
    return (1.-q)*x + q*y

def linear3(v1, v2, q):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (linear(x1, x2, q), linear(y1, y2, q), linear(z1, z2, q))

def circular(h1, h2, q, circle=1.0):
    #print("Src hues: "+ str((h1, h2)))
    d = h2 - h1
    if h1 > h2:
        h1, h2 = h2, h1
        d = -d
        q = 1.0 - q
    if d > circle/2.0:
        h1 = h1 + circle
        h = linear(h1, h2, q)
    else:
        h = h1 + q*d
    if h >= circle:
        h -= circle
    #print("Hue: "+str(h))
    return h


if __name__ == "__main__":
    l, a, b = rgb_to_lab(50, 70, 200)
    print ((l, a, b))
    r, g, b = lab_to_rgb(l, a, b)
    print ((r*255, g*255, b*255))
    
    
#    c = Color()
#    c.setRGB((127, 255, 0))
#    ryb = c.getRYB()
#    print(ryb, str(c))
#    
#    c2 = Color()
#    c2.setRYB(ryb)
#    
#    print(c.getRGB(),  c2.getRGB())
