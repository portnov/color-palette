# coding: utf-8

from fnmatch import fnmatch
from os.path import exists

from l10n import _
from gimp import GimpPalette
from xml import XmlPalette
from paletton import Paletton
from css import *
from svg import SVG
from image import Image
from scribus import Scribus

storages = [GimpPalette, XmlPalette, Paletton, CSS, SVG, Image, Scribus]

def get_all_filters(save=False):
    result = ""
    for cls in storages:
        if save and not cls.can_save:
            continue
        if not save and not cls.can_load:
            continue
        result += u"{} ({});; ".format(cls.title, u" ".join(cls.filters))
    result += _("All files (*)")
    return result

def detect_storage(filename, save=False):
    for cls in storages:
        if save and not cls.can_save:
            continue
        if not save and not cls.can_load:
            continue
        if not any([fnmatch(filename, mask) for mask in cls.filters]):
            continue
        if exists(filename) and not cls.check(filename):
            continue
        return cls
    return None

