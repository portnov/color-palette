#!/usr/bin/python

import sys
from os.path import join, basename, dirname, splitext
import gettext
import argparse

gettext.install("colors", localedir="share/locale", unicode=True)

bindir = dirname(sys.argv[0])
rootdir = dirname(bindir)
sys.path.insert(0,rootdir)

from palette.image import PaletteImage
from palette.storage.xml import XmlPalette
from dialogs.open_palette import load_palette, save_palette

def parse_cmdline():
    parser = argparse.ArgumentParser(description="Convert palettes between supported formats")
    parser.add_argument('input', metavar='FILENAME')
    parser.add_argument('-o', '--output', nargs=1, metavar='FILENAME', help='Specify output file name instead of <input_file_name>.png')
    parser.add_argument('-f', '--format', metavar='FORMAT', help='Use specified output format')
    parser.add_argument('-g', '--group', nargs=1, metavar='GROUP', help='Use specified group from MyPaint palette')
    parser.add_argument('-a', '--all', action='store_true', help='Use all groups from MyPaint palette')
    return parser.parse_args()

def default_dst_filename(src):
    name, ext = splitext(src)
    return unicode(name) + u'.png'

def get_dst_filename(src, args, group=None, idx=None):
    if args.all:
        dst = args.output
        if dst is not None:
            dst = dst[0]
        else:
            dst = src
        name, ext = splitext(dst)
        return u"{}_{}_{}{}".format(unicode(name,'utf-8'), idx, group, ext)
    elif args.output is not None:
        return unicode(args.output[0], 'utf-8')
    else:
        return default_dst_filename(src)

def convert(srcfile, dstfile, group=None, formatname=None):
    palette = load_palette(srcfile, options=group)
    save_palette(palette, dstfile, formatname=formatname)
    print(u"Writing {}".format(dstfile).encode('utf-8'))

args = parse_cmdline()

print args.format
srcfile = args.input

if args.all:
    groups = XmlPalette.get_group_names(srcfile)
    for idx, grp in enumerate(groups):
        dstfile = get_dst_filename(srcfile, args, unicode(grp), idx+1)
        convert(srcfile, dstfile, grp)
else:
    dstfile = get_dst_filename(srcfile, args, args.group)
    convert(srcfile, dstfile, formatname=args.format)


