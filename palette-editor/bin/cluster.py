#!/usr/bin/python

import sys
from os.path import dirname, abspath, join
import numpy as np
from time import time
from pylab import imread
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.utils import shuffle
import gettext

bindir = dirname(sys.argv[0])
rootdir = dirname(bindir)
sys.path.append(rootdir)

def locate_locales():
    d = abspath( join(rootdir, "share", "locale") )
    if sys.platform.startswith('win'):
        if not exists(d):
            d = abspath( join(bindir, "share", "locale") )
    print("Using locales at " + d)
    return d

if sys.platform.startswith('win'):
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang

gettext.install("colors", localedir=locate_locales(), unicode=True)

from color.colors import *
from palette.palette import *
from palette.storage.storage import *
from palette.storage.all import *
from palette.storage.cluster import get_common_colors
from dialogs.open_palette import save_palette

if len(sys.argv) != 3:
    print("Synopsis: cluster.py input.png output.gpl")
    print("  Extracts most common colors from image to palette.")
    sys.exit(1)

filename = sys.argv[1]
dstfile = sys.argv[2]

colors = get_common_colors(filename)

palette = create_palette(colors)
save_palette(palette, dstfile)

