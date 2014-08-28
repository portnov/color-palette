
from PyQt4 import QtGui, QtCore

from color import mixers
from palette.image import PaletteImage
from palette.storage.all import *
from filedialog import *

class PaletteOpenDialog(PreviewFileDialog):
    def get_preview_image(self, path):
        loader = detect_storage(path)
        if loader is None:
            return None
        palette = loader().load(mixers.MixerRGB, path)
        image = PaletteImage(palette).get(160, 160)
        return image


def get_palette_filename(parent=None, caption=None, directory=None):
    dialog = PaletteOpenDialog(parent=parent, caption=caption, directory=directory, filter=get_all_filters())
    dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
    if dialog.exec_():
        return unicode( dialog.selectedFiles()[0] )
    else:
        return None

