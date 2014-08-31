
from os.path import join, basename
from math import sqrt, floor
from gettext import gettext as _

from color.colors import *
from color import mixers
from palette.image import PaletteImage
from palette.storage.storage import *
from palette.storage.cluster import *

class Image(Storage):
    title = _("Raster image")
    filters = ["*.jpg", "*.png"]
    can_load = image_loading_supported
    can_save = True

    @staticmethod
    def check(filename):
        return True

    def save(self, file_w):
        w,h = self.palette.ncols * 48, self.palette.nrows * 48
        image = PaletteImage( self.palette ).get(w,h)
        image.save(file_w)

    def load(self, mixer, file_r, options=None):
        colors = get_common_colors(file_r)
        self.palette = create_palette(colors, mixer)
        return self.palette

