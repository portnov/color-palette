#!/usr/bin/python

import sys
import numpy as np
from time import time
from pylab import imread
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.utils import shuffle

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

