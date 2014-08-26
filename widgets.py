#import sys

from math import cos, sin, pi, sqrt, atan2
from PyQt4 import QtGui, QtCore

import colors
from colors import seq

def dnd_pixmap(color):
    pixmap = QtGui.QPixmap(32,32)
    pixmap.fill(color)
    return pixmap

def create_qdrag_color(widget, color):
    r,g,b = color.getRGB()
    qcolor = QtGui.QColor(r,g,b)
    drag = QtGui.QDrag(widget)
    mime = QtCore.QMimeData()
    mime.setColorData(qcolor)
    drag.setMimeData(mime)
    drag.setPixmap(dnd_pixmap(color))
    return drag

class ColorWidget(QtGui.QLabel):
    clicked = QtCore.pyqtSignal()
    selected = QtCore.pyqtSignal()
    
    def __init__(self, *args):
        super(ColorWidget, self).__init__(*args);
        self.setMinimumSize(18, 18)
        self.clicked.connect(self.on_click)
        self.rgb = None
        self._mouse_pressed = False
        self._drag_start_pos = None
        self.select_button = QtCore.Qt.LeftButton
        self.drop_enabled = True
        self.pick_enabled = True
        self.setAcceptDrops(True)
        self.show()
    
    def setRGB(self, rgb):
        self.rgb = rgb
    
    def getColor(self):
        if self.rgb is None:
            return None
        return colors.Color(*self.rgb)
    
    def setColor(self, clr):
        self.setRGB(clr.getRGB())
        self.setToolTip(clr.verbose())
    
    def paintEvent(self, event):
        clr = self.getColor()
        if clr is not None:
            self.setToolTip(clr.verbose())
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(event, qp)
        qp.end()
    
    def wheelEvent(self, event):
        if (not self.pick_enabled) or (self.rgb is None):
            event.ignore()
            return
        event.accept()
        clr = self.getColor()
        steps = event.delta()/120.0
        if event.modifiers() & QtCore.Qt.ControlModifier:
            clr = colors.increment_hue(clr, 0.01*steps)
        elif event.modifiers() & QtCore.Qt.ShiftModifier:
            clr = colors.lighter(clr, 0.1*steps)
        else:
            clr = colors.saturate(clr, 0.1*steps)
        self.setColor(clr)
        self.repaint()
        self.selected.emit()

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self._mouse_pressed = True
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self._drag_start_pos = event.pos()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        if event.button() == self.select_button and self.pick_enabled:
            self.clicked.emit()
            event.accept()

    def mouseMoveEvent(self, event):
        if not self._mouse_pressed:
            return
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QtGui.QApplication.startDragDistance():
            return

        drag = create_qdrag_color(self, self.getColor())
        drag.exec_()

    def dragEnterEvent(self, event):
        if event.mimeData().hasColor() and self.drop_enabled:
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasColor():
            qcolor = QtGui.QColor(event.mimeData().colorData())
            r,g,b,_ = qcolor.getRgb()
            color = colors.Color(r,g,b)
            self.on_drop_color(color)
            self.repaint()
            self.selected.emit()
    
    def on_drop_color(self, color):
        self.setColor(color)
    
    def drawWidget(self, event,  qp):
        #print("Painting " + str(self))
        w, h = self.size().width(),  self.size().height()
        if self.rgb is None:
            if (w >= 70) and (h > 20):
                qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "<unset>")
            return
        
        qp.setBrush(QtGui.QColor(*self.rgb))
        qp.drawRect(0, 0,  w,  h)
        clr = self.getColor()
        if (w >= 150) and (h >= 50):
            qp.setPen(clr.invert())
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, clr.verbose())
        
    def on_click(self):
        #print("CLICK")
        current = self.getColor()
        if current is not None:
            clr = QtGui.QColorDialog.getColor(current)
        else:
            clr = QtGui.QColorDialog.getColor()
        r, g, b, a = clr.getRgb()
        self.setRGB((r, g, b))
        self.repaint()
        self.selected.emit()
    
    def sizeHint(self):
        return QtCore.QSize(100, 100)

class TwoColorsWidget(ColorWidget):

    second_color_set = QtCore.pyqtSignal()

    def __init__(self, *args):
        ColorWidget.__init__(self, *args)
        self.pick_enabled = False
        self._second_color = None

    def get_second_color(self):
        return self._second_color

    def set_second_color(self, color):
        self._second_color = color
        self.repaint()
        self.second_color_set.emit()

    second_color = property(get_second_color, set_second_color)

    def drawWidget(self, event, qp):
        w, h = self.size().width(),  self.size().height()

        if self.rgb is not None:
            qp.setBrush(QtGui.QColor(*self.rgb))
            qp.drawPolygon(QtCore.QPointF(0.0, 0.0),
                           QtCore.QPointF(w, 0.0),
                           QtCore.QPointF(0.0, h))

        if self._second_color is not None:
            qp.setBrush(self._second_color)
            qp.drawPolygon(QtCore.QPointF(w, 0.0),
                           QtCore.QPointF(w, h),
                           QtCore.QPointF(0.0, h))

    def on_drop_color(self, color):
        #print("Drop: " + str(color))
        self.second_color = color

class CacheImage(object):
    def __init__(self, mixer, w=0, h=0):
        self.colors = []
        self.mixer = mixer
        self.image_w = w
        self.image_h = h
        self.image = None
        self.calc()

    def setMixer(self,mixer):
        self.mixer = mixer
        self.redraw()
    
    def get(self, w, h):
        if self.image_w == w and self.image_h == h and self.image is not None:
            return self.image
        else:
            self.draw(w, h)
            return self.image
    
    def calc(self):
        self.colors = []
    
    def redraw(self, w=None, h=None):
        if w is None:
            w = self.image_w
        if h is None:
            h = self.image_h
        self.calc()
        self.draw(w, h)
    
    def draw(self, w, h):
        pass

class HueRing(CacheImage):
    
    STEPS=180
    
    def __init__(self, mixer, w=0, h=0):
        CacheImage.__init__(self, mixer, w, h)
    
    def calc(self):
      self.colors = [self.mixer.fromHue(hue) for hue in seq(0.0, 1.0, 1.0/self.STEPS)]
    
    def draw(self, w, h):
        self.image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        self.image.fill(0)
        self.image_w = w
        self.image_h = h
        R = min(w, h)/2.0
        r = 0.8 * R
        ow = oh = min(w, h)
        ox = (w-ow)/2.0
        oy = (h-oh)/2.0
        x0, y0 = w/2.0,  h/2.0
        iw, ih = 0.8*ow, 0.8*oh
        ix = (w-iw)/2.0
        iy = (h-ih)/2.0
        outrect = QtCore.QRectF(ox, oy, ow, oh)
        inrect = QtCore.QRectF(ix,iy, iw,ih)
        alpha = 0.0
        da = 360.0/self.STEPS
        qp = QtGui.QPainter()
        qp.begin(self.image)
        idx = 0
        #alpha = 30.0
        while alpha < 360.0:
            a = 2*pi*alpha/360.0
            b = 2*pi*(alpha + da)/360.0
            xA, yA = x0 + R*cos(a), y0 - R*sin(a)
            xB, yB = x0 + r*cos(b), y0 - r*sin(b)
            #print("Alpha: {:.2f}, dAlpha: {:.2f}, a: {:.2f}, b: {:.2f}, A: ({:.2f}, {:.2f}), B: ({:.2f}, {:.2f})".format( alpha, da, a, b, xA, yA, xB, yB))
            #xC, yC = x0 + R*cos(b), y0 + R*sin(b)
            #xD, yD = x0 + r*cos(a), y0 - r*sin(a)
            path = QtGui.QPainterPath()
            path.moveTo(xA, yA)
            path.arcTo(outrect, alpha, da)
            #path.lineTo(xB, yB)
            #path.lineTo(xD, yD)
            path.arcTo(inrect, (alpha+da), - da)
            path.lineTo(xA, yA)
            path.closeSubpath()
            #qp.setPen(self.colors[idx])
            #qp.drawPath(path)
            qp.fillPath(path, self.colors[idx])
            #break
            idx += 1
            alpha += da
        qp.end()


class Gradient(CacheImage):
    
    STEPS = 50
    
    def __init__(self, mixer, w=0, h=0, c1=None, c2=None, c3=None, c4=None):
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.c4 = c4
        CacheImage.__init__(self, mixer, w, h)
    
    def calc(self):
        self.colors = []
        if self.c1 is None or self.c2 is None or self.c3 is None or self.c4 is None:
            return
        left = [self.mixer.mix(self.c1, self.c3, q) for q in seq(0.0, 1.0, 1.0/self.STEPS)]
        right = [self.mixer.mix(self.c2, self.c4, q) for q in seq(0.0, 1.0, 1.0/self.STEPS)]
        for i in range(self.STEPS):
            cl = left[i]
            cr = right[i]
            self.colors.append([self.mixer.mix(cl, cr, q) for q in seq(0.0, 1.0,  1.0/self.STEPS)])
    
    def draw(self, w, h):
        #print("Draw: " + str((w, h)))
        self.image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        self.image.fill(0)
        self.image_w = w
        self.image_h = h
        rectw = w / self.STEPS
        recth = h /self.STEPS
        qp = QtGui.QPainter()
        qp.begin(self.image)
        for i, row in enumerate(self.colors):
            for j, col in enumerate(row):
                x = j * rectw
                y = i * recth
                qp.setBrush(col)
                qp.setPen(col)
                qp.drawRect(x, y, rectw, recth)
        qp.end()

class HueGradient(Gradient):
    def __init__(self, mixer, hue, w=None, h=None):
        self.hue = hue
        CacheImage.__init__(self, mixer, w, h)
    
    def setHue(self, hue):
        self.hue = hue
        self.redraw()

    def calc(self):
        self.colors = []
        if self.hue is None:
            return
        #print("Hue: "+str(self.hue))
        self.colors = [[self.mixer.shade(self.hue, s, v) for s in seq(0.0, 1.0, 1.0/self.STEPS)]
                            for v in seq(0.0, 1.0, 1.0/self.STEPS)]

class GradientWidget(QtGui.QLabel):
    def __init__(self, gradient,  *args):
        QtGui.QLabel.__init__(self, *args)
        self.gradient = gradient
    
    def paintEvent(self, event):
        if self.gradient.c1 is None or self.gradient.c2 is None or self.gradient.c3 is None or self.gradient.c4 is None:
            return
        w, h = self.size().width(),  self.size().height()
        image = self.gradient.get(w, h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)
        qp.end()
    
    def setColor(self, idx, clr):
        if idx == 1:
            self.gradient.c1 = clr
        elif idx == 2:
            self.gradient.c2 = clr
        elif idx == 3:
            self.gradient.c3 = clr
        elif idx == 4:
            self.gradient.c4 = clr
        w, h = self.size().width(),  self.size().height()
        self.gradient.redraw(w, h)
        self.update()
    
    def setMixer(self, mixer):
        self.gradient.mixer = mixer
        self.gradient.redraw(self.size().width(),  self.size().height())
        self.update()

class ImageWidget(QtGui.QLabel):
    def __init__(self, cache,  *args):
        """cache must have method:
           get(w,h) -> QImage
        """
        QtGui.QLabel.__init__(self, *args)
        self.cache = cache

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        image = self.cache.get(w, h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)
        qp.end()

class Selector(QtGui.QLabel):
    
    selectedSV = QtCore.pyqtSignal(float,float)
    selectedHue = QtCore.pyqtSignal(float)
    selected = QtCore.pyqtSignal()

    def __init__(self, mixer, *args):
        QtGui.QLabel.__init__(self, *args)
        self.mixer = mixer
        self.ring = HueRing(mixer)
        self.square = HueGradient(mixer, 0.0)
        self.mouse_pressed = False
        self.selected_sv = None
        self.selected_hue = 0.0
        self.selected_color = None
        self.harmony = None
        self.harmonized = []
        self.setMinimumSize(100,100)
        self.setAcceptDrops(True)

    def setColor(self, color):
        self.selected_color = color
        h = self.mixer.getHue(self.selected_color)
        self.selected_hue = h*2*pi
        self.square.setHue(h)
        self.selectedHue.emit(h)
        _,s,v = self.mixer.getShade(self.selected_color)
        self.selected_sv = s,v
        self._update_harmony()
        self.repaint()
        self.selected.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasColor():
            event.acceptProposedAction()

    def dropEvent(self, event):
        lst = event.mimeData().formats()
        #print([str(x) for x in lst])
        if event.mimeData().hasColor():
            qcolor = QtGui.QColor(event.mimeData().colorData())
            r,g,b,_ = qcolor.getRgb()
            #print(qcolor.getRgb())
            color = colors.Color(r,g,b)
            event.acceptProposedAction()
            #print(color)
            self.setColor(color)

    def sizeHint(self):
        return QtCore.QSize(120, 120)

    def setHarmony(self, harmony):
        self.harmony = harmony
        if self.selected_color is not None and self.harmony is not None:
            self.harmonized = self.harmony.get(self.selected_color)
        self.repaint()

    def setMixer(self, mixer):
        self.mixer = mixer
        self.square.setMixer(mixer)
        self.ring.setMixer(mixer)
        self.repaint()

    def _polar(self, r, phi):
        x0, y0 = self.size().width()/2.0,  self.size().height()/2.0
        return x0+r*cos(phi), y0-r*sin(phi)

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        ring = self.ring.get(w, h)
        m = min(w, h)
        iw = ih = m*0.8/sqrt(2.0)
        square = self.square.get(iw, ih)
        dx = (w - iw)/2.0
        dy = (h - ih)/2.0
        self.ls_square = QtCore.QRectF(dx,dy, iw, ih)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, ring)
        qp.drawImage(dx, dy, square)

        R = m/2.0
        r = 0.8*R
        x1,y1 = self._polar(r, self.selected_hue)
        x2,y2 = self._polar(R, self.selected_hue)
        qp.setPen(colors.Color(0,0,0))
        qp.drawLine(x1,y1, x2, y2)

        if self.selected_sv is not None:
            s, v = self.selected_sv
            x0 = s*iw + dx
            y0 = v*ih + dy
            x,y = x0-3, y0-3
            w = h = 6
            qp.setPen(colors.Color(0,0,0))
            qp.drawEllipse(x,y,w,h)

        if self.harmony is not None and self.selected_color is not None:
            h_selected = self.mixer.getHue(self.selected_color)
            clrs = self.harmony.get(self.selected_color)
            for clr in clrs:
                h,s,v = self.mixer.getShade(clr)
                if abs(h-h_selected) < 0.01:
                    x0 = s*iw + dx
                    y0 = v*ih + dy
                    x,y = x0-3, y0-3
                    w = h = 6
                    qp.setPen(colors.Color(0,0,0))
                    qp.drawRect(x,y,w,h)
                else:
                    x0,y0 = self._polar(r, h*2.0*pi)
                    x,y = x0-3, y0-3
                    w = h = 6
                    qp.setPen(colors.Color(0,0,0))
                    qp.drawRect(x,y,w,h)

        qp.end()

    def wheelEvent(self, event):
        if self.selected_color is None:
            event.ignore()
            return
        event.accept()
        clr = self.selected_color
        steps = event.delta()/120.0
        if event.modifiers() & QtCore.Qt.ControlModifier:
            clr = colors.increment_hue(clr, 0.01*steps)
        elif event.modifiers() & QtCore.Qt.ShiftModifier:
            clr = colors.lighter(clr, 0.1*steps)
        else:
            clr = colors.saturate(clr, 0.1*steps)
        self.setColor(clr)
        self.repaint()
        self.selected.emit()

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self.mouse_pressed = True
        event.accept()

    def is_on_ring(self, x, y):
        w, h = self.size().width(),  self.size().height()
        x0, y0 = w/2.0, h/2.0
        m = min(w, h)
        R = m/2.0
        r = 0.8*R
        rho = sqrt((x-x0)**2 + (y-y0)**2)
        return (rho > r) and (rho < R)
    
    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        self.mouse_pressed = False
        x,y = event.x(), event.y()
        self._select(x,y)
        event.accept()

    def getSV(self, x, y):
        xmin, ymin = self.ls_square.x(), self.ls_square.y()
        w, h = self.ls_square.width(), self.ls_square.height()
        s = (x - xmin)/w
        v = (y - ymin)/h
        return (s,v)

    def getHue(self, x, y):
        w, h = self.size().width(),  self.size().height()
        x0, y0 = w/2.0, h/2.0
        dx, dy = x-x0, y-y0
        hue = pi/2.0 - atan2(dx, -dy)
        if hue < 0.0:
            hue += 2*pi
        return hue
    
    def _update_harmony(self):
        if self.harmony is not None:
            self.harmonized = self.harmony.get(self.selected_color)

    def _select(self, x, y):
        if self.ls_square.contains(x,y):
            self.selected_sv = s, v = self.getSV(x,y)
            self.repaint()
            self.selectedSV.emit(s,v)
            h = self.selected_hue / (2.0*pi)
            self.selected_color = self.mixer.shade(h, s, v)
            self._update_harmony()
            self.selected.emit()
        elif self.is_on_ring(x,y):
            self.selected_hue = self.getHue(x,y)
            h = self.selected_hue / (2.0*pi)
            self.square.setHue(h)
            self.repaint()
            self.selectedHue.emit(h)
            if self.selected_sv is not None:
                s, v = self.selected_sv
                self.selected_color = self.mixer.shade(h, s, v)
                self._update_harmony()
                self.selected.emit()

    def mouseMoveEvent(self, event):
        x,y = event.x(), event.y()
        if self.mouse_pressed:
            self._select(x,y)

