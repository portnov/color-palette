from copy import copy
from PyQt5 import QtGui, QtCore, QtWidgets

from color.colors import *

class SetMixer(QtWidgets.QUndoCommand):
    def __init__(self, owner, pairs, old_mixer_idx, new_mixer_idx):
        QtWidgets.QUndoCommand.__init__(self)
        self.owner = owner
        self.setText(_("selecting color model"))
        self.old_mixer_idx = old_mixer_idx
        self.mixer_idx = new_mixer_idx
        self.pairs = pairs

    def redo(self):
        _,  mixer = self.pairs[self.mixer_idx]
        print("Selected mixer: " + str(mixer))
        self.owner.setMixer(mixer, self.mixer_idx)

    def undo(self):
        print("setMixer.undo")
        _,  mixer = self.pairs[self.old_mixer_idx]
        self.owner.setMixer(mixer, self.old_mixer_idx)

class ChangeColor(QtWidgets.QUndoCommand):
    def __init__(self, model, text, fn):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText(text)
        self.fn = fn
        self.model = model

    def redo(self):
        self.old_color = self.model.getColor()
        color = self.fn(self.old_color)
        self.model.setColor(color)
        self.model.widget.repaint()

    def undo(self):
        print("change color.undo")
        self.model.setColor(self.old_color)
        self.model.widget.repaint()

class SetColor(QtWidgets.QUndoCommand):
    def __init__(self, model, color):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText(_("setting color"))
        self.model = model
        self.color = color

    def redo(self):
        self.old_color = self.model.getColor()
        self.model.color = self.color
        self.model.widget.repaint()
        self.old_history_colors = self.model.get_color_history().getColors()
        print("Push color to history: {}".format(self.color))
        self.model.get_color_history().push_new(self.color)
    
    def undo(self):
        print("undo")
        self.model.color = self.old_color
        print("Restore color: {}".format(self.old_color))
        self.model.widget.repaint()
        self.model.get_color_history().setColors(self.old_history_colors)

class Clear(QtWidgets.QUndoCommand):
    def __init__(self, model):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText(_("clearing color swatch"))
        self.model = model

    def redo(self):
        self.old_color = self.model.getColor()
        self.model.color = None
        self.model.widget.repaint()

    def undo(self):
        print("clear.undo")
        self.model.color = self.old_color
        self.model.widget.repaint()


