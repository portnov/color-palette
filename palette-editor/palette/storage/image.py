
from os.path import join, basename
from math import sqrt, floor

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

        colors = get_common_colors(file_r)
        colors.sort(cmp=_cmp)
        self.palette = create_palette(colors, mixer)
        return self.palette

