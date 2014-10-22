
from PyQt4 import QtGui, QtCore

from palette import *
from color.colors import *

class PaletteImage(object):
    def __init__(self, palette, w=None, h=None, padding=2.0, background=None, indicate_modes=False):
        self.palette = palette
        self.w = w
        self.h = h
        self.image = None
        self.padding = padding
        if background is None:
            self.background = Color(127,127,127)
        else:
            self.background = background
        self.indicate_modes = indicate_modes

    def invalidate(self):
        self.image = None

    def get(self, w, h):
        if w == self.w and h == self.h and self.image is not None:
            return self.image
        else:
            self.image = self.draw(w, h)
            return self.image

    def draw(self, w, h):
        if w is None or h is None:
            return None
        image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        image.fill(self.background)
        slot_w = float(w)/float(self.palette.ncols)
        slot_h = float(h)/float(self.palette.nrows)
        rw = slot_w - self.padding
        rh = slot_h - self.padding
        qp = QtGui.QPainter()
        qp.begin(image)
        for i in range(self.palette.nrows):
            for j in range(self.palette.ncols):
                x = slot_w * j + self.padding/2.0
                y = slot_h * i + self.padding/2.0
                color = self.palette.getColor(i,j)
                qp.setPen(self.background)
                qp.setBrush(color)
                qp.drawRect(x,y, rw, rh)
                if self.indicate_modes:
                    slot = self.palette.slots[i][j]
                    qp.setPen(Color(0,0,0))
                    if slot.mode == HORIZONTALLY_GENERATED:
                        qp.drawLine(x+2, y+slot_h/2.0, x+slot_w-2, y+slot_h/2.0)
                    elif slot.mode == VERTICALLY_GENERATED:
                        qp.drawLine(x+slot_w/2.0, y+2, x+slot_w/2.0, y+slot_h-2)
        qp.end()
        return image
