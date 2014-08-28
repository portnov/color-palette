#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore

from color.mixers import *
from palette.palette import *
from palette.viewer import PaletteViewWindow
from palette.image import PaletteImage
from palette.widget import *
from palette.storage.gimp import *
from widgets.widgets import *

class GUI(QtGui.QMainWindow):
    def __init__(self, palette):
        QtGui.QMainWindow.__init__(self)
        self.palette_widget = PaletteWidget(self, palette)
        self.palette_widget.editing_enabled = False
        self.palette_widget.selected.connect(self.on_select)
        self.setCentralWidget(self.palette_widget)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.show()

    def sizeHint(self):
        r,c = self.palette_widget.palette.nrows, self.palette_widget.palette.ncols
        return QtCore.QSize(c*20, r*20)

    def on_select(self, row, col):
        color = self.palette_widget.palette.getColor(row,col)
        print("Selected ({},{}): {}".format(row,col, color))

app = QtGui.QApplication(sys.argv)
palette = GimpPalette().load(MixerRGB, sys.argv[1])
gui = GUI(palette)
sys.exit(app.exec_())
