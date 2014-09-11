
from math import cos, sin, pi, sqrt, atan2
from PyQt4 import QtGui, QtCore

from color.colors import *
from widgets import create_qdrag_color

class Scratchpad(QtGui.QWidget):
    def __init__(self, colors=None, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        if colors is None:
            self.colors = []
        else:
            self.colors = colors
        self.border_color = Color(0,0,0)
        self.drop_enabled = True
        self.clear_button = QtCore.Qt.RightButton
        self.drag_button = QtCore.Qt.LeftButton

        self._prev_resize_pos = None
        self._resize_idx = None
        self._drag_start_pos = None
        self._drop_indicate_idx = None

        self.setAcceptDrops(True)
        self.setMouseTracking(True)

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
        return self.colors[idx][0]

    def _add_color(self, color, x):
        if not self.colors:
            self.colors = [(color, 1.0)]
            return
        avg = self._avg()
        idx = self._insert_idx_at_x(x)
        self.colors.insert(idx, (color, avg))

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
        return event.buttons() & self.drag_button

    def add_color(self, color, repaint=True):
        if not self.colors:
            self.colors = [(color, 1.0)]
        else:
            avg = self._avg()
            self.colors.append((color, avg))
        if repaint:
            self.repaint()

    def get_colors(self):
        return [clr for clr,c in self.colors]

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        if event.button() == self.drag_button:
            idx = self._edge_at_x(event.x())
            if idx is not None:
                self._prev_resize_pos = event.pos()
                self._resize_idx = idx
            else:
                self._drag_start_pos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        if event.button() == self.clear_button:
            x = event.x()
            self._clear(x)
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
        if (event.pos() - self._drag_start_pos).manhattanLength() < QtGui.QApplication.startDragDistance():
            return

        clr = self._color_at_x(event.x())
        drag = create_qdrag_color(self, clr)
        drag.exec_()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        w, h = self.size().width(),  self.size().height()
        if not self.colors:
            qp.setPen(self.border_color)
            qp.drawRect(0, 0,  w,  h)
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
            qp.drawRect(x0,y0,w,h)
            if i == self._drop_indicate_idx:
                qp.setPen(Color(0,255,0))
                qp.drawLine(x0,y0,x0,h)
            x0 += w
        qp.end()

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
    
