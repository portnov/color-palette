
from gettext import gettext as _
from fnmatch import fnmatch
from os.path import exists

from gimp import GimpPalette
from xml import XmlPalette

storages = [GimpPalette, XmlPalette]

def get_all_filters():
    result = ""
    for cls in storages:
        result += "{} ({});; ".format(cls.title, " ".join(cls.filters))
    result += _("All files (*)")
    return result

def detect_storage(filename):
    for cls in storages:
        if not any([fnmatch(filename, mask) for mask in cls.filters]):
            continue
        if exists(filename) and not cls.check(filename):
            continue
        return cls
    return None

