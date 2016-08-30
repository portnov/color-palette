
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
    title = _("Adobe swatch exchange")
    filters = ["*.ase"]
    can_save = True
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
        self.palette.meta["SourceFormat"] = "Adobe ase"
        if filename:
            self.palette.name = basename(filename)

        if do_close:
            file.close()

        return self.palette

    def save(self, file_w):
        header = 'ASEF\x00\x01\x00\x00'
        data = ''

        for row in self.palette.slots:
            for slot in row:
                block_size = 0
                color = slot.color

                name = color.name
                name_bytes = name.encode('utf_16_be')
                name_len_bytes = len(name_bytes)
                name_len = len(name)
                block_size += 4 + name_len_bytes + 4

                if color.meta["Spot"] == "1":
                    usage = '\x00\x01'
                elif color.meta["Global"] == "1":
                    usage = '\x00\x00'
                else:
                    usage = '\x00\x02'

                r,g,b = color.getRGB1()
                block_size += 14
                values = 'RGB ' + struct.pack('>3f', r,g,b)

                name_data = struct.pack('>H', name_len+1) + name_bytes + '\x00\x00'
                data += '\x00\x01' + struct.pack('>L', block_size) + name_data + values + usage

        count = self.palette.nrows * self.palette.ncols

        data = header + struct.pack('>L', count) + data
        with open(file_w, 'wb') as f:
            f.write(data)


