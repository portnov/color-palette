
from os.path import join, basename
from PyQt4 import QtGui
from lxml import etree as ET

from color.colors import *
from color import mixers
from palette.storage.storage import *

class Paletton(Storage):
    name = 'paletton'
    title = _("Paletton.com palette")
    filters = ["*.xml"]
    can_load = True
    can_save = False

    @staticmethod
    def check(filename):
        return ET.parse(filename).getroot().tag == 'palette'

    def load(self, mixer, file_r, options=None):
        self.palette = Palette(mixer)
        xml = ET.parse(file_r)

        xml_colorsets = xml.findall("colorset")
        max_colors = None
        for colorset in xml_colorsets:
            xml_colors = colorset.findall("color")
            n = len(xml_colors)
            if max_colors is None or n > max_colors:
                max_colors = n
        self.palette.ncols = max_colors
        all_slots = []
        for colorset in xml_colorsets:
            xml_colors = colorset.findall("color")
            for xml_color in xml_colors:
                r = int(xml_color.attrib['r'])
                g = int(xml_color.attrib['g'])
                b = int(xml_color.attrib['b'])
                clr = Color(r, g, b)
                slot = Slot(clr, user_defined=True)
                all_slots.append(slot)
        self.palette.setSlots(all_slots)
        print("Loaded palette: {}x{}".format( self.palette.nrows, self.palette.ncols ))
        return self.palette

