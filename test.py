#!/usr/bin/python

import sys
from PyQt4 import QtGui

from widgets.widgets import *
from widgets.wheel import *
from color import colors, mixers, harmonies

def click(w):
    def handler(hue, chroma, luma):
        print("H: {:.2f}, C: {:.2f}, Y: {:.2f}".format(hue, chroma, luma))
    return handler

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    w = HCYSelector()
    w.selected.connect(click(w))
    w.show()
    sys.exit(app.exec_())

