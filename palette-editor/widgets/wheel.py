
from math import cos, sin, pi, sqrt, atan2
from PyQt4 import QtGui, QtCore

from color.colors import *
from widgets import *

class Wheel(CacheImage):
    def __init__(self, mixer=None, w=0, h=0):
        self.luma = 0.5
        CacheImage.__init__(self, mixer, w, h)

    def calc(self):
        self.colors = []
        for chroma in seq(0, 1, 0.05):
            steps = max( 100 * 2*pi*chroma / 5.0,  6)
            lst = []
            for hue in seq(0, 1, 1.0/steps):
                color = hcy(hue, chroma, self.luma)
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
        x0, y0 = w/2.0, h/2.0
        Rmax = min(w,h)/2.0
        step_chroma = 1.0 / float(len(self.colors))
        step_r = Rmax * step_chroma

        color = hcy(0,0,self.luma)
        qp.setBrush(color)
        qp.setPen(color)
        qp.drawEllipse(x0-step_r, y0-step_r, step_r*2 + 1, step_r*2 + 1)

        for i, ring in enumerate(self.colors[1:]):
            if i == 0:
                continue
            step_hue = 1.0/ float(len(ring))
            step_alpha = 360.0 * step_hue 
            r = i*step_r
            R = (i+1)*step_r
            iw = ih = 2*r
            ow = oh = 2*R
            ox = (w-ow)/2.0
            oy = (h-oh)/2.0
            ix = (w-iw)/2.0
            iy = (h-ih)/2.0
            outrect = QtCore.QRectF(ox, oy, ow, oh)
            inrect = QtCore.QRectF(ix,iy, iw,ih)
            for j, color in enumerate(ring):
                a = 2*pi*j*step_hue
                b = 2*pi*(j+1)*step_hue
                alpha = j*step_alpha
                xA, yA = x0 + R*cos(a), y0 - R*sin(a)
                xB, yB = x0 + r*cos(b), y0 - r*sin(b)
                path = QtGui.QPainterPath()
                path.moveTo(xA, yA)
                path.arcTo(outrect, alpha, step_alpha)
                path.arcTo(inrect, (alpha+step_alpha), - step_alpha)
                #print("A: {}, {}".format(xA,yA))
                #path.lineTo(xA, yA)
                #path.closeSubpath()
                qp.setPen(color)
                qp.drawPath(path)
                qp.fillPath(path, color)
        qp.end()

class Slider(CacheImage):
    def __init__(self, mixer=None, w=0, h=0):
        self.hue = 0
        CacheImage.__init__(self, mixer, w, h)

    N = 50

    def calc(self):
        self.colors = []
        for i in range(self.N):
            self.colors.append(hcy(self.hue, 1.0, 1.0 - i/float(self.N)))

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

class WheelWidget(QtGui.QWidget):

    clicked = QtCore.pyqtSignal(float, float)
    edited = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.cache = Wheel()
        self.mouse_pressed = False
        self._selected = None
        self.hue = 0
        self.chroma = 0
        self.luma = 0
        self._harmonized = None
        self._harmony = None
        self._harmony_parameter = 0.5
        self._dragged = None
        self.enable_editing = False

    def _get_nearest(self, x,y):
        if not self.enable_editing:
            return None
        if not self._harmonized:
            return None
        rho_min = None
        result = None
        for idx, pair in enumerate(self._harmonized):
            hue, chroma = pair
            x1,y1 = self._hc_to_xy(hue, chroma)
            rho2 = (x-x1)**2 + (y-y1)**2
            if rho2 < 25:
                if rho_min is None or rho2 < rho_min:
                    rho_min = rho2
                    result = idx
        print("Nearest to ({}, {}): #{}".format(x,y,result))
        return result

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self.mouse_pressed = True
        if self._harmony is None:
            self._dragged = self._get_nearest(event.x(), event.y())
        event.accept()

    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        self.mouse_pressed = False
        x,y = event.x(), event.y()
        if self._dragged is None:
            self._select(x,y)
        self._dragged = None
        event.accept()

    def mouseMoveEvent(self, event):
        x,y = event.x(), event.y()
        if self.mouse_pressed:
            if self._dragged is None:
                self._select(x,y)
            else:
                self._drag(x,y)

    def wheelEvent(self, event):
        steps = event.delta()/120.0
        apply_to_harmonized = self.enable_editing and self._harmonized

        if event.modifiers() & QtCore.Qt.ControlModifier:
            fn = lambda h,c : ((h+0.01*steps)%1, c)
        else:
            fn = lambda h,c : (h, clip(c+0.1*steps))

        if apply_to_harmonized:
            self._harmonized = [fn(h,c) for h,c in self._harmonized]

        if self._selected:
            h,c = self._xy_to_hc(*self._selected)
            h1,c1 = fn(h,c)
            self._selected = self._hc_to_xy(h1,c1)
            self.hue = h1
            self.chroma = c1
            self.clicked.emit(h1,c1)

        self.repaint()
        if apply_to_harmonized:
            self.edited.emit()

    def _xy_to_hc(self, x,y):
        w, h = self.size().width(),  self.size().height()
        x0, y0 = w/2.0, h/2.0
        R = min(x0,y0)
        dx, dy = x-x0, y-y0
        chroma = sqrt(dx**2 + dy**2)/R
        if chroma > 1.0:
            return None
        hue = atan2(-dy, dx)/(2*pi)
        return (hue, chroma)

    def _hc_to_xy(self, hue, chroma):
        w, h = self.size().width(),  self.size().height()
        x0, y0 = w/2.0, h/2.0
        R = min(x0,y0)
        x = x0 + chroma*R*cos(hue*2*pi)
        y = y0 - chroma*R*sin(hue*2*pi)
        return (x,y)

    def _apply_hc(self, fn, xy):
        h,c = self._xy_to_hc(*xy)
        h1,c1 = fn(h,c)
        return self._hc_to_xy(h1,c1)

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        image = self.cache.get(w, h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)

        if self._selected is not None:
            x,y = self._selected
            qp.setBrush(QtGui.QColor(255,255,255, 127))
            qp.setPen(Color(0,0,0))
            qp.drawEllipse(x-4, y-4, 8, 8)

        if self._harmonized is not None:
            for idx, pair in enumerate(self._harmonized):
                hue, chroma = pair
                x,y = self._hc_to_xy(hue, chroma)
                if self._dragged == idx:
                    qp.setBrush(Color(255,255,255))
                else:
                    qp.setBrush(QtGui.QColor(0,0,0,0))
                qp.setPen(Color(0,0,0))
                qp.drawRect(x-3, y-3, 6, 6)

        qp.end()

    def _drag(self, x,y):
        s = self._xy_to_hc(x,y)
        if s is None:
            return

        hue,chroma = s
        self._harmonized[self._dragged] = (hue, chroma)
        self.repaint()
        self.edited.emit()

    def _select(self, x, y):
        w, h = self.width(), self.height()
        x0, y0 = w/2.0, h/2.0
        dx, dy = x-x0, y-y0
        R = min(x0,y0)
        chroma = sqrt(dx**2 + dy**2)/R
        if chroma > 1.0:
            return
        hue = atan2(-dy, dx)/(2*pi)
        self._selected = x,y
        self.repaint()
        self.hue = hue
        self.chroma = chroma

        if self._harmony is not None:
            self._calc_harmony(self.get_color())

        self.clicked.emit(hue, chroma)

    def select(self, hue, chroma):
        x,y = self._hc_to_xy(hue, chroma)
        self._selected = x,y
        self._calc_harmony(hcy(hue, chroma, self.luma))
        #self.repaint()

    def get_color(self):
        return hcy(self.hue, self.chroma, self.luma)

    def set_luma(self, luma):
        self.luma = luma
        self.cache.luma = luma
        self.cache.redraw(self.width(), self.height())

    def _calc_harmony(self, current):
        if self._harmony is None:
            return
        #print("Calc harmony from {}".format(str(current)))
        colors = self._harmony.get(current, self._harmony_parameter)
        self._harmonized = []
        for clr in colors:
            h,c,y = clr.getHCY()
            self._harmonized.append((h,c))

    def set_harmony(self, harmony, current):
        self._harmony = harmony
        self._calc_harmony(current)
        self.repaint()

    def set_harmony_parameter(self, value, current):
        self._harmony_parameter = value
        self._calc_harmony(current)
        self.repaint()

class SliderWidget(QtGui.QWidget):

    clicked = QtCore.pyqtSignal(float)

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.cache = Slider()
        self.mouse_pressed = False
        self.luma = 0.5

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self.mouse_pressed = True
        event.accept()

    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        self.mouse_pressed = False
        x,y = event.x(), event.y()
        self._select(y)
        event.accept()

    def mouseMoveEvent(self, event):
        x,y = event.x(), event.y()
        if self.mouse_pressed:
            self._select(y)

    def wheelEvent(self, event):
        steps = event.delta()/120.0
        if self.luma is not None:
            self.luma = clip(self.luma + 0.05*steps)
            self.repaint()
            self.clicked.emit(self.luma)

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        image = self.cache.get(w, h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)
        if self.luma is not None:
            y0 = (1.0 - self.luma) * h
            qp.setPen(Color(0,0,0))
            w = min(w, 35)
            qp.drawRect(0,y0-2, w, 4)
        qp.end()

    def _select(self, y):
        w, h = self.width(), self.height()
        self.luma = float(h-y)/float(h)
        #print("Slider._select({})".format(self.luma))
        self.repaint()
        self.clicked.emit(self.luma)

    def select(self, luma):
        self.luma = luma
        #print("Slider.select({})".format(self.luma))
    
    def get_luma(self):
        return self.luma

class HCYSelector(QtGui.QWidget):

    selected = QtCore.pyqtSignal(float,float,float)
    edited = QtCore.pyqtSignal()

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.box = QtGui.QHBoxLayout()
        self.wheel = WheelWidget()
        self.slider = SliderWidget()
        self.box.addWidget(self.slider, 1)
        self.box.addWidget(self.wheel, 5)
        self.setLayout(self.box)
        self.wheel.clicked.connect(self._on_click_wheel)
        self.wheel.edited.connect(self._on_wheel_edited)
        self.slider.clicked.connect(self._on_click_slider)
        self.harmonies_selector = None

    def _on_wheel_edited(self):
        self.edited.emit()

    def get_enable_editing(self):
        return self.wheel.enable_editing
    
    def set_enable_editing(self, value):
        self.wheel.enable_editing = value
        #print("Enable editing: {}".format(value))
        if value and self.wheel._harmonized is None:
            self.wheel._harmonized = [(0,0.9), (0, 0.3), (0.5, 0.3), (0.5, 0.9)]

    enable_editing = property(get_enable_editing, set_enable_editing)

    def _on_click_wheel(self, hue, chroma):
        self.slider.cache.hue = hue
        self.slider.cache.redraw(self.slider.width(), self.slider.height())
        self.update()
        self.selected.emit(hue, chroma, self.slider.luma)

    def _on_click_slider(self, luma):
        self.wheel.set_luma(luma)
        self.update()
        self.selected.emit(self.wheel.hue, self.wheel.chroma, luma)

    def setColor(self, color):
        if color is None:
            return
        h,c,y = color.getHCY()
        self.slider.cache.hue = h
        self.slider.cache.redraw(self.slider.width(), self.slider.height())
        self.slider.select(y)
        self.wheel.set_luma(y)
        self.wheel.select(h,c)
        self.update()

    def getColor(self):
        return self.wheel.get_color()

    def set_harmonized(self, list):
        pass
        #self.wheel._harmonized = list
        #self.repaint()

    def setHarmony(self, harmony, idx=None):
        self.set_harmony(harmony)
        if self.harmonies_selector is not None and idx is not None:
            self.harmonies_selector.select_item(idx)

    def set_harmony(self, harmony):
        current = self.getColor()
        if current is None:
            return
        self.wheel.set_harmony(harmony, current)

    def set_harmony_parameter(self, value):
        self.wheel.set_harmony_parameter(value, self.getColor())

    def get_harmonized(self):
        if self.wheel._harmonized is None:
            return None
        return [hcy(hue, chroma, self.slider.luma) for hue, chroma in self.wheel._harmonized]



