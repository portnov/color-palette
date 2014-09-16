
from color.colors import *

class Space(object):
    @classmethod
    def getCoords(cls, color):
        pass

    @classmethod
    def fromCoords(cls, coords):
        pass

class RGB(Space):
    @classmethod
    def getCoords(cls, color):
        return color.getRGB()

    @classmethod
    def fromCoords(cls, coords):
        return Color(*coords)

class RGB1(Space):
    @classmethod
    def getCoords(cls, color):
        return color.getRGB1()

    @classmethod
    def fromCoords(cls, coords):
        result = Color()
        result.setRGB1(coords)
        return result

class HSV(Space):
    @classmethod
    def getCoords(cls, color):
        return color.getHSV()

    @classmethod
    def fromCoords(cls, coords):
        return hsv(*coords)

class HLS(Space):
    @classmethod
    def getCoords(cls, color):
        return color.getHLS()

    @classmethod
    def fromCoords(cls, coords):
        return hls(*coords)

class HCY(Space):
    @classmethod
    def getCoords(cls, color):
        return color.getHCY()

    @classmethod
    def fromCoords(cls, coords):
        return hcy(*coords)

class RYB(Space):
    @classmethod
    def getCoords(cls, color):
        return color.getRYB()

    @classmethod
    def fromCoords(cls, coords):
        return ryb(*coords)

class CMY(Space):
    @classmethod
    def getCoords(cls, color):
        c,m,y = color.getCMY()
        return (c,m,y)
    
    @classmethod
    def fromCoords(cls, coords):
        c,m,y = coords
        color = Color()
        color.setCMY((c,m,y))
        return color

class LCh(Space):
    @classmethod
    def getCoords(cls, color):
        l,c,h = color.getLCh()
        return (h/360.0, c/100.0, l/100.0)

    @classmethod
    def fromCoords(cls, coords):
        h,c,l = coords
        return lch(l*100.0, c*100.0, h*360.0)

class Lab(Space):
    @classmethod
    def getCoords(cls, color):
        l,a,b = color.getLab()
        return (l,a,b)

    @classmethod
    def fromCoords(cls, coords):
        l,a,b = coords
        return lab(l,a,b)

