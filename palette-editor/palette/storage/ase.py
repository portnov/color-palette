
from os.path import join, basename
from PyQt4 import QtGui
import struct

from color.colors import *
from color import mixers
from palette.storage.storage import *

# Adopted from Swatchbooker's adobe_ase.py
# Initial (c) 2008 Olivier Berten <olivier.berten@gmail.com>
# See also http://bazaar.launchpad.net/~olivier-berten/swatchbooker/trunk/view/head:/src/swatchbook/codecs/adobe_ase.py

class AsePalette(Storage):

    name = 'ase'
    title = _("Adobe swatch exchange (ase)")
    filters = ["*.ase"]
    can_save = False
    can_load = True
    
    @staticmethod
    def check(filename):
        with open(filename,'rb') as file:
            head = file.read(4)
            return (head == 'ASEF')

    def load(self, mixer, file, options=None):
        filename = None
        if hasattr(file,'read'):
            do_close = False
        elif type(file) in [str,unicode]:
            filename = file
            file = open(file, 'rb')
            do_close = True

        colors = []

        file.seek(4)
        version = struct.unpack('>2H', file.read(4))
        print("Reading ASE version {}".format(version))
        nblocks = struct.unpack('>L', file.read(4))[0]
        for i in range(nblocks):
            block_name = None
            block_type, block_size = struct.unpack('>HL', file.read(6))
            if block_size > 0:
                length = struct.unpack('>H', file.read(2))[0]
                if length > 0:
                    block_name = struct.unpack(str(length*2)+'s',file.read(length*2))[0]
                    block_name = unicode(block_name,'utf_16_be').split('\x00', 1)[0]
            if block_type == 0x0001: # Actual color
                model = struct.unpack('4s',file.read(4))[0]
                color = Color()
                if model == 'CMYK':
                    cmyk = list(struct.unpack('>4f',file.read(16)))
                    color.setCMYK(cmyk)
                elif model == 'RGB ':
                    rgb = list(struct.unpack('>3f',file.read(12)))
                    color.setRGB1(rgb)
                elif model == 'LAB ':
                    print("Lab model is not supported yet; block_name {}".format(block_name))
                    file.read(12)
                elif model == 'Gray':
                    gray = 1-struct.unpack('>f',file.read(4))[0]
                    color.setRGB1(gray, gray, gray)
                else:
                    print("Unknown color model: {}".format(model))
                    return None

                color_type = struct.unpack('>H',file.read(2))[0]
                if color_type == 0:
                    color.meta["Global"] = "1"
                elif color_type == 1:
                    color.meta["Spot"] = "1"
                if block_name:
                    color.name = block_name

                colors.append(color)

        self.palette = create_palette(colors)
        self.palette.meta["Version"] = str(version)
        if filename:
            self.palette.name = basename(filename)

        if do_close:
            file.close()

        return self.palette

