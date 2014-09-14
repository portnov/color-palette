
from PyQt4 import QtGui, QtCore

from color import colors
from widgets.commands import *

class Document(object):
    def __init__(self, window):
        self.window = window
        self.undoStack = QtGui.QUndoStack(window)

        self.current_color = ColorModel(self)

        self.scratchpad = ScratchpadModel(self)

        self.swatches = [[ColorModel(self) for i in range(5)] for j in range(5)]

        self.svg_colors = [[ColorModel(self) for i in range(7)] for j in range(3)]

    def get_undo_stack(self):
        return self.undoStack

class ScratchpadModel(object):
    def __init__(self, parent):
        self.parent = parent
        self.colors = []

    def get_undo_stack(self):
        return self.parent.get_undo_stack()

class ColorModel(object):
    def __init__(self, parent, color=None):
        self.parent = parent
        self.color = color
        self.set_color_enabled = True

    def to_set_color(self):
        return self.set_color_enabled

    def get_undo_stack(self):
        return self.parent.get_undo_stack()

    def get_tooltip(self):
        if self.color is None:
            return None
        return self.color.verbose()

    def getColor(self):
        return self.color

    def setColor(self, color):
        command = SetColor(self, color)
        self.command(command)

    def clear(self):
        command = Clear(self)
        self.command(command)

    def command(self, cmd):
        self.get_undo_stack().push(cmd)
    
    def rotate_color(self, x):
        command = ChangeColor(self, _("rotating color"),
                                lambda c : colors.increment_hue(c, x))
        self.command(command)

    def lighter(self, x):
        command = ChangeColor(self, _("changing color lightness"),
                                 lambda c : colors.lighter(c, x))
        self.command(command)

    def saturate(self, x):
        command = ChangeColor(self, _("changing color saturation"),
                                 lambda c : colors.saturate(c, x))
        self.command(command)



