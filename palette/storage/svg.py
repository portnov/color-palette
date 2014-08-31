
from os.path import join, basename
from math import sqrt, floor
from gettext import gettext as _
from PyQt4 import QtGui
from lxml import etree as ET

from color.colors import *
from color import mixers
from palette.storage.storage import *
from matching.svg import read_template

class SVG(Storage):
    title = _("SVG images")
    filters = ["*.svg"]
    can_load = True
    can_save = False

    @staticmethod
    def check(filename):
        return ET.parse(filename).getroot().tag == '{http://www.w3.org/2000/svg}svg'

    def load(self, mixer, file_r, options=None):
        self.palette = Palette(mixer)
        self.palette.ncols = None

        all_slots = []
        colors = []

        def add_color(clr):
            for c in colors:
                if c.getRGB() == clr.getRGB():
                    return None
            colors.append(clr)
            return clr

        svg_colors,x = read_template(file_r)
        for clr in svg_colors:
            color = add_color(clr)
            if color is None:
                continue
            slot = Slot(color, user_defined=True)
            all_slots.append(slot)
        n_colors = len(all_slots)
        if n_colors > MAX_COLS:
            self.palette.ncols = max( int( floor(sqrt(n_colors)) ), 1)
        else:
            self.palette.ncols = max(n_colors, 1)
        self.palette.setSlots(all_slots)
        print("Loaded palette: {}x{}".format( self.palette.nrows, self.palette.ncols ))
        return self.palette

