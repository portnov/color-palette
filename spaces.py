
from colors import *

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

