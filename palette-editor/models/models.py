
from PyQt4 import QtGui, QtCore

from color import colors
from widgets.commands.general import *

class Document(object):
    def __init__(self, window, options):
        self.window = window
        self.undoStack = QtGui.QUndoStack(window)
        self.options = options

        self.current_color = ColorModel(self)

        self.scratchpad = ScratchpadModel(self)

        self.swatches = [[ColorModel(self) for i in range(5)] for j in range(5)]

        self.svg_colors = [[ColorModel(self) for i in range(7)] for j in range(3)]

    def get_undo_stack(self):
        return self.undoStack

class Clipboard(object):
    def __init__(self, get_color, set_color):
        self.get_color = get_color
        self.set_color = set_color

    def _copy_text(self, text):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(text)

    def _copy_color(self):
        color = self.get_color()
        if color:
            clipboard = QtGui.QApplication.clipboard()
            qcolor = color.asQColor()
            mime = QtCore.QMimeData()
            mime.setColorData(qcolor)
            clipboard.setMimeData(mime)

    def _copy_color_text(self, get_text):
        #print "copy_color_text"
        color = self.get_color()
        if color:
            text = get_text(color)
            self._copy_text(text)

    def _copy_hex_text(self):
        #print "copy hex text"
        self._copy_color_text(lambda clr: clr.hex())

    def _copy_rgb_text(self):
        self._copy_color_text(lambda clr: clr.getRgbString())

    def _copy_hsv_text(self):
        self._copy_color_text(lambda clr: clr.getHsvString())

    def _paste_color(self):
        clipboard = QtGui.QApplication.clipboard()
        if clipboard.mimeData().hasColor():
            qcolor = QtGui.QColor(clipboard.mimeData().colorData())
            r,g,b,_ = qcolor.getRgb()
            color = Color(r,g,b)
            self.set_color(color)
        else:
            print("No color in clipboard")

    def add_cliboard_actions(self, menu, set_enabled):
        copy = menu.addAction(_("Copy color"))
        copy.triggered.connect(self._copy_color)
        if set_enabled:
            paste = menu.addAction(_("Paste color"))
            paste.triggered.connect(self._paste_color)
        copy_hex = menu.addAction(_("Copy hexadecimal representation"))
        copy_hex.triggered.connect(self._copy_hex_text)
        copy_rgb = menu.addAction(_("Copy RGB representation"))
        copy_rgb.triggered.connect(self._copy_rgb_text)
        copy_hsv = menu.addAction(_("Copy HSV representation"))
        copy_hsv.triggered.connect(self._copy_hsv_text)

class ScratchpadModel(object):
    def __init__(self, parent):
        self.parent = parent
        self.colors = []
        self.options = parent.options

    def get_undo_stack(self):
        return self.parent.get_undo_stack()

class ColorModel(QtCore.QObject):
    def __init__(self, parent, color=None):
        QtCore.QObject.__init__(self)
        self.parent = parent
        self.color = color
        self.set_color_enabled = True
        self.clipboard = Clipboard(self.getColor, self._set_color)
        self.options = parent.options

    def to_set_color(self):
        return self.set_color_enabled

    def get_undo_stack(self):
        return self.parent.get_undo_stack()

    def get_tooltip(self):
        if self.color is None:
            return None
        return self.color.verbose()

    def getColor(self):
        return self.color

    def setColor(self, color):
        command = SetColor(self, color)
        self.command(command)

    def clear(self):
        command = Clear(self)
        self.command(command)

    def command(self, cmd):
        self.get_undo_stack().push(cmd)

    def get_context_menu(self, widget):
        menu = QtGui.QMenu(widget)
        clear = menu.addAction(_("Clear"))
        clear.triggered.connect(self.clear)
        self.clipboard.add_cliboard_actions(menu, True)
        return menu
    
    def _set_color(self, color):
        self.command(SetColor(self, color))

    def rotate_color(self, x):
        command = ChangeColor(self, _("rotating color"),
                                lambda c : colors.increment_hue(c, x))
        self.command(command)

    def lighter(self, x):
        command = ChangeColor(self, _("changing color lightness"),
                                 lambda c : colors.lighter(c, x))
        self.command(command)

    def saturate(self, x):
        command = ChangeColor(self, _("changing color saturation"),
                                 lambda c : colors.saturate(c, x))
        self.command(command)



