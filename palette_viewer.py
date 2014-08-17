#!/usr/bin/python

import sys
from PyQt4 import QtGui

from palette import *
from mixers import *
from viewer import PaletteViewWindow

app = QtGui.QApplication(sys.argv)
palette = GimpPalette().load(MixerRGB, sys.argv[1])
w = PaletteViewWindow(palette)
sys.exit(app.exec_())
