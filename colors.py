from math import cos, acos, sqrt, pi
from PyQt4 import QtGui, QtCore
import colorsys
import lcms

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
    
R=[c/255.0 for c in (254.0,39.0,18.0)]
Y=[c/255.0 for c in (254.0,255.0,51.0)]
B=[c/255.0 for c in (2.0, 81.0, 254.0)]

def chg(x):
    return (x*x + x)/2.

def chg1(y):
    """ Y >= -1/8. """
    return (sqrt(8*y+1)-1)/2. 

def mixRYB(qR,qY,qB):
    r =  (qR*R[0] + qY*Y[0] + qB*B[0])
    g =  (qR*R[1] + qY*Y[1] + qB*B[1])
    b =  (qR*R[2] + qY*Y[2] + qB*B[2])
    if r > 1:
        r = 1.
    if g > 1:
        g = 1.
    if b > 1:
        b = 1.
    return r,g,b

def rgb2ryb(r,g,b):
    rr = 1.166899171946144 * r - 1.239542922240454 * g + 0.38609912739206 * b
    ry = - 0.16256805363876 * r + 1.240812985159507 * g - 0.39441226649859 * b
    rb = - 0.050052025037218 * r - 0.16129799071971 * g + 1.05576866652902 * b
# TODO: warn about color clipping
    return (clip(rr), clip(ry), clip(rb))

vY = 1.0
vR = 0.9
vB = 0.7

hR = 0.
hY = 1./6
hB = 2./3

def simple_mix(x1,a,x2,b):
    if a==b==0:
        return (x1+x2)/2.
    q = float(b)/(a+b)
    h = (1.-q)*x1 + q*x2
#     print 'simple_mix/ q: %.2f' % q
    return h

def mixRYB_hsv(qR,qY,qB):
    return colorsys.rgb_to_hsv(*mixRYB(qR,qY,qB))

# RYBHSV -> RGB1
def rybhsv2rgb(h1,s1,v1):
    if h1 < 1./3:
        q = h1*3
        h2,s2,v2 = mixRYB_hsv(chg(1-q),chg(q),0.)
    elif h1 < 2./3:
        q = (h1-1./3)*3
        h2,s2,v2 = mixRYB_hsv(0,chg(1-q),chg(q))
    else:
        q = (h1-2./3)*3
        h2,s2,v2 = mixRYB_hsv(chg(q),0,chg(1-q))
    #r,g,b = colorsys.hsv_to_rgb(h2, s1*s2, v1*v2)
    #r,g,b = colorsys.hsv_to_rgb(h2, s2, v2)
    r,g,b = colorsys.hsv_to_rgb(h2, s1, v1)
    return r,g,b

# RGB1 -> RYBHSV
def rgb2rybhsv(r,g,b):
    h1,s1,v1 = colorsys.rgb_to_hsv(r,g,b)
    if h1 < 1./6:        # Between R and Y
        q = h1*6
        h2 = simple_mix(0.,chg1(1-q), 1./3,chg1(q))
    elif h1 < 2./3:       # Between Y and B
        q = (h1-1./6)*2
        h2 = simple_mix(1./3,chg1(1-q), 2./3, chg1(q))
    else:                # Between B and R
        q = (h1-2./3)*3
        h2 = simple_mix(2./3,chg1(1-q), 1.,chg1(q))
    return h2, s1, v1

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
    
    def setRYB(self, rybhsv):
        rgb = rybhsv2rgb(*rybhsv)
        self.setRGB1(rgb)
    
    def getRYB(self):
        return rgb2rybhsv(*self.getRGB1())
    
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
        result += "RYB: {:.2f} {:.2f} {:.2f}\n".format(rr, ry, rb)
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
