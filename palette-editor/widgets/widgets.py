#import sys

from math import cos, sin, pi, sqrt, atan2
from PyQt5 import QtGui, QtCore, QtWidgets

from color import colors
from color.colors import seq

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
    mime.setData("application/x-metainfo", color.meta.to_xml())
    drag.setMimeData(mime)
    drag.setPixmap(dnd_pixmap(color))
    return drag

class ItemModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self.last_enabled = True

    def flags(self, index):
        default = super(ItemModel, self).flags(index)
        if not self.last_enabled:
            if index.row() == self.rowCount()-1:
                return default & ~QtCore.Qt.ItemIsEnabled
        return default

class ClassSelector(QtWidgets.QComboBox):

    selected = QtCore.pyqtSignal(int, int)


    def __init__(self, parent=None, pairs=None):
        QtWidgets.QComboBox.__init__(self, parent)
        model = ItemModel()
        self.setModel(model)
        self.pairs = pairs
        self._prev_idx = 0
        for name, nothing in self.pairs:
            self.addItem(name)
        self._skip_select = False
        self.currentIndexChanged.connect(self._on_select)

    def set_last_enabled(self, value):
        self.model().last_enabled = value
        self.update()

    def _on_select(self, idx):
        if not self._skip_select:
            self.selected.emit(self._prev_idx, idx)
        self._prev_idx = idx

    def get_item(self, idx):
        _, cls = self.pairs[idx]
        return cls

    def get_current_item(self):
        idx = self.currentIndex()
        return self.get_item(idx)
    
    def select_item(self, idx):
        self._skip_select = True
        self.setCurrentIndex(idx)
        self._skip_select = False

class ParamSlider(QtWidgets.QSlider):
    changed = QtCore.pyqtSignal(int,int)

    def __init__(self, parent=None):
        QtWidgets.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(50)
        self.valueChanged.connect(self._on_change)
        self._prev_value = 50
        self._skip_change = False

    def _on_change(self, value):
        if not self._skip_change:
            self.changed.emit(self._prev_value, value)
        self._prev_value = value

    def set_value(self, value):
        self._skip_change = True
        self.setValue(value)
        self._skip_change = False

class ColorWidget(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()
    selected = QtCore.pyqtSignal()
    dropped = QtCore.pyqtSignal(float,float,float)
    cleared = QtCore.pyqtSignal()
    
    def __init__(self, parent, model, *args):
        QtWidgets.QLabel.__init__(self, parent, *args)
        self.model = model
        self.model.widget = self
        self.setMinimumSize(18, 18)
        self.clicked.connect(self.on_click)
        self.cleared.connect(self.on_clear)
        self._mouse_pressed = False
        self._drag_start_pos = None
        self.drop_enabled = True
        self.pick_enabled = True
        self.border_color = None
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        self.show()

    def is_empty(self):
        return self.model.getColor() is None
    
    def getColor(self):
        return self.model.getColor()

    def setColor_(self, clr):
        self.model.color = clr
        tooltip = self.model.get_tooltip()
        if tooltip is not None:
            self.setToolTip(tooltip)
    
    def setColor(self, clr, undo=False):
        if self.model.to_set_color():
            self.model.setColor(clr)
        else:
            if not undo and clr is not None:
                r,g,b = clr.getRGB()
                self.dropped.emit(r,g,b)
            elif undo:
                self.model.color = clr
        tooltip = self.model.get_tooltip()
        if tooltip is not None:
            self.setToolTip(tooltip)
    
    def paintEvent(self, event):
        clr = self.getColor()
        if clr is not None:
            tooltip = self.model.get_tooltip()
            if tooltip is not None:
                self.setToolTip(tooltip)
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(event, qp)
        qp.end()
    
    def wheelEvent(self, event):
        if (not self.pick_enabled) or self.is_empty():
            event.ignore()
            return
        event.accept()
        steps = event.delta()/120.0
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.model.rotate_color(0.01*steps)
        elif event.modifiers() & QtCore.Qt.ShiftModifier:
            self.model.lighter(0.1*steps)
        else:
            self.model.saturate(0.1*steps)
        self.repaint()
        if not self.model.to_set_color():
            self.selected.emit()

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self._mouse_pressed = True
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self._drag_start_pos = event.pos()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        if self.pick_enabled:
            if event.button() == self.model.options.select_button:
                self.clicked.emit()
                event.accept()
            elif event.button() == self.model.options.menu_button:
                menu = self.model.get_context_menu(self)
                if menu:
                    menu.exec_(event.globalPos())
                    event.accept()
            elif event.button() == self.model.options.clear_button:
                self.cleared.emit()
                event.accept()

    def mouseMoveEvent(self, event):
        if not self._mouse_pressed:
            return
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QtWidgets.QApplication.startDragDistance():
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
            if event.mimeData().hasFormat("application/x-metainfo"):
                data = event.mimeData().data("application/x-metainfo")
                color.meta.set_from_xml(str(data))
            self.on_drop_color(color)
            self.repaint()
            if not self.model.to_set_color():
                self.selected.emit()
    
    def on_drop_color(self, color):
        self.setColor(color)
    
    def drawWidget(self, event,  qp):
        #print("Painting " + str(self))
        w, h = self.size().width(),  self.size().height()
        if self.is_empty():
            if (w >= 70) and (h > 20):
                qp.drawText(event.rect(), QtCore.Qt.AlignCenter, _("<unset>"))
            if self.border_color is not None:
                qp.setPen(self.border_color)
                qp.drawRect(QtCore.QRectF(0, 0,  w,  h))
            return
        
        if self.border_color is not None:
            qp.setPen(self.border_color)
        clr = self.getColor()
        qp.setBrush(clr)
        qp.drawRect(QtCore.QRectF(0, 0,  w,  h))
        if (w >= 150) and (h >= 50):
            qp.setPen(clr.invert())
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, clr.verbose())
        
    def on_click(self):
        #print("CLICK")
        current = self.getColor()
        if current is not None:
            clr = QtWidgets.QColorDialog.getColor(current)
        else:
            clr = QtWidgets.QColorDialog.getColor()
        r, g, b, a = clr.getRgb()
        self.setColor(colors.Color(r,g,b))
        self.repaint()
        if not self.model.to_set_color():
            self.selected.emit()

    def on_clear(self):
        self.model.clear()
        self.repaint()
        if not self.model.to_set_color():
            self.selected.emit()
    
    def sizeHint(self):
        return QtCore.QSize(100, 100)

class TwoColorsWidget(ColorWidget):

    second_color_set = QtCore.pyqtSignal()

    def __init__(self, parent, model, *args):
        ColorWidget.__init__(self, parent, model, *args)
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

        if not self.is_empty():
            qp.setBrush(self.getColor())
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

class ColorHistoryWidget(QtWidgets.QWidget):

    selected = QtCore.pyqtSignal()

    def __init__(self, model, vertical=False, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.model = model
        self.model.widget = self
        self.selected_color = None

        if vertical:
            self.layout = QtWidgets.QVBoxLayout()
        else:
            self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.setup()

    def setup(self):
        self.slots = []
        for color_model in self.model.color_models:
            slot = ColorWidget(self, color_model)
            slot.pick_enabled = False
            slot.selected.connect(lambda: self.on_select(slot))
            self.layout.addWidget(slot)
            self.slots.append(slot)

    def setColors(self, colors, undo=False):
        for slot, color in zip(self.slots, colors):
            slot.setColor(color, undo)

    def getColors(self):
        result = []
        for slot in self.slots:
            result.append(slot.getColor())
        return result

    def on_select(self, slot):
        self.selected_color = slot.getColor()
        self.selected.emit()



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
        if w is None or h is None:
             return
        self.calc()
        self.draw(w, h)
    
    def draw(self, w, h):
        pass

class HueRing(CacheImage):
    
    STEPS=180
    
    def __init__(self, mixer, width_coef=0.8, w=0, h=0):
        self.width_coef = width_coef
        CacheImage.__init__(self, mixer, w, h)
    
    def calc(self):
      self.colors = [self.mixer.fromHue(hue) for hue in seq(0.0, 1.0, 1.0/self.STEPS)]
    
    def draw(self, w, h):
        if w is None or h is None:
             return
        self.image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        self.image.fill(0)
        self.image_w = w
        self.image_h = h
        R = min(w, h)/2.0
        r = self.width_coef * R
        ow = oh = min(w, h)
        ox = (w-ow)/2.0
        oy = (h-oh)/2.0
        x0, y0 = w/2.0,  h/2.0
        iw, ih = self.width_coef*ow, self.width_coef*oh
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

class HueStepsRing(CacheImage):
    def __init__(self, mixer, steps=12, inner_coef=0.75, outer_coef=0.85, w=0, h=0):
        self.STEPS = steps
        self.inner_coef = inner_coef
        self.outer_coef = outer_coef
        self.chroma = 1.0
        self.luma = 1.0
        self.start_hue = 0.0
        CacheImage.__init__(self, mixer, w, h)

    def setShade(self, chroma, luma):
        self.chroma = chroma
        self.luma = luma
        self.redraw()

    def setStartHue(self, hue):
        self.start_hue = hue
        self.redraw()

    def calc(self):
        self.hues = [hue % 1.0 for hue in seq(self.start_hue, self.start_hue + 1.0, 1.0/self.STEPS)]
        #hues = sorted(hues)
        self.colors = [self.mixer.shade(hue % 1.0, self.chroma, self.luma) for hue in self.hues] 

    def get_color_at_angle(self, a):
        #print "Searching for a={}".format(a)
        da2 = 0.5/float(self.STEPS)
        for i, hue in enumerate(self.hues):
            #amin = a1 - 2*pi/float(self.STEPS) 
            amax = 2*pi*((hue + da2) % 1.0)
            amin = 2*pi*((hue - da2) % 1.0)

            amax1 = amax + 2*pi
            amin1 = amin + 2*pi

            amax2 = amax - 2*pi
            amin2 = amin - 2*pi

            amax = min(amax, amax1, amax2, key=lambda x: abs(a-x))
            amin = min(amin, amin1, amin2, key=lambda x: abs(a-x))
            #print "  Test {} < {} < {}".format(amin, a, amax)
            if (amin <= a < amax):
                return self.colors[i]
        return self.colors[0]

    def get_hue_at_angle(self, a):
        color = self.get_color_at_angle(a)
        return self.mixer.getHue(color)

    def draw(self, w, h):
        if w is None or h is None:
             return
        self.image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        self.image.fill(0)
        self.image_w = w
        self.image_h = h
        m = min(w, h)
        R = self.outer_coef * m/2.0
        r = self.inner_coef * m/2.0

        ow = oh = self.outer_coef*m
        ox = (w-ow)/2.0
        oy = (h-oh)/2.0
        x0, y0 = w/2.0,  h/2.0
        iw, ih = self.inner_coef*m, self.inner_coef*m
        #print "HueStepsRing: m={}, iw={}, ih={}".format(m, iw, ih)
        ix = (w-iw)/2.0
        iy = (h-ih)/2.0
        outrect = QtCore.QRectF(ox, oy, ow, oh)
        inrect = QtCore.QRectF(ix,iy, iw,ih)
        alpha = 0.0
        da = 360.0/self.STEPS
        da2 = da/2.0
        qp = QtGui.QPainter()
        qp.begin(self.image)
        border_color = QtGui.QColor(127, 127, 127)
        pen = QtGui.QPen(border_color)
        pen.setWidthF(2.0)
        alpha = self.start_hue * 360.0 - da2
        for idx in range(self.STEPS):
            a = 2*pi*alpha/360.0
            b = 2*pi*(alpha + da)/360.0
            xA, yA = x0 + R*cos(a), y0 - R*sin(a)
            xB, yB = x0 + r*cos(b), y0 - r*sin(b)
            path = QtGui.QPainterPath()
            path.moveTo(xA, yA)
            path.arcTo(outrect, alpha, da)
            path.arcTo(inrect, (alpha+da), - da)
            path.lineTo(xA, yA)
            path.closeSubpath()
            qp.fillPath(path, self.colors[idx])
            qp.strokePath(path, pen)
            #break
            alpha += da
        qp.end()

class Spectrum(CacheImage):
    STEPS = 100

    def __init__(self, mixer, w=0, h=0):
        CacheImage.__init__(self, mixer, w, h)

    def calc(self):
        self.colors = [self.mixer.fromHue(h) for h in seq(0.0, 1.0, 1.0/self.STEPS)]

    def draw(self, w, h):
        #print("Draw: " + str((w, h)))
        if w is None or h is None:
             return
        self.image = QtGui.QImage(w, h,  QtGui.QImage.Format_ARGB32_Premultiplied)
        self.image.fill(0)
        self.image_w = w
        self.image_h = h
        rectw = float(w) / self.STEPS
        qp = QtGui.QPainter()
        qp.begin(self.image)
        for i, col in enumerate(self.colors):
            x = i * rectw
            y = 0
            qp.setBrush(col)
            qp.setPen(col)
            qp.drawRect(QtCore.QRectF(x, y, rectw, h))
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
        if w is None or h is None:
             return
        w = int(w)
        h = int(h)
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
                qp.drawRect(QtCore.QRectF(x, y, rectw, recth))
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

class GradientWidget(QtWidgets.QLabel):
    def __init__(self, gradient,  *args):
        QtWidgets.QLabel.__init__(self, *args)
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

class ImageWidget(QtWidgets.QLabel):
    def __init__(self, cache,  *args):
        """cache must have method:
           get(w,h) -> QImage
        """
        QtWidgets.QLabel.__init__(self, *args)
        self.cache = cache

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        image = self.cache.get(w, h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)
        qp.end()

class Selector(QtWidgets.QLabel):
    
    selectedSV = QtCore.pyqtSignal(float,float)
    selectedHue = QtCore.pyqtSignal(float)
    selected = QtCore.pyqtSignal(int, colors.Color, colors.Color)

    manual_edit_implemented = False

    def __init__(self, mixer, hue_steps=None, *args):
        QtWidgets.QLabel.__init__(self, *args)
        self.mixer = mixer
        self.hue_steps = hue_steps
        if hue_steps is None:
            self.ring_width_coef = 0.8
            self.steps_inner_coef = 0.8
        else:
            self.ring_width_coef = 0.85
            self.steps_inner_coef = 0.7
        self.ring = HueRing(mixer, width_coef=self.ring_width_coef)
        if hue_steps is None:
            self.steps = None
        else:
            self.steps = HueStepsRing(mixer, steps=hue_steps, outer_coef=self.ring_width_coef, inner_coef=self.steps_inner_coef)
        self.square = HueGradient(mixer, 0.0)
        self.mouse_pressed = False
        self.selected_sv = None
        self.selected_hue = 0.0
        self._prev_color = colors.Color(0,0,0)
        self.selected_color = colors.Color(0,0,0)
        self.harmony = None
        self._harmony_parameter = 0.5
        self.harmonized = []
        self.setMinimumSize(100,100)
        self.setAcceptDrops(True)
        self.class_selector = None
        self.harmonies_selector = None
        self._sequence = 0

    def set_hue_steps(self, hue_steps=None):
        self.hue_steps = hue_steps
        if hue_steps is None:
            self.ring_width_coef = 0.8
            self.steps_inner_coef = 0.8
            self.steps = None
        else:
            self.ring_width_coef = 0.85
            self.steps_inner_coef = 0.7
            self.steps = HueStepsRing(self.mixer, steps=hue_steps, outer_coef=self.ring_width_coef, inner_coef=self.steps_inner_coef)
            _,s,v = self.mixer.getShade(self.selected_color)
            self.selected_sv = s,v
            self.steps.setShade(s, v)
            self.steps.calc()
        self.ring = HueRing(self.mixer, width_coef=self.ring_width_coef)
        self.repaint()

    def setColor(self, color, repaint=True, no_signal=False):
        if color is not None:
            self.selected_color = color
            h = self.mixer.getHue(self.selected_color)
            self.selected_hue = h*2*pi
            self.square.setHue(h)
            if self.steps is not None:
                self.steps.setStartHue(h)
            self.selectedHue.emit(h)
            _,s,v = self.mixer.getShade(self.selected_color)
            self.selected_sv = s,v
            if self.steps is not None:
                self.steps.setShade(s, v)
            self._update_harmony()
            if repaint:
                self.repaint()
            if not no_signal:
                self.selected.emit(self._sequence, self._prev_color, self.selected_color)

    def dragEnterEvent(self, event):
        if event.mimeData().hasColor():
            event.acceptProposedAction()

    def dropEvent(self, event):
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

    def setHarmony(self, harmony, idx=None):
        self.harmony = harmony
        if self.selected_color is not None and self.harmony is not None:
            self.harmonized = self.harmony.get(self.selected_color, self._harmony_parameter)
        if self.harmonies_selector is not None and idx is not None:
            self.harmonies_selector.select_item(idx)
        self.repaint()

    def set_harmony_parameter(self, value):
        self._harmony_parameter = value
        if self.selected_color is not None and self.harmony is not None:
            self.harmonized = self.harmony.get(self.selected_color, self._harmony_parameter)
            self.repaint()
            if self.isVisible():
                self.selected.emit(self._sequence, self._prev_color, self.selected_color)

    def setMixer_(self, mixer, idx=None, repaint=True):
        self.mixer = mixer
        self.square.mixer = mixer
        if self.steps is not None:
            self.steps.mixer = mixer
        self.ring.mixer = mixer
        if idx is not None and self.class_selector is not None:
            self.class_selector.select_item(idx)
        if repaint:
            self.repaint()

    def setMixer(self, mixer, idx=None):
        self.mixer = mixer
        self.square.setMixer(mixer)
        if self.steps is not None:
            self.steps.setMixer(mixer)
        self.ring.setMixer(mixer)
        if idx is not None and self.class_selector is not None:
            self.class_selector.select_item(idx)
        self.repaint()

    def _polar(self, r, phi):
        x0, y0 = self.size().width()/2.0,  self.size().height()/2.0
        return x0+r*cos(phi), y0-r*sin(phi)

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        ring = self.ring.get(w, h)
        if self.steps is not None:
            steps = self.steps.get(w, h)
        else:
            steps = None
        m = min(w, h)
        iw = ih = m*self.steps_inner_coef /sqrt(2.0)
        #print "Selector: m = {}, iw = ih = {}".format(m, iw)
        square = self.square.get(iw, ih)
        dx = (w - iw)/2.0
        dy = (h - ih)/2.0
        self.ls_square = QtCore.QRectF(dx,dy, iw, ih)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, ring)
        if steps is not None:
            qp.drawImage(0, 0, steps)
        qp.drawImage(QtCore.QPointF(dx, dy), square)

        R = m/2.0
        r = self.ring_width_coef*R
        x1,y1 = self._polar(r, self.selected_hue)
        x2,y2 = self._polar(R, self.selected_hue)
        qp.setPen(colors.Color(0,0,0))
        qp.drawLine(QtCore.QPointF(x1,y1), QtCore.QPointF(x2, y2))

        if self.selected_sv is not None:
            s, v = self.selected_sv
            x0 = s*iw + dx
            y0 = v*ih + dy
            x,y = x0-3, y0-3
            w = h = 6
            qp.setBrush(QtGui.QColor(255,255,255, 127))
            qp.setPen(colors.Color(0,0,0))
            qp.drawEllipse(QtCore.QRectF(x,y,w,h))

        if self.harmony is not None and self.selected_color is not None:
            h_selected = self.mixer.getHue(self.selected_color)
            clrs = self.harmony.get(self.selected_color, self._harmony_parameter)
            for clr in clrs:
                h,s,v = self.mixer.getShade(clr)
                if abs(h-h_selected) < 0.01:
                    x0 = s*iw + dx
                    y0 = v*ih + dy
                    x,y = x0-3, y0-3
                    w = h = 6
                    qp.setPen(colors.Color(0,0,0))
                    qp.drawRect(QtCore.QRectF(x,y,w,h))
                else:
                    x0,y0 = self._polar(r, h*2.0*pi)
                    x,y = x0-3, y0-3
                    w = h = 6
                    qp.setPen(colors.Color(0,0,0))
                    qp.drawRect(QtCore.QRectF(x,y,w,h))

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
        #self.selected.emit(self

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
        r = self.ring_width_coef*R
        rho = sqrt((x-x0)**2 + (y-y0)**2)
        return (rho > r) and (rho < R)

    def is_on_steps(self, x, y):
        if self.steps is None:
            return False
        w, h = self.size().width(),  self.size().height()
        x0, y0 = w/2.0, h/2.0
        m = min(w, h)
        R = self.ring_width_coef*m/2.0
        r = self.steps_inner_coef*m/2.0
        rho = sqrt((x-x0)**2 + (y-y0)**2)
        return (rho > r) and (rho < R)
    
    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        self.mouse_pressed = False
        x,y = event.x(), event.y()
        self._select(x,y)
        event.accept()
        self._sequence += 1

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

    def getHueStep(self, x, y):
        if self.steps is not None:
            hue = self.getHue(x,y)
            return self.steps.get_hue_at_angle(hue)
        else:
            return None
    
    def _update_harmony(self):
        if self.harmony is not None:
            self.harmonized = self.harmony.get(self.selected_color, self._harmony_parameter)

    def get_harmonized(self):
        return self.harmonized

    def _select(self, x, y):
        if self.ls_square.contains(x,y):
            self.selected_sv = s, v = self.getSV(x,y)
            if self.steps is not None:
                self.steps.setShade(s, v)
            self.repaint()
            self.selectedSV.emit(s,v)
            h = self.selected_hue / (2.0*pi)
            self._prev_color = self.selected_color
            self.selected_color = self.mixer.shade(h, s, v)
            self._update_harmony()
            #print "Selecting: {} -> {}".format(self._prev_color, self.selected_color)
            self.selected.emit(self._sequence, self._prev_color, self.selected_color)

        elif self.is_on_steps(x,y):
            hue = self.getHueStep(x,y)
            #print "Click on steps, hue={}".format(hue)
            self.selected_hue = hue*2.0*pi
            self.square.setHue(hue)
            self.steps.setStartHue(hue)
            self.repaint()
            self.selectedHue.emit(hue)
            if self.selected_sv is not None:
                s, v = self.selected_sv
                self._prev_color = self.selected_color
                self.selected_color = self.mixer.shade(hue, s, v)
                self._update_harmony()
                self.selected.emit(self._sequence, self._prev_color, self.selected_color)

        elif self.is_on_ring(x,y):
            self.selected_hue = self.getHue(x,y)
            h = self.selected_hue / (2.0*pi)
            self.square.setHue(h)
            if self.steps is not None:
                self.steps.setStartHue(h)
            self.repaint()
            self.selectedHue.emit(h)
            if self.selected_sv is not None:
                s, v = self.selected_sv
                self._prev_color = self.selected_color
                self.selected_color = self.mixer.shade(h, s, v)
                self._update_harmony()
                self.selected.emit(self._sequence, self._prev_color, self.selected_color)

    def mouseMoveEvent(self, event):
        x,y = event.x(), event.y()
        if self.mouse_pressed:
            self._select(x,y)
