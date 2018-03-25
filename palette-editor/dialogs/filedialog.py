#!/usr/bin/python

import sys

from PyQt5 import QtGui, QtCore, QtWidgets


class PreviewFileDialog(QtWidgets.QFileDialog):
    def __init__(self, *args, **kwargs):
        QtWidgets.QFileDialog.__init__(self, *args, **kwargs)
        #self.setObjectName("PreviewFileDialog")

        box = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel(_("Preview:"))
        box.addWidget(label)
        box.addStretch()
        self.preview = QtWidgets.QLabel()
        self.preview.setMinimumSize(160,160)
        #geometry = self.preview.geometry()
        #geometry.setWidth(160)
        #geometry.setHeight(160)
        #self.preview.setGeometry(geometry)
        box.addWidget(self.preview)
        box.addStretch()
        self.layout().addLayout(box, 1, 3, 3, 1)
        
        self.currentChanged.connect(self.on_current_changed)

    def on_current_changed(self, qstr):
        path = unicode(qstr)
        image = self.get_preview_image(path)
        if image is None:
            self.preview.setText(_("No preview"))
        elif type(image) == QtGui.QPixmap:
            pixmap = image
            self.preview.setPixmap(pixmap.scaled(self.preview.width(), self.preview.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            pixmap = QtGui.QPixmap.fromImage(image)
            self.preview.setPixmap(pixmap.scaled(self.preview.width(), self.preview.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def get_preview_image(self, path):
        # No default implementation
        return None

class ImagePreviewFileDialog(PreviewFileDialog):
    def get_preview_image(self, path):
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            return None
        else:
            return pixmap

def get_filename(parent=None, caption=None, directory=None, filter=None, make_preview=None):
    if make_preview is None:
        filename = QtWidgets.QFileDialog.getOpenFileName(parent=parent, caption=caption, directory=directory, filter=filter)
        return str(filename)

    class Dialog(PreviewFileDialog):
        def get_preview_image(self, path):
            return make_preview(path)

    dialog = Dialog(parent=parent, caption=caption, directory=directory, filter=filter)
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
    if dialog.exec_():
        return unicode( dialog.selectedFiles()[0] )
    else:
        return None

def get_image_filename(parent=None, caption=None, directory=None, filter=None):
    dialog = ImagePreviewFileDialog(parent=parent, caption=caption, directory=directory, filter=filter)
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
    if dialog.exec_():
        return str( dialog.selectedFiles()[0] )
    else:
        return None

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    dialog = ImagePreviewFileDialog(caption="Open", directory=".", filter="*.svg")
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
    dialog.exec_()
    
