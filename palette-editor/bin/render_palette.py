#!/usr/bin/python

import sys
from os.path import join, basename, dirname, abspath, exists
import gettext

gettext.install("colors", localedir="share/locale", unicode=True)

bindir = dirname(sys.argv[0])
rootdir = dirname(bindir)
sys.path.append(rootdir)

from palette.image import PaletteImage
from dialogs.open_palette import load_palette

srcfile = sys.argv[1]
dstfile = sys.argv[2]

palette = load_palette(srcfile)
w,h = palette.ncols * 48, palette.nrows * 48
image = PaletteImage(palette, indicate_modes=True).get(w,h)
image.save(dstfile)

