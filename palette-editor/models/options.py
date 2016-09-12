
from PyQt4 import QtGui, QtCore

from color import colors
from widgets.commands.general import *

class Options(object):
    def __init__(self, settings=None):
        # Mouse button to select color: default left
        self.select_button = QtCore.Qt.LeftButton
        # Mouse button to clear color (for swatches): default right
        self.clear_button  = QtCore.Qt.RightButton
        # Mouse button to toggle "user-defined" mark (for palette): default right
        self.mark_button   = QtCore.Qt.RightButton
        # Mouse button to call context menu: default no context menus
        self.menu_button   = None

        # Size of area under cursor to use - from 1x1 to say 15x15
        self.picker_area = 9
        # Whether to average color while moving cursor with mouse button held.
        self.picker_average = True

        self.color_history_size = 5

        self.settings = settings
        if settings is not None:
            self.restore(settings)

    def store(self, settings=None):
        if settings is None:
            settings = self.settings

        settings.setValue("input/select_button", self._button_to_int(self.select_button))
        settings.setValue("input/clear_button", self._button_to_int(self.clear_button))
        settings.setValue("input/mark_button", self._button_to_int(self.mark_button))
        settings.setValue("input/menu_button", self._button_to_int(self.menu_button))

        settings.setValue("picker/area_size", self.picker_area)
        settings.setValue("picker/average", self.picker_average)

    def _button_to_int(self, button):
        if button is not None:
            return int(button)
        else:
            return None

    def _variant_to_button(self, value):
        button, ok = value.toInt()
        if ok:
            if button is not None:
                result = QtCore.Qt.MouseButton(button)
            else:
                result = None
        else:
            result = None
        return result

    def restore(self, settings=None):
        if settings is None:
            settings = self.settings

        value = self._variant_to_button(settings.value("input/select_button"))
        if value:
            self.select_button = value
        value = self._variant_to_button(settings.value("input/clear_button"))
        if value:
            self.clear_button = value
        value = self._variant_to_button(settings.value("input/mark_button"))
        if value:
            self.mark_button = value
        value = self._variant_to_button(settings.value("input/menu_button"))
        if value:
            self.menu_button = value

        value, ok = settings.value("picker/area_size").toInt()
        if ok:
            self.picker_area = value
        self.picker_average = settings.value("picker/average").toBool()

