
from os.path import join, basename, getsize
from PyQt4 import QtGui
import struct

from color.colors import *
from color import mixers
from palette.storage.storage import *

# Adopted from Swatchbooker's adobe_aco.py
# Initial (c) 2008 Olivier Berten <olivier.berten@gmail.com>
# See also http://bazaar.launchpad.net/~olivier-berten/swatchbooker/trunk/view/head:/src/swatchbook/codecs/adobe_aco.py

class AcoPalette(Storage):

    name = 'aco'
    title = _("Adobe Photoshop color file format")
    filters = ["*.aco"]
    can_save = False
    can_load = True

    @staticmethod
    def check(filename):
        with open(filename, 'rb') as file:
            head = file.read(2)
            return struct.unpack('>h', head)[0] in (0,1,2)

    def load(self, mixer, file, options=None):
        filename = None
        if hasattr(file,'read'):
            do_close = False
        elif type(file) in [str,unicode]:
            filename = file
            file = open(file, 'rb')
            do_close = True

        colors = []

        filesize = getsize(filename)
        version, ncolors = struct.unpack('>2H', file.read(4))
        if version == 1 and filesize > 4 + ncolors*10 + 1: # Added 1 for the Focoltone library in Photoshop 5
            file.seek(4 + ncolors * 10)
            version, ncolors = struct.unpack('>2H', file.read(4))

        for i in range(ncolors):
            name = None
            color = Color()
            model = struct.unpack('>H',file.read(2))[0]
            if model == 2:
                c,m,y,k = struct.unpack('>4H', file.read(8))
                c,m,y,k = 1-float(c)/0xFFFF, 1-float(m)/0xFFFF, 1-float(y)/0xFFFF, 1-float(k)/0xFFFF
                color.setCMYK((c,m,y,k))
            elif model == 9:
                c,m,y,k = struct.unpack('>4H', file.read(8))
                c,m,y,k = float(c)/10000, float(m)/10000, float(y)/10000, float(k)/10000
                color.setCMYK((c,m,y,k))
            elif model == 0:
                r,g,b = struct.unpack('>3H', file.read(6))
                r,g,b = float(r)/0xFFFF, float(g)/0xFFFF, float(b)/0xFFFF
                color.setRGB1((r,g,b))
                file.seek(2, 1)
            elif model == 1:
                h,s,v = struct.unpack('>3H', file.read(6))
                h,s,v = float(h)/0xFFFF, float(s)/0xFFFF, float(v)/0xFFFF
                color.setHSV((h,s,v))
                file.seek(2, 1)
            elif model == 7: # Lab
                print("Lab model is not supported yet")
                file.seek(8, 1)
                continue
            elif model == 8:
                k = struct.unpack('>H',file.read(2))[0]
                k = float(k)/10000
                color.setRGB1((k,k,k))
            else:
                print("Unsupported color model #{}".format(model))
                file.seek(8,1)

            if version == 2:
                length = struct.unpack('>L',file.read(4))[0]
                if length > 0:
                    name = struct.unpack(str(length*2)+'s',file.read(length*2))[0]
                    name = unicode(name, 'utf_16_be').split('\x00', 1)[0]
            if version == 0: # Photoshop 6
                length = struct.unpack('B',file.read(1))[0]
                if length > 0:
                    name = file.read(length)

            if name:
                color.name = name

            colors.append(color)

        self.palette = create_palette(colors)
        self.palette.meta["Version"] = str(version)
        if filename:
            self.palette.name = basename(filename)

        if do_close:
            file.close()

        return self.palette

