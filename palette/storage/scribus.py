
from math import floor
from os.path import join, basename
from lxml import etree as ET

from color.colors import *
from color import mixers
from palette.storage.storage import *

cmyk_factor = float(1.0/255.0)

def fromHex_CMYK(s):
    t = s[1:]
    cs,ms,ys,ks = t[0:2], t[2:4], t[4:6], t[6:8]
    c,m,y,k = int(cs,16), int(ms,16), int(ys,16), int(ks,16)
    c,m,y,k = [float(x)*cmyk_factor for x in [c,m,y,k]]
    result = Color()
    result.setCMYK((c,m,y,k))
    return result

class Scribus(Storage):
    title = _("Scribus color swatches")
    filters = ["*.xml"]
    can_load = True
    can_save = True

    @staticmethod
    def check(filename):
        return ET.parse(filename).getroot().tag == 'SCRIBUSCOLORS'

    def load(self, mixer, file_r, options=None):
        xml = ET.parse(file_r).getroot()

        colors = []

        for elem in xml.findall("COLOR"):
            if "RGB" in elem.attrib:
                color = fromHex(elem.attrib["RGB"])
                colors.append(color)
            elif "CMYK" in elem.attrib:
                color = fromHex_CMYK(elem.attrib["CMYK"])
                colors.append(color)

        self.palette = create_palette(colors)
        return self.palette

    def save(self, file_w):
        xml = ET.Element("SCRIBUSCOLORS", NAME="Palette")
        
        for i,row in enumerate(self.palette.getColors()):
            for j,color in enumerate(row):
                name="Swatch-{}-{}".format(i,j)
                ET.SubElement(xml, "COLOR", NAME=name, RGB=color.hex())

        ET.ElementTree(xml).write(file_w, encoding="utf-8", pretty_print=True, xml_declaration=True)


