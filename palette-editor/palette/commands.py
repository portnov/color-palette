
from copy import copy
from PyQt5 import QtGui, QtCore, QtWidgets

from .palette import *
from color.colors import *

class MarkCommand(QtWidgets.QUndoCommand):
    def __init__(self, widget, row, column, mark=None):
        QtWidgets.QUndoCommand.__init__(self)
        self.widget = widget
        self.palette = widget.palette
        self.row = row
        self.column = column
        self.mark = mark
        self.setText(_("toggling mark on palette slot"))

    def redo(self):
        self.palette.mark_color(self.row, self.column, self.mark)
        self.widget.repaint()

    def undo(self):
        self.palette.mark_color(self.row, self.column, self.mark)
        self.widget.repaint()

class SetColor(QtWidgets.QUndoCommand):
    def __init__(self, widget, row, column, color):
        QtWidgets.QUndoCommand.__init__(self)
        self.widget = widget
        self.palette = widget.palette
        self.row = row
        self.column = column
        self.color = color
        self.setText(_("changing color in palette slot"))

    def redo(self):
        slot = self.palette.slots[self.row][self.column]
        if slot.mode == USER_DEFINED:
            self.old_color = slot.getColor()
        else:
            self.old_color = None
        self.palette.paint(self.row, self.column, self.color)
        self.palette.recalc()
        self.widget.repaint()
        #self.old_history_colors = self.model.get_color_history().getColors()
        #self.model.get_color_history().push_new(self.color)

    def undo(self):
        if self.old_color is None:
            self.palette.mark_color(self.row, self.column, False)
        else:
            self.palette.paint(self.row, self.column, self.old_color)
        self.palette.recalc()
        self.widget.repaint()
        #self.model.get_color_history().setColors(self.old_history_colors)

INSERT=0
DELETE=1
ROW=0
COLUMN=1

class EditLayout(QtWidgets.QUndoCommand):
    def __init__(self, widget, action, kind, idx):
        QtWidgets.QUndoCommand.__init__(self)
        self.widget = widget
        self.palette = widget.palette
        self.action = action
        self.kind = kind
        self.idx = idx
        self.colors = []
        self.setText(self.actionText())

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
        self.widget.recalc_size()
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
        self.widget.recalc_size()
        self.widget.repaint()

    def actionText(self):
        if self.kind == ROW and self.action == DELETE:
            return _("deleting palette row")
        elif self.kind == ROW and self.action == INSERT:
            return _("inserting row into palette")
        elif self.kind == COLUMN and self.action == DELETE:
            return _("deleting palette column")
        else:
            return _("inserting column into palette")

class ChangeColors(QtWidgets.QUndoCommand):
    def __init__(self, widget, palette, text, fn):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText(text)
        self.widget = widget
        self.palette = palette
        self.fn = fn
        self.colors = []

    def remember_colors(self):
        for row, col, slot in self.palette.getUserDefinedSlots():
            self.colors.append((row, col, slot.getColor()))

    def redo(self):
        self.remember_colors()
        for row, col, slot in self.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = self.fn(clr)
            slot.setColor(clr)
        self.palette.recalc()
        self.widget.update()

    def undo(self):
        for row, col, clr in self.colors:
            self.palette.paint(row, col, clr)
        self.palette.recalc()
        self.widget.update()

class SwatchesToPalette(QtWidgets.QUndoCommand):
    def __init__(self, palette_widget, mixer, swatches):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText(_("creating palette from color swatches"))
        self.palette_widget = palette_widget
        self.mixer = mixer
        self.swatches = swatches

    def redo(self):
        self.old_palette = copy( self.palette_widget.palette )
        palette = Palette(self.mixer, nrows=len(self.swatches), ncols=len(self.swatches[0]))
        for i,row in enumerate(self.swatches):
            for j,w in enumerate(row):
                clr = w.getColor()
                if clr is None:
                    palette.slots[i][j].mark(False)
                else:
                    palette.slots[i][j].color = clr
                    palette.slots[i][j].mark(True)
        self.palette_widget.palette = palette
        self.palette_widget.selected_slot = None
        self.palette_widget.redraw()
        self.palette_widget.update()

    def undo(self):
        self.palette_widget.palette = self.old_palette
        self.palette_widget.selected_slot = None
        self.palette_widget.redraw()
        self.palette_widget.update()

class SortBy(QtWidgets.QUndoCommand):
    def __init__(self, widget, palette, text, key):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText(text)
        self.widget = widget
        self.palette = palette
        self.key = key
        self.colors = []

    def remember_colors(self):
        for row, col, slot in self.palette.getUserDefinedSlots():
            self.colors.append((row, col, slot.getColor()))

    def redo(self):
        self.remember_colors()
        src_colors = [r[2].getColor() for r in self.palette.getUserDefinedSlots()]
        new_colors = sorted(src_colors, key=self.key)
        for idx, (row, col, slot) in enumerate(self.palette.getUserDefinedSlots()):
            new_clr = new_colors[idx]
            slot.setColor(new_clr)
        self.palette.recalc()
        self.widget.update()

    def undo(self):
        for row, col, clr in self.colors:
            self.palette.paint(row, col, clr)
        self.palette.recalc()
        self.widget.update()

