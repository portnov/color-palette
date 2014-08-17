from PyQt4 import QtGui

from palette import *
from colors import *
from widgets import *
from mixers import *

class PaletteViewWindow(QtGui.QWidget):
    def __init__(self, palette):
        QtGui.QWidget.__init__(self)
        self.palette = palette
        self.init_gui()
    
    def init_gui(self):
        grid = QtGui.QGridLayout(self)
        for i,row in enumerate(self.palette.getColors()):
            for j, color in enumerate(row):
                w = ColorWidget(self)
                w.setColor(color)
                grid.addWidget(w, i, j)
        self.setLayout(grid)
        self.show()
