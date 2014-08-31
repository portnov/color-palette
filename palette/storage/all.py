
from gettext import gettext as _
from fnmatch import fnmatch
from os.path import exists

from gimp import GimpPalette
from xml import XmlPalette
from paletton import Paletton
from css import *

storages = [GimpPalette, XmlPalette, Paletton, CSS]

def get_all_filters(save=False):
    result = ""
    for cls in storages:
        if save and not cls.can_save:
            continue
        if not save and not cls.can_load:
            continue
        result += "{} ({});; ".format(cls.title, " ".join(cls.filters))
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

