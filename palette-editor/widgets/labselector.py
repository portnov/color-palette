
from math import cos, sin, pi, sqrt, atan2
from PyQt4 import QtGui, QtCore

from color.colors import *
from widgets import *

class Square(CacheImage):
    def __init__(self, mixer=None, w=0, h=0):
        self.lightness = 50.0
        CacheImage.__init__(self, mixer, w,h)

    def calc(self):
        self.colors = []
        STEP=4.0
        for a in seq(-127.0, 127.0, STEP):
            lst = []
            for b in seq(-127.0, 127.0, STEP):
                color = lab(self.lightness, a, b)
                lst.append(color)
            self.colors.append(lst)

    def draw(self, w, h):
        assert w is not None
        assert h is not None
        assert w > 0
        assert h > 0
        self.image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        assert not self.image.isNull()
        self.image.fill(0)
        qp = QtGui.QPainter()
        qp.begin(self.image)
        xstep = w / float(len(self.colors[0]))
        ystep = h / float(len(self.colors))
        for i, row in enumerate(self.colors):
            for j, clr in enumerate(row):
                qp.setPen(clr)
                qp.setBrush(clr)
                qp.drawRect(j*xstep, i*ystep, xstep, ystep)
        qp.end()

class Slider(CacheImage):
    def __init__(self, mixer=None, w=0, h=0):
        self.a = 0.0
        self.b = 0.0
        CacheImage.__init__(self, mixer, w,h)

    N = 50

    def calc(self):
        self.colors = []
        for i in range(self.N):
            self.colors.append(lab(100*(1 - i/float(self.N)), self.a, self.b))

    def draw(self, w, h):
        w = min(w, 30)
        self.image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        self.image.fill(0)
        qp = QtGui.QPainter()
        qp.begin(self.image)
        rw = w
        rh = h / float(self.N)
        for i,color in enumerate(self.colors):
            x = 0
            y = i * rh
            qp.setBrush(color)
            qp.setPen(color)
            qp.drawRect(x,y, rw, rh)
        qp.end()

class SquareWidget(QtGui.QWidget):
    clicked = QtCore.pyqtSignal(float,float)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.cache = Square()
        self._mouse_pressed = False
        self._selected = None
        self.l = 0
        self.a = 0
        self.b = 0

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self._mouse_pressed = True
        event.accept()

    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        self._mouse_pressed = False
        x,y = event.x(), event.y()
        self._select(x,y)
        event.accept()

    def mouseMoveEvent(self, event):
        x,y = event.x(), event.y()
        if self._mouse_pressed:
            self._select(x,y)

    def _xy_to_ab(self, x, y):
        w, h = self.size().width(),  self.size().height()
        b = (x/float(w))*256 - 127
        a = (y/float(h))*256 - 127
        return (a,b)

    def _ab_to_xy(self, a, b):
        w, h = self.size().width(),  self.size().height()
        x = w * (b+127)/256.0
        y = h * (a+127)/256.0
        return (x,y)
    
    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        image = self.cache.get(w, h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)

        if self._selected is not None:
            x,y = self._ab_to_xy( * self._selected )
            qp.setBrush(QtGui.QColor(255,255,255, 127))
            qp.setPen(Color(0,0,0))
            qp.drawEllipse(x-4, y-4, 8, 8)

        qp.end()

    def _select(self, x, y):
        w, h = self.width(), self.height()
        a, b = self._xy_to_ab(x,y)
        self._selected = a,b
        self.repaint()
        self.a = a
        self.b = b
        self.clicked.emit(a, b)

    def set_l(self, l):
        self.l = l
        self.cache.lightness = l
        self.cache.redraw(self.width(), self.height())

    def get_color(self):
        return lab(self.l, self.a, self.b)


class SliderWidget(QtGui.QWidget):

    clicked = QtCore.pyqtSignal(float)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.cache = Slider()
        self._mouse_pressed = False
        self.l = 0.0

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self._mouse_pressed = True
        event.accept()

    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        self._mouse_pressed = False
        x,y = event.x(), event.y()
        self._select(y)
        event.accept()

    def mouseMoveEvent(self, event):
        x,y = event.x(), event.y()
        if self._mouse_pressed:
            self._select(y)

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        image = self.cache.get(w, h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)
        if self.l is not None:
            y0 = (100.0 - self.l) * h / 100.0
            qp.setPen(Color(0,0,0))
            w = min(w, 35)
            qp.drawRect(0,y0-2, w, 4)
        qp.end()

    def _select(self, y):
        w, h = self.width(), self.height()
        self.l = 100.0 * float(h-y)/float(h)
        #print("Slider._select({})".format(self.luma))
        self.repaint()
        self.clicked.emit(self.l)

    def select(self, l):
        self.l = l
        #print("Slider.select({})".format(self.luma))
    
    def get_l(self):
        return self.l

class LabSelector(QtGui.QWidget):
    selected = QtCore.pyqtSignal(Color, Color)

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.box = QtGui.QHBoxLayout()
        self.square = SquareWidget()
        self.slider = SliderWidget()
        self.box.addWidget(self.slider, 1)
        self.box.addWidget(self.square, 5)
        self.setLayout(self.box)
        self.square.clicked.connect(self._on_click_square)
        self.slider.clicked.connect(self._on_click_slider)
        self._prev_color = lab(0,0,0)

    def _on_click_square(self, a, b):
        self.slider.cache.a = a
        self.slider.cache.b = b
        self.slider.cache.redraw(self.slider.width(), self.slider.height())
        self.update()
        color = lab(self.slider.l, a, b)
        self.selected.emit(self._prev_color, color)
        self._prev_color = color

    def _on_click_slider(self, l):
        self.square.set_l(l)
        self.update()
        color = lab(l, self.square.a, self.square.b)
        self.selected.emit(self._prev_color, color)
        self._prev_color = color
    
    def setColor(self, color, no_signal=False):
        if color is None:
            return
        l,a,b = color.getLab()
        self.slider.cache.a = a
        self.slider.cache.b = b
        self.slider.cache.redraw(self.slider.width(), self.slider.height())
        self.slider.select(l)
        self.square.set_l(l)
        self.square.select(a,b)
        self.update()
        if not no_signal:
            self.selected.emit(self._prev_color, color)
            self._prev_color = color

    def getColor(self):
        return self.square.get_color()

