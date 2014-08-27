
from math import sin, cos, atan2, sqrt, pi
from colors import *

def mixH(H1, H2, S1, S2, I1, I2, k1, k2):
    numerator = I1*S1*k1*cos(H1) + I2*S2*k2*cos(H2)
    denom = (I1*S1*k1)**2 + (I2*S2*k2)**2 + 2*I1*S1*I2*S2*k1*k2*cos(H1-H2)
    if denom < 0.001:
        return 0.0
    quat = numerator / sqrt(denom)
    return acos(clip(quat, -1, 1))

class Mixer(object):
    @classmethod
    def fromHue(cls, hue):
        c = Color()
        c.setHSV((hue, 1.0, 1.0))
        return c

    @classmethod
    def getHue(cls, color):
        return color.getHLS()[0]

    @classmethod
    def shade(cls, h, s, v):
        return hsv(h, s, v)
    
    @classmethod
    def getShade(cls, color):
        return color.getHSV()

class MixerRGB(Mixer):
    @classmethod
    def mix(cls, c1, c2, q):
        rgb = linear3(c1.getRGB(),  c2.getRGB(), q)
        return Color(*rgb)

def mix_trigonometric(r1,f1, r2,f2, q):
    x = (1-q)*r1*cos(f1) + q*r2*cos(f2)
    y = (1-q)*r1*sin(f1) + q*r2*sin(f2)
    rho = sqrt( q**2 * r2**2 + 2*q*(1-q)*r1*r2*cos(f2-f1) + (1-q)**2 * r1**2 )
    phi = atan2(y, x)
    return (rho, phi)

def mix_wheel(h1,c1, h2, c2, q):
    c, phi = mix_trigonometric(c1, h1*2*pi, c2, h2*2*pi, q)
    h = phi/(2*pi) % 1.0
    return (h, c)

class MixerRYB(Mixer):
    @classmethod
    def fromHue(cls, hue):
        c = Color()
        luma = hue_to_luma(rybhue_to_hue(hue))
        #print luma
        c.setRYB((hue, 1.0, luma))
        return c

    @classmethod
    def getHue(cls, color):
        return color.getRYB()[0]
    
    @classmethod
    def getShade(cls, color):
        return color.getRYB()

    @classmethod
    def shade(cls, h, s, v):
        c = Color()
        c.setRYB((h, s, v))
        return c

    @classmethod
    def mix(cls, clr1, clr2, q):
        h1,c1,y1 = clr1.getRYB()
        h2,c2,y2 = clr2.getRYB()
        h,c = mix_wheel(h1,c1, h2,c2, q)
        y = linear(y1, y2, q)
        result = Color()
        #print("RYB: " + str(ryb))
        result.setRYB((h,c,y))
        return result

class MixerHLS(Mixer):
    @classmethod
    def fromHue(cls, hue):
        c = Color()
        c.setHLS((hue, 0.5, 1.0))
        return c

    @classmethod
    def getHue(cls, color):
        return color.getHLS()[0]

    @classmethod
    def mix(cls, c1, c2, q):
        h1, l1, s1 = c1.getHLS()
        h2, l2, s2 = c2.getHLS()
        h = circular(h1, h2, q)
        l = linear(l1, l2, q)
        s = linear(s1, s2, q)

        hls = (h, l, s)
        result = Color()
        #print("HLS: " + str(hls))
        result.setHLS(hls)
        return result

class MixerHSV(Mixer):
    @classmethod
    def mix(cls, c1, c2, q):
        h1, s1, v1 = c1.getHSV()
        h2, s2, v2 = c2.getHSV()
        h = circular(h1, h2, q)
        s = linear(s1, s2, q)
        v = linear(v1, v2, q)

        hsv = (h,s,v)
        result = Color()
        #print("HLS: " + str(hls))
        result.setHSV(hsv)
        return result

class MixerHCY(Mixer):
    @classmethod
    def fromHue(cls, hue):
        c = Color()
        luma = hue_to_luma(hue)
        c.setHCY((hue, 1.0, luma))
        return c

    @classmethod
    def getHue(cls, color):
        return color.getHCY()[0]

    @classmethod
    def shade(cls, h, c, y):
        result = Color()
        result.setHCY((h,c,y))
        return result

    @classmethod
    def getShade(cls, color):
        return color.getHCY()

    @classmethod
    def mix(cls, clr1, clr2, q):
        h1, c1, y1 = clr1.getHCY()
        h2, c2, y2 = clr2.getHCY()
        h = circular(h1, h2, q)
        c = linear(c1, c2, q)
        y = linear(y1, y2, q)

        result = Color()
        result.setHCY((h,c,y))
        return result

class MixerHSI(Mixer):
    @classmethod
    def mix(cls, c1, c2, q):
        h1, s1, v1 = c1.getHSV()
        h2, s2, v2 = c2.getHSV()
        h = mixH(h1*2*pi, h2*2*pi, s1, s2, v1*pi, v2*pi, 1.0-q, q)/(2*pi)
        s = linear(s1, s2, q)
        v = linear(v1, v2, q)
        #print("HSI/HSV: " + str((h, s, v)))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        c = Color(r*255, g*255, b*255)
        return c

class MixerCMYK(Mixer):
    @classmethod
    def mix(cls, clr1, clr2, q):
        c1, m1, y1, k1 = clr1.getCMYK()
        c2, m2, y2, k2 = clr2.getCMYK()
        c = linear(c1, c2, q)
        m = linear(m1, m2, q)
        y = linear(y1, y2, q)
        k = linear(k1, k2, q)
        result = Color()
        result.setCMYK((c, m, y, k))
        return result

class MixerCMY(Mixer):
    @classmethod
    def mix(cls, clr1, clr2, q):
        c1, m1, y1 = clr1.getCMY()
        c2, m2, y2 = clr2.getCMY()
        #print("CMY({:.2f},{:.2f},{:.2f}) + CMY({:.2f},{:.2f},{:.2f})".format(c1, m1, y1, c2, m2, y2))
        if q <= 0.5:
            k1 = 1.0
            k2 = q*2.0
        else:
            k1 = 2.0*(1.0-q)
            k2 = 1.0
        #print("Ks: "+str((k1, k2)))
        c = k1*c1 + k2*c2
        m = k1*m1 + k2*m2
        y = k1*y1 + k2*y2
        M = max(c, m, y)
        if M > 1.0:
            c = c / M
            m = m / M
            y = y / M
        result = Color()
        result.setCMY((c, m, y))
        return result

if use_lcms:
    class MixerLab(Mixer):
        @classmethod
        def mix(cls, clr1, clr2, q):
            lab1 = clr1.getLab()
            lab2 = clr2.getLab()
            lab = linear3(lab1, lab2, q)
            result = Color()
            result.setLab(lab)
            return result

    class MixerLCh(Mixer):
        @classmethod
        def fromHue(cls, hue):
            c = Color()
            c.setLCh((50.0, 100.0, hue*360.0))
            return c

        @classmethod
        def getHue(cls, color):
            return color.getLCh()[2]/360.0

        @classmethod
        def getShade(cls, color):
            l,c,h = color.getLCh()
            return h/360.0, c/100.0, l/100.0

        @classmethod
        def shade(cls, h, s, v):
            c = Color()
            c.setLCh((v*100, s*100, h*360.0))
            return c

        @classmethod
        def mix(cls, clr1, clr2, q):
            l1, c1, h1 = clr1.getLCh()
            l2, c2, h2 = clr2.getLCh()
            l = linear(l1, l2, q)
            c = linear(c1, c2, q)
            h = circular(h1, h2, q, 360)
            result = Color()
            result.setLCh((l, c, h))
            return result

    class MixerLChDesaturate(MixerLCh):
        @classmethod
        def mix(cls, clr1, clr2, q):
            l1, c1, h1 = clr1.getLCh()
            l2, c2, h2 = clr2.getLCh()
            
            l = linear(l1, l2, q)
            h1 = h1/360.0
            h2 = h2/360.0
            h, c = mix_wheel(h1,c1, h2,c2, q)
            h = h * 360.0

            return lch(l, c, h)
            
