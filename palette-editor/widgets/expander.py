
from PyQt5 import QtGui, QtCore, QtWidgets

class ToggleLabel(QtWidgets.QLabel):
    toggled = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, vertical=False, expanded=True, text=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        self.text = text
        self.expanded = expanded
        self.vertical = vertical
        self._mouse_pressed = False
        self.__rect = None
        self._expanded_icon = QtGui.QImage(locate_icon("expanded.png"))
        self._collapsed_icon = QtGui.QImage(locate_icon("collapsed.png"))

    def sizeHint(self):
        rect = self._rect()
        w,h = rect.width(), rect.height()
        if not self.expanded and self.vertical:
            return QtCore.QSize(h,w)
        else:
            return QtCore.QSize(w,h)

    def _rect(self):
        metrics = QtGui.QFontMetrics(self.font())
        size = metrics.size(0, self.text)
        result = QtCore.QRect(0,0, size.width()+25, size.height()+10)
#         if not self.expanded and self.vertical:
#             result = QtCore.QRect(0,0, size.width(), size.height())
#         else:
#             result = QtCore.QRect(0,0, size.height(), size.width())
        self.__rect = result
        return result

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        rect = self._rect()
        w, h = rect.width(), rect.height()
        if self.vertical and not self.expanded:
            qp.translate(QtCore.QPointF(h,0))
            rect = QtCore.QRect(rect.y(),-rect.x(), rect.width(), rect.height())
            qp.rotate(90)
        #print rect.x(), rect.y(), rect.width(), rect.height()
        qp.setPen(QtGui.QColor(0,0,0))
        if self.underMouse():
            qp.setBrush(QtGui.QColor(127,127,127,127))
        rect = QtCore.QRect(rect.x(), rect.y(), rect.width()-2, rect.height()-2)
        qp.drawRoundedRect(rect,3,3)
        rect = QtCore.QRect(rect.x()+19, rect.y(), rect.width()-19, rect.height())
        qp.drawText(rect, QtCore.Qt.AlignCenter, self.text)
        if self.expanded:
            icon = self._expanded_icon
        else:
            icon = self._collapsed_icon
        qp.drawImage(6,6, icon)
#         qp.resetTransform()
#         rect = self.rect()
#         rect = QtCore.QRect(rect.x(), rect.y(), rect.width()-1, rect.height()-1)
#         qp.drawRect(rect)
        qp.end()

    def enterEvent(self, event):
        self.repaint()

    def leaveEvent(self, event):
        self.repaint()

    def toggle(self):
        self.expanded = not self.expanded
        #self._w, self._h = self._h, self._w
        rect = self._rect()
        w,h = rect.width(), rect.height()
        if self.vertical and not self.expanded:
            self.setMinimumSize(h,w)
        else:
            self.setMinimumSize(w,h)
        self.repaint()
        self.toggled.emit()

    def mousePressEvent(self, event):
        self._mouse_pressed = True

    def mouseReleaseEvent(self, event):
        if self._mouse_pressed:
            #print "click"
            self.toggle()
        self._mouse_pressed = False
        event.accept()


class ExpanderWidget(QtWidgets.QWidget):
    def __init__(self, text, widget, parent=None, vertical=False):
        super(ExpanderWidget, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout()

        self.toggle = ToggleLabel(text = text, vertical=vertical)
        self.toggle.toggled.connect(self._on_toggled)

        if isinstance(widget, QtWidgets.QLayout):
            widget_ = QtWidgets.QWidget()
            widget_.setLayout(widget)
            widget = widget_

        self.widget = widget

        self.layout.addWidget(self.toggle,1)
        self.layout.addWidget(self.widget,9)
        self.setLayout(self.layout)
        #self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
        #self.setStyleSheet("* {border: #000}")

    def _on_toggled(self):
        if self.widget.isVisible():
            self.widget.setVisible(False)
        else:
            self.widget.setVisible(True)

