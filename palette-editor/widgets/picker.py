
from PyQt4 import QtGui, QtCore

from color.colors import *

class Picker(QtGui.QPushButton):
    def __init__(self, parent, text, model):
        QtGui.QPushButton.__init__(self, text, parent)
        self.model = model
        self.color = None
        self._picking = False
        self.border_color = None
        self.text = text
        self.clicked.connect(self._prepare)

    def getColor(self):
        return self.model.getColor()

    def setColor(self, clr, undo=False):
        if self.model.to_set_color():
            self.model.setColor(clr)

    def is_empty(self):
        return self.model.getColor() is None
    
    def paintEvent(self, event):
        if self.text is not None:
            QtGui.QPushButton.paintEvent(self, event)
            return 

        clr = self.getColor()
        if clr is not None:
            tooltip = self.model.get_tooltip()
            if tooltip is not None:
                self.setToolTip(tooltip)
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(event, qp)
        qp.end()

    def drawWidget(self, event,  qp):
        #print("Painting " + str(self))
        w, h = self.size().width(),  self.size().height()
        if self.is_empty():
            if (w >= 70) and (h > 20):
                qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "<unset>")
            if self.border_color is not None:
                qp.setPen(self.border_color)
                qp.drawRect(0, 0,  w,  h)
            return
        
        if self.border_color is not None:
            qp.setPen(self.border_color)
        clr = self.getColor()
        qp.setBrush(clr)
        qp.drawRect(0, 0,  w,  h)
        if (w >= 150) and (h >= 50):
            qp.setPen(clr.invert())
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, clr.verbose())

    def mouseMoveEvent(self, event):
        if self._picking:
            self._pick_color(event.globalPos())
            return
        return QtGui.QPushButton.mouseMoveEvent(self, event)
    
    def mouseReleaseEvent(self, event):
        if self._picking:
            self._picking = False
            self.releaseKeyboard()
            self.releaseMouse()
            self._pick_color(event.globalPos())
        return QtGui.QPushButton.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        if self._picking:
            if event.key() == QtCore.Qt.Key_Escape:
                self._picking = False
                self.releaseKeyboard()
                self.releaseMouse()
            event.accept()
            return
        return QtGui.QPushButton.keyPressEvent(self, event)

    def _prepare(self, event):
        #print "Clicked"
        self._picking = True
        self.grabKeyboard()
        self.grabMouse(QtCore.Qt.CrossCursor)

    def _pick_color(self, pos):
        desktop = QtGui.QApplication.desktop().winId()
        #screen = QtGui.QApplication.desktop().primaryScreen()
        pixmap = QtGui.QPixmap.grabWindow(desktop, pos.x(), pos.y(), 1, 1)
        img = pixmap.toImage()
        color = Color(QtGui.QColor(img.pixel(0,0)))
        self.setColor(color)

