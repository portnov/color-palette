
from os.path import join, basename
from PyQt4 import QtGui
from lxml import etree as ET

from color.colors import *
from color import mixers
from palette.storage.storage import *

class XmlPalette(Storage):
    title = _("MyPaint palette")
    filters = ["*.xml"]
    can_load = True
    can_save = False

    @staticmethod
    def check(filename):
        return ET.parse(filename).getroot().tag == 'colors'

    @staticmethod
    def get_options_widget(dialog, filename):

        def on_group_changed(selector):
            def handler():
                dialog.options = selector.currentText()
                dialog.on_current_changed(filename)
            return handler

        widget = QtGui.QWidget()
        box = QtGui.QHBoxLayout()
        label = QtGui.QLabel(_("Group: "))
        selector = QtGui.QComboBox()

        xml = ET.parse(filename)
        for xmlgrp in xml.xpath("//group"):
            xml_label = xmlgrp.find('label')
            if xml_label is not None:
                selector.addItem(xml_label.text)

        selector.currentIndexChanged.connect(on_group_changed(selector))
        selector.setCurrentIndex(0)

        box.addWidget(label)
        box.addWidget(selector)
        widget.setLayout(box)
        return widget

    def save(self, file_w=None):
        pass

    def load(self, mixer, file_r, group_name):

        def find_group(xml):
            #print("Searching {}".format(group_name))
            grp = None
            for xmlgrp in xml.xpath("//group"):
                xml_label = xmlgrp.find('label')
                if xml_label is None:
                    continue
                #print("Found {}".format(xml_label.text))
                if group_name is None or xml_label.text == group_name:
                    grp = xmlgrp
                    break
            return grp

        self.palette = Palette(mixer)
        self.palette.ncols = None
        xml = ET.parse(file_r)
        grp = find_group(xml)
        layout = grp.find('layout')
        if layout is not None:
            self.palette.ncols = int( layout.attrib['columns'] )

        all_slots = []
        n_colors = 0
        for xmlclr in grp.findall('color'):
            sRGB = xmlclr.find('sRGB')
            if sRGB is None:
                continue
            attrs = sRGB.attrib
            r = float(attrs['r'].replace(',','.'))
            g = float(attrs['g'].replace(',','.'))
            b = float(attrs['b'].replace(',','.'))
            clr = Color()
            clr.setRGB1((r,g,b))
            slot = Slot(clr)
            all_slots.append(slot)
            n_colors += 1

        if n_colors < DEFAULT_GROUP_SIZE:
            self.palette.ncols = n_colors
        if not self.palette.ncols:
            if n_colors > MAX_COLS:
                self.palette.ncols = MAX_COLS
            else:
                self.palette.ncols = n_colors
        self.palette.setSlots(all_slots)
        print("Loaded palette: {}x{}".format( self.palette.nrows, self.palette.ncols ))
        return self.palette

