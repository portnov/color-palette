#!/usr/bin/python

import sys
from PyQt4 import QtGui

from widgets.widgets import *
from color import colors, mixers, harmonies

def on_select(w):
    def handler():
        clr = w.selected_color
        print("Selected: " + str(clr))
    return handler


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    w = Selector(mixers.MixerLCh)
    w.setHarmony(harmonies.SimpleHarmony)
    w.selected.connect(on_select(w))
    w.show()
    sys.exit(app.exec_())

