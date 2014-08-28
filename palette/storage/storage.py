
from os.path import join, basename

from color.colors import *
from color import mixers
from palette.palette import *

class Storage(object):
    def __init__(self, palette=None):
        self.palette = palette

    def load(self, mixer, file_r, *args, **kwargs):
        raise NotImplemented

    def save(self, file_w):
        raise NotImplemented

