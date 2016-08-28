# coding: utf-8

from fnmatch import fnmatch
from os.path import exists

from gimp import GimpPalette
from xml import XmlPalette
from paletton import Paletton
from css import *
from svg import SVG
from image import Image
from scribus import Scribus
from ase import AsePalette
from aco import AcoPalette

storages = [GimpPalette, XmlPalette, Paletton, CSS, SVG, Image, Scribus, AsePalette, AcoPalette]

def get_storage_by_name(name):
    #print("Searching for storage named {}".format(name))
    for cls in storages:
        if cls.name == name:
            print("Using storage class {}".format(cls))
            return cls
    return None

def get_all_filters(save=False):
    result = ""
    for cls in storages:
        if save and not cls.can_save:
            continue
        if not save and not cls.can_load:
            continue
        result += cls.get_filter() + ";;"
    result += _("All files (*)")
    return result

def detect_storage(filename, save=False):
    for cls in storages:
        if save and not cls.can_save:
            continue
        if not save and not cls.can_load:
            continue
        if not any([fnmatch(filename.lower(), mask) for mask in cls.filters]):
            continue
        if exists(filename) and not cls.check(filename):
            continue
        return cls
    return None

def get_storage_name_by_filter(filter):
    for cls in storages:
        if cls.get_filter() == filter:
            return cls.name
    return None

