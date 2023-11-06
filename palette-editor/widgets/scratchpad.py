
from math import cos, sin, pi, sqrt, atan2
from PyQt5 import QtGui, QtCore, QtWidgets

from color.colors import *
from .widgets import create_qdrag_color
from .commands.scratchpad import *
from models.models import Clipboard

class Scratchpad(QtWidgets.QWidget):
    def __init__(self, model, parent=None, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, *args, **kwargs)
        self.model = model
        self.undoStack = model.get_undo_stack()

        self.border_color = Color(0,0,0)
        self.drop_enabled = True

        self._prev_resize_pos = None
        self._resize_idx = None
        self._drag_start_pos = None
        self._drop_indicate_idx = None

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setMinimumSize(100, 50)

    def sizeHint(self):
        return QtCore.QSize(200, 50)

    def _get_colors(self):
        return self.model.colors

    def _set_colors(self, lst):
        self.model.colors = lst

    colors = property(_get_colors, _set_colors)

    def _calc(self, w):
        cs = [c for clr,c in self.colors]
        s = float(sum(cs))
        return [c*w/s for c in cs]

    def _avg(self):
        cs = [c for clr,c in self.colors]
        if not cs:
            return 1.0
        else:
            return sum(cs)/float(len(cs))

    def _idx_at_x(self, x):
        width = self.width()
        ws = self._calc(width)
        x0 = 0.0
        for i,w in enumerate(ws):
            if x < x0+w:
                return i
            x0 += w
        return None
    
    def _insert_idx_at_x(self, x):
        width = self.width()
        ws = self._calc(width)
        x0 = 0.0
        for i,w in enumerate(ws):
            if x < x0+w/2.0:
                return i
            x0 += w
        return len(self.colors)

    def _edge_at_x(self, x):
        width = self.width()
        ws = self._calc(width)
        x0 = 0.0
        delta = 5.0
        for i,w in enumerate(ws):
            x0 += w
            #print x0-delta, x, x0+delta
            if x0-delta < x < x0+delta:
                return i
        return None
    
    def _color_at_x(self, x):
        idx = self._idx_at_x(x)
        if idx is None:
            return None
        return self.colors[idx][0]

    def _add_color(self, color, x):
        idx = self._insert_idx_at_x(x)
        command = InsertColor(self, idx, color)
        self.undoStack.push(command)

    def _clear(self, x):
        if not self.colors:
            return
        idx = self._idx_at_x(x)
        self.colors.pop(idx)

    def _move(self, idx, delta_px):
        if not self.colors or idx is None:
            return
        #print("Move #{} for {}".format(idx, delta_px))
        #ws = self._calc(self.width())
        cs = [c for clr,c in self.colors]
        clrs = [clr for clr,c in self.colors]
        s = float(sum(cs))
        w = float(self.width())
        delta = delta_px * s/w
        clr0,c0 = self.colors[idx]
        clr1,c1 = self.colors[idx+1]
        self.colors[idx] = clr0, max(0.02, c0+delta)
        self.colors[idx+1] = clr1, max(0.02, c1-delta)

    def _mouse_pressed(self, event):
        return event.buttons() & self.model.options.select_button

    def add_color(self, color, repaint=True):
        command = AddColor(self, color, repaint)
        self.undoStack.push(command)

    def get_colors(self):
        return [clr for clr,c in self.colors]

    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            self._on_tooltip(event)
            return True
        else:
            return super(Scratchpad, self).event(event)

    def _on_tooltip(self, event):
        x = event.pos().x()
        color = self._color_at_x(x)
        if color is not None:
            QtWidgets.QToolTip.showText(event.globalPos(), color.verbose())

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        if event.button() == self.model.options.select_button:
            idx = self._edge_at_x(event.x())
            if idx is not None:
                self._prev_resize_pos = event.pos()
                self._resize_idx = idx
            else:
                self._drag_start_pos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        if event.button() == self.model.options.menu_button:
            menu = self._get_context_menu(event.x())
            menu.exec_(event.globalPos())
        elif event.button() == self.model.options.clear_button:
            self._clear(event.x())
            self.repaint()
        if self._mouse_pressed(event) and self._prev_resize_pos is not None:
            x = event.x()
            idx = self._resize_idx
            x0 = self._prev_resize_pos.x()
            self._move(idx, x-x0)
            self.repaint()

        self._prev_resize_pos = None
        self._resize_idx = None
        self._drag_start_pos = None
        event.accept()

    def on_clear(self, x):
        def wrapped():
            self._clear(x)
            self.repaint()
        return wrapped

    def _get_context_menu(self, x):

        def _get_color():
            return self._color_at_x(x)

        def _set_color(color):
            self._add_color(color, x)

        menu = QtWidgets.QMenu(self)
        clear = menu.addAction(_("Clear"))
        clear.triggered.connect(self.on_clear(x))

        self.clipboard = Clipboard(_get_color, _set_color)
        self.clipboard.add_cliboard_actions(menu, True)
        return menu

    def mouseMoveEvent(self, event):
        idx = self._edge_at_x(event.x())
        resizing = idx is not None or self._prev_resize_pos is not None
        if resizing:
            shape = QtCore.Qt.SizeHorCursor
        else:
            shape = QtCore.Qt.ArrowCursor
        self.setCursor(QtGui.QCursor(shape))

        if self._mouse_pressed(event) and self._prev_resize_pos is not None:
            x0 = self._prev_resize_pos.x()
            x = event.x()
            self._move(self._resize_idx, x-x0)
            self.repaint()

        if self._mouse_pressed(event) and resizing:
            self._prev_resize_pos = event.pos()
        else:
            self._prev_resize_pos = None

        if self._mouse_pressed(event) and not resizing:
            self._start_drag(event)

    def _start_drag(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return

        clr = self._color_at_x(event.x())
        drag = create_qdrag_color(self, clr)
        drag.exec_()

    def paintEvent(self, event):
        #print "painting scratchpad"
        qp = QtGui.QPainter()
        qp.begin(self)
        w, h = self.size().width(),  self.size().height()
        if not self.colors:
            qp.setPen(self.border_color)
            qp.drawRect(QtCore.QRectF(0, 0,  w,  h))
            qp.end()
            return
        ws = self._calc(w)
        x0 = 0
        y0 = 0
        for i, pair in enumerate(zip(self.colors, ws)):
            p,w = pair
            clr,c = p
            qp.setBrush(clr)
            qp.setPen(clr)
            qp.drawRect(QtCore.QRectF(x0,y0,w,h))
            if i == self._drop_indicate_idx:
                qp.setPen(Color(0,255,0))
                qp.drawLine(x0,y0,x0,h)
            x0 += w
        qp.end()

    def dragLeaveEvent(self, event):
        self._drop_indicate_idx = None
        self.repaint()

    def leaveEvent(self, event):
        self._drop_indicate_idx = None
        self.repaint()

    def dragMoveEvent(self, event):
        self._drop_indicate_idx = self._insert_idx_at_x(event.pos().x())
        self.repaint()
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasColor() and self.drop_enabled:
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasColor():
            qcolor = QtGui.QColor(event.mimeData().colorData())
            r,g,b,_ = qcolor.getRgb()
            color = Color(r,g,b)
            self._add_color(color, event.pos().x())
            self._drop_indicate_idx = None
            self.repaint()
    
