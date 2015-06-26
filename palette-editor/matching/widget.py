
from PyQt4 import QtGui, QtSvg, QtCore

import transform
from color.colors import *
from color.spaces import *

class TemplateWidget(QtGui.QWidget):
    template_loaded = QtCore.pyqtSignal()
    colors_matched = QtCore.pyqtSignal()
    file_dropped = QtCore.pyqtSignal(unicode)

    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.setAcceptDrops(True)
        self._template_filename = None
        self._need_render = True
        self._src_colors = None
        self._dst_colors = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            path = unicode( urls[0].path() )
            self.file_dropped.emit(path)

    def _get_color(self, i):
        if i < len(self._colors):
            return self._colors[i]
        else:
            return Color(i*10, i*10, i*10)
    
    def _update(self):
        pass

    def loadTemplate(self, filename):
