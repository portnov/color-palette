from PyQt4 import QtGui, QtCore

from color.colors import *

class SwatchesCommand(QtGui.QUndoCommand):
    def __init__(self, owner):
        QtGui.QUndoCommand.__init__(self)
        self.owner = owner
        self.colors = []

    def remember_swatches(self):
        self.colors = [[w.getColor() for w in row] for row in self.owner.swatches]

    def undo(self):
        for oldrow, row in zip(self.colors, self.owner.swatches):
            for clr, w in zip(oldrow, row):
                w.setColor(clr)
                w.update()

class ClearSwatches(SwatchesCommand):
    def __init__(self, owner):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("clearing color swatches"))

    def redo(self):
        self.remember_swatches()
        for row in self.owner.swatches:
            for w in row:
                w.setColor(None)
                w.update()

class ChangeSwatchesColors(SwatchesCommand):
    def __init__(self, owner, text, fn):
        SwatchesCommand.__init__(self, owner)
        self.setText(text)
        self.fn = fn

    def _map_swatches(self, fn):
        for row in self.owner.swatches:
            for w in row:
                clr = w.getColor()
                if clr is None:
                    continue
                clr = fn(clr)
                w.setColor(clr)
        self.owner.update()

    def redo(self):
        self.remember_swatches()
        self._map_swatches(self.fn)

