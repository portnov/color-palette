
from os.path import join, basename
from math import sqrt, floor
from PyQt4 import QtGui

from color.colors import *
from color import mixers
from palette.image import PaletteImage
from palette.palette import *
from palette.storage.storage import *
from palette.storage.cluster import *

LOAD_MORE = 1
LOAD_LESS = 2

print("Ok")

class Image(Storage):
    title = _("Raster image")
    filters = ["*.jpg", "*.png", "*.gif"]
    can_load = image_loading_supported
    can_save = True

    @staticmethod
    def check(filename):
        return True

    @staticmethod
    def get_options_widget(dialog, filename):
        if use_sklearn:
            return None

        def on_method_changed(checked):
            method = None
            if dialog._more_button.isChecked():
                method = LOAD_MORE
            elif dialog._less_button.isChecked():
                method = LOAD_LESS
            dialog.options = method
            dialog.on_current_changed(filename)

        group_box = QtGui.QGroupBox(_("Loading method"))
        dialog._more_button = more = QtGui.QRadioButton(_("Use 49 most used colors"))
        dialog._less_button = less = QtGui.QRadioButton(_("Use 9 most used colors and mix them"))

        more.toggled.connect(on_method_changed)
        less.toggled.connect(on_method_changed)

        if dialog.options != LOAD_LESS:
            more.setChecked(True)
        else:
            less.setChecked(True)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(more)
        vbox.addWidget(less)
        group_box.setLayout(vbox)
        return group_box

    def save(self, file_w):
        w,h = self.palette.ncols * 48, self.palette.nrows * 48
        image = PaletteImage( self.palette ).get(w,h)
        image.save(file_w)

    def load(self, mixer, file_r, options=None):
        def _cmp(clr1,clr2):
            h1,s1,v1 = clr1.getHSV()
            h2,s2,v2 = clr2.getHSV()
            x = cmp(h1,h2)
            if x != 0:
                return x
            x = cmp(v1,v2)
            if x != 0:
                return x
            return cmp(s1,s2)

        if use_sklearn or options != LOAD_LESS:
            colors = get_common_colors(file_r)
            colors.sort(cmp=_cmp)
            self.palette = create_palette(colors, mixer)
            return self.palette

        else:
            colors = get_common_colors(file_r, n_clusters=9)
            colors.sort(cmp=_cmp)

            palette = Palette(mixer, nrows=7, ncols=7)

            palette.paint(0, 0, colors[0])
            palette.paint(0, 3, colors[1])
            palette.paint(0, 6, colors[2])
            palette.paint(3, 0, colors[3])
            palette.paint(3, 3, colors[4])
            palette.paint(3, 6, colors[5])
            palette.paint(6, 0, colors[6])
            palette.paint(6, 3, colors[7])
            palette.paint(6, 6, colors[8])

            palette.need_recalc_colors = True
            palette.recalc()

            return palette


