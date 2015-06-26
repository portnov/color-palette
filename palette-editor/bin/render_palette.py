#!/usr/bin/python

import sys
from os.path import join, basename, dirname, splitext
import gettext
import argparse

gettext.install("colors", localedir="share/locale", unicode=True)

bindir = dirname(sys.argv[0])
rootdir = dirname(bindir)
sys.path.append(rootdir)

from palette.image import PaletteImage
from palette.storage.xml import XmlPalette
from dialogs.open_palette import load_palette

def parse_cmdline():
    parser = argparse.ArgumentParser(description="Render palette of any supported format to image file")
    parser.add_argument('input', metavar='FILENAME')
    parser.add_argument('-o', '--output', nargs=1, metavar='FILENAME', help='Specify output file name instead of <input_file_name>.png')
    parser.add_argument('-g', '--group', nargs=1, metavar='GROUP', help='Render specified group from MyPaint palette')
    parser.add_argument('-a', '--all', help='Render all groups from MyPaint palette')
    parser.add_argument('-i', '--indicate-modes', help='Indicate auto-generated colors with vertical/horizontal lines')
    return parser.parse_args()

def default_dst_filename(src):
    name, ext = splitext(src)
    return name + '.png'

def get_dst_filename(src, args, group=None):
    if args.all:
        dst = args.output
        name, ext = splitext(dst)
        return "{}_{}.{}".format(name, group, ext)
    elif args.output is not None:
        return args.output
    else:
        return default_dst_filename(src)

def render(srcfile, dstfile, args):
    palette = load_palette(srcfile)
    w,h = palette.ncols * 48, palette.nrows * 48
    image = PaletteImage(palette, indicate_modes=args.indicate_modes).get(w,h)
    image.save(dstfile)

args = parse_cmdline()

srcfile = args.input

if args.all:
    groups = XmlPalette.get_group_names()
    for grp in groups:
        dstfile = get_dst_filename(src, args, grp)
        render(srcfile, dstfile, args)
else:
    dstfile = get_dst_filename(srcfile, args, args.group)
    render(srcfile, dstfile, args)


