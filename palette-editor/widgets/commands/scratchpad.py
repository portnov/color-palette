from copy import copy
from PyQt4 import QtGui, QtCore

from color.colors import *

class ScratchpadCommand(QtGui.QUndoCommand):
    def __init__(self, scratchpad, text):
        QtGui.QUndoCommand.__init__(self)
        self.scratchpad = scratchpad
        self.setText(text)

    def remember_colors(self):
        self.old_colors = copy( self.scratchpad.colors )

    def restore_colors(self):
        self.scratchpad.colors = self.old_colors
        self.scratchpad.repaint()

    def undo(self):
        self.restore_colors()


class InsertColor(ScratchpadCommand):
    def __init__(self, scratchpad, idx, color):
        ScratchpadCommand.__init__(self, scratchpad, _("inserting color to scratchpad"))
        self.idx = idx
        self.color = color

    def redo(self):
        self.remember_colors()
        if not self.scratchpad.colors:
            self.scratchpad.colors = [(self.color, 1.0)]
            return
        avg = self.scratchpad._avg()
        self.scratchpad.colors.insert(self.idx, (self.color, avg))
        self.scratchpad.repaint()

class AddColor(ScratchpadCommand):
    def __init__(self, scratchpad, color, repaint=True):
        ScratchpadCommand.__init__(self, scratchpad, _("appending color to scratchpad"))
        self.color = color
        self.repaint = repaint

    def redo(self):
        self.remember_colors()
        if not self.scratchpad.colors:
            self.scratchpad.colors = [(self.color, 1.0)]
        else:
            avg = self.scratchpad._avg()
            self.scratchpad.colors.append((self.color, avg))
        if self.repaint:
            self.scratchpad.repaint()

