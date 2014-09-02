
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
    can_save = True

    @staticmethod
    def check(filename):
        return True

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

    def save(self, file_w):
        SVG_NS = "http://www.w3.org/2000/svg"
        NSMAP = dict(svg=SVG_NS)

        padding=2.0
        slotsz = 48.0
        
        rw = slotsz - padding
        rh = slotsz - padding

        svg = ET.Element("svg", nsmap=NSMAP)
        group = ET.SubElement(svg, "g", id="palette")

        def rect(x,y,w,h, color):
            ET.SubElement(group, "rect", x=str(x), y=str(y), width=str(w), height=str(h), fill=color.hex())

        for i in range(self.palette.nrows):
            for j in range(self.palette.ncols):
                x = slotsz * j + padding/2.0
                y = slotsz * i + padding/2.0
                color = self.palette.getColor(i,j)
                rect(x,y, rw, rh, color)

        svg.attrib['width']  = str( slotsz*self.palette.ncols )
        svg.attrib['height'] = str( slotsz*self.palette.nrows )

        ET.ElementTree(svg).write(file_w, encoding="utf-8", pretty_print=True, xml_declaration=True)




