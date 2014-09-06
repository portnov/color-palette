
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

class HSV(Space):
    @classmethod
    def getCoords(cls, color):
        return color.getHSV()

    @classmethod
    def fromCoords(cls, coords):
        return hsv(*coords)

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


class LCh(Space):
    @classmethod
    def getCoords(cls, color):
        l,c,h = color.getLCh()
        return (h/360.0, c/100.0, l/100.0)

    @classmethod
    def fromCoords(cls, coords):
        h,c,l = coords
        return lch(l*100.0, c*100.0, h*360.0)

