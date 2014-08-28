
from gettext import gettext as _
from fnmatch import fnmatch

from gimp import GimpPalette

storages = [GimpPalette]

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
        if not cls.check(filename):
            continue
        return cls
    return None

