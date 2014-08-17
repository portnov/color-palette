#!/usr/bin/python

import sys
from PyQt4 import QtGui
from colors import *
from palette import *
from mixers import *
from viewer import PaletteViewWindow

palette = Palette(MixerRGB, 5, 5)
palette.paint(0, 0, Color(255.0, 0.0, 0.0))
palette.paint(0, 4, Color(0.0, 0.0, 0.0))
palette.paint(4, 0, Color(255.0, 255.0, 255.0))
palette.paint(4, 4, Color(0.0, 255.0, 0.0))
palette.recalc()
# palette.recalc()
# palette.recalc()

storage = GimpPalette(palette)

storage.save("test.gpl")

app = QtGui.QApplication(sys.argv)
w = PaletteViewWindow(palette)
sys.exit(app.exec_())

