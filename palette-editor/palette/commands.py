
from PyQt4 import QtGui, QtCore

from palette import *
from color.colors import *

class MarkCommand(QtGui.QUndoCommand):
    def __init__(self, widget, row, column, mark=None):
        QtGui.QUndoCommand.__init__(self)
        self.widget = widget
        self.palette = widget.palette
        self.row = row
        self.column = column
        self.mark = mark

    def redo(self):
        self.palette.mark_color(self.row, self.column, self.mark)
        self.widget.repaint()

    def undo(self):
        self.palette.mark_color(self.row, self.column, self.mark)
        self.widget.repaint()

class SetColor(QtGui.QUndoCommand):
    def __init__(self, widget, row, column, color):
        QtGui.QUndoCommand.__init__(self)
        self.widget = widget
        self.palette = widget.palette
        self.row = row
        self.column = column
        self.color = color

    def redo(self):
        slot = self.palette.slots[self.row][self.column]
        if slot.mode == USER_DEFINED:
            self.old_color = slot.getColor()
        else:
            self.old_color = None
        self.palette.paint(self.row, self.column, self.color)
        self.palette.recalc()
        self.widget.repaint()

    def undo(self):
        if self.old_color is None:
            self.palette.mark_color(self.row, self.column, False)
        else:
            self.palette.paint(self.row, self.column, self.old_color)
        self.palette.recalc()
        self.widget.repaint()

INSERT=0
DELETE=1
ROW=0
COLUMN=1

class EditLayout(QtGui.QUndoCommand):
    def __init__(self, widget, action, kind, idx):
        QtGui.QUndoCommand.__init__(self)
        self.widget = widget
        self.palette = widget.palette
        self.action = action
        self.kind = kind
        self.idx = idx
        self.colors = []

    def remember_row(self, idx):
        for i in range(self.palette.ncols):
            slot = self.palette.slots[idx][i]
            if slot.mode == USER_DEFINED:
                self.colors.append((idx,i, slot.getColor()))

    def remember_column(self, idx):
        for i in range(self.palette.nrows):
            slot = self.palette.slots[i][idx]
            if slot.mode == USER_DEFINED:
                self.colors.append((i, idx, slot.getColor()))

    def redo(self):
        if self.kind == ROW and self.action == DELETE:
            self.remember_row(self.idx)
            self.palette.del_row(self.idx)
        elif self.kind == ROW and self.action == INSERT:
            self.palette.add_row(self.idx)
        elif self.kind == COLUMN and self.action == DELETE:
            self.remember_column(self.idx)
            self.palette.del_column(self.idx)
        else:
            self.palette.add_column(self.idx)
        self.widget.repaint()

    def undo(self):
        if self.kind == ROW and self.action == DELETE:
            self.palette.add_row(self.idx)
        elif self.kind == ROW and self.action == INSERT:
            self.palette.del_row(self.idx)
        elif self.kind == COLUMN and self.action == DELETE:
            self.palette.add_column(self.idx)
        else:
            self.palette.del_column(self.idx)
        for r,c,clr in self.colors:
            self.palette.paint(r, c, clr)
        self.palette.recalc()
        self.widget.repaint()

