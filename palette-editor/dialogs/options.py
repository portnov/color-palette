# coding: utf-8

from PyQt4 import QtGui, QtCore

from color.colors import *
#from models.options import Options

class SelectButton(QtGui.QComboBox):
    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)

        self.addItem(_("Left button"))
        self.addItem(_("Middle button"))
        self.addItem(_("Right button"))
        self.addItem(_("Disable"))

    def get_button(self):
        idx = self.currentIndex()
        if idx == 3:
            return None
        else:
            return QtCore.Qt.MouseButton(idx)

    def set_button(self, button):
        if button == None:
            self.setCurrentIndex(3)
        else:
            idx = int(button)
            self.setCurrentIndex(idx)

class OptionsDialog(QtGui.QDialog):
    def __init__(self, options, *args, **kwargs):
        QtGui.QDialog.__init__(self, *args, **kwargs)

        self.options = options

        tabs = QtGui.QTabWidget(self)

        input_tab = QtGui.QWidget()
        layout = QtGui.QFormLayout()

        self.select_button = SelectButton(input_tab)
        layout.addRow(_("Select color with"), self.select_button)
        self.clear_button = SelectButton(input_tab)
        layout.addRow(_("Clear color with"), self.clear_button)
        self.mark_button = SelectButton(input_tab)
        layout.addRow(_("Toggle mark on color"), self.mark_button)
        self.menu_button = SelectButton(input_tab)
        layout.addRow(_("Show context menu on"), self.menu_button)

        input_tab.setLayout(layout)

        picker_tab = QtGui.QWidget()
        layout = QtGui.QFormLayout()

        self.picker_area = QtGui.QSpinBox(picker_tab)
        self.picker_area.setMinimum(1)
        self.picker_area.setMaximum(15)
        layout.addRow(_("Picker area size"), self.picker_area)
        self.picker_average = QtGui.QCheckBox(picker_tab)
        layout.addRow(_("Average color while mouse dragging"), self.picker_average)

        picker_tab.setLayout(layout)

        tabs.addTab(input_tab, _("Input"))
        tabs.addTab(picker_tab, _("Color picker"))
        
        buttons = QtGui.QHBoxLayout()
        buttons.addStretch(1)
        ok = QtGui.QPushButton(_("Ok"))
        ok.clicked.connect(self._on_ok)
        cancel = QtGui.QPushButton(_("&Cancel"))
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addLayout(buttons,1)
        self.setLayout(layout)

        self.setWindowTitle(_("Preferences"))

        self.load_settings()

    def _on_ok(self):
        self.save_settings()
        self.options.store()
        self.accept()

    def load_settings(self):

        self.select_button.set_button(self.options.select_button)
        self.clear_button.set_button(self.options.clear_button)
        self.mark_button.set_button(self.options.mark_button)
        self.menu_button.set_button(self.options.menu_button)

        self.picker_area.setValue(self.options.picker_area)

        if self.options.picker_average:
            self.picker_average.setCheckState(QtCore.Qt.Checked)
        else:
            self.picker_average.setCheckState(QtCore.Qt.Unchecked)

    def save_settings(self):
        self.options.select_button = self.select_button.get_button()
        self.options.clear_button = self.clear_button.get_button()
        self.options.mark_button = self.mark_button.get_button()
        self.options.menu_button = self.menu_button.get_button()

        self.options.picker_area = self.picker_area.value()
        self.options.picker_average = (self.picker_average.checkState() == QtCore.Qt.Checked)

