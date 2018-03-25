#!/usr/bin/python

import sys
from os.path import join, basename, dirname, abspath, exists
from PyQt5 import QtGui, QtCore
import gettext

gettext.install("colors", localedir="share/locale", unicode=True)

bindir = dirname(sys.argv[0])
rootdir = dirname(bindir)
sys.path.append(rootdir)

datarootdir = join( rootdir, "share" )
if not sys.platform.startswith('win'):
    datarootdir_installed = join( datarootdir, "palette-editor" )
    if exists(datarootdir_installed):
        datarootdir = datarootdir_installed
else:
    datarootdir_compiled = join( bindir, "share" )
    if exists(datarootdir_compiled):
        datarootdir = datarootdir_compiled

from color.mixers import *
from palette.palette import *
from palette.viewer import PaletteViewWindow
from palette.image import PaletteImage
from palette.widget import *
from widgets.widgets import *
from dialogs.open_palette import load_palette

def locate_icon(name):
    path = join(datarootdir, "icons", name)
    if not exists(path):
        print("Icon not found: " + path)
    return path
try:
    __builtins__.locate_icon = locate_icon
except AttributeError:
    __builtins__['locate_icon'] = locate_icon

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

app = QtWidgets.QApplication(sys.argv)
palette = load_palette(sys.argv[1])
gui = GUI(palette)
sys.exit(app.exec_())
