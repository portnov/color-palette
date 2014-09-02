
import sys
import os
import gettext
from os.path import join, basename, dirname, abspath

def locate_locales():
    thisdir = dirname(sys.argv[0])
    d = abspath( join(thisdir, "po") )
    print("Using locales at " + d)
    return d

if sys.platform.startswith('win'):
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang

t = gettext.translation("colors", localedir=locate_locales())
_ = t.ugettext

