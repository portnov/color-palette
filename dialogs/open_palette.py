
from PyQt4 import QtGui, QtCore

from color import mixers
from palette.image import PaletteImage
from palette.storage.all import *
from filedialog import *

class PaletteOpenDialog(PreviewFileDialog):
    def __init__(self, *args, **kwargs):
        PreviewFileDialog.__init__(self, *args, **kwargs)
        self.options_widget = QtGui.QLabel("No options")
        self.options = None
        self._show_options()
        self.currentChanged.connect(self.show_options)
     
    def _show_options(self, widget=None):
        if widget is None:
            widget = self.options_widget
        if widget is self.options_widget:
            return
        if self.options_widget is not None:
            self.layout().removeWidget(self.options_widget)
        self.layout().addWidget(widget, 4,0, 1,3)
     
    def show_options(self, qstr):
        filename = unicode(qstr)
        self.options = None
        widget = self.get_options_widget(filename)
        self._show_options(widget)

    def get_options_widget(self, filename):
        loader = detect_storage(filename)
        return loader.get_options_widget(self, filename)

    def get_preview_image(self, path):
        palette = load_palette(path, options=self.options)
        image = PaletteImage(palette).get(160, 160)
        return image

def open_palette_dialog(parent=None, caption=None):
    dialog = PaletteOpenDialog(parent=parent, caption=caption, filter=get_all_filters())
    dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
    if dialog.exec_():
        filename = unicode( dialog.selectedFiles()[0] )
        return load_palette(filename, options = dialog.options)
    else:
        return None

def save_palette_filename(parent=None, caption=None):
    filename = QtGui.QFileDialog.getSaveFileName(parent, caption=caption, filter=get_all_filters())
    return unicode(filename)

def load_palette(filename, mixer=None, options=None):
    if mixer is None:
        mixer = mixers.MixerRGB
    loader = detect_storage(filename)
    if loader is None:
        return None
    palette = loader().load(mixer, filename, options)
    return palette

def save_palette(palette, path):
    loader = detect_storage(path)
    if loader is None:
        raise RuntimeError("Unknown file type!")
    loader(palette).save(path)

