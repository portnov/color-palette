#!/usr/bin/python

import sys
from PyQt5 import QtGui, QtCore
import gettext

gettext.install("colors", localedir="share/locale", unicode=True)

from color.colors import *
from widgets.scratchpad import *
from widgets.widgets import *

class Test(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QVBoxLayout()
        clr = ColorWidget()
        scratchpad = Scratchpad(colors = [(red, 0.6), (green, 0.4)])
        layout.addWidget(clr,1)
        layout.addWidget(scratchpad, 2)
        self.setLayout(layout)

if __name__ == "__main__":
    green = Color(100,255,100)
    red = Color(255,100,100)

    app = QtWidgets.QApplication(sys.argv)
    w = Test()
    w.show()
    sys.exit(app.exec_())
