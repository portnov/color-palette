#!/usr/bin/python

import sys

from PyQt4 import QtGui

from widgets import *
import colors
from colors import Color
import mixers
import harmonies
from palette import Palette, GimpPalette
from palette_widget import PaletteWidget
from svg_widget import SvgTemplateWidget

class GUI(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.gui = GUIWidget(self)
        self.setCentralWidget(self.gui)

        #QtGui.QIcon.setThemeName('Tango')

        self.add_tool_button(self.gui.toolbar_palette, QtGui.QStyle.SP_DialogOpenButton, "Open palette", self.on_open_palette)
        self.add_tool_button(self.gui.toolbar_palette, QtGui.QStyle.SP_DialogSaveButton, "Save palette", self.on_save_palette)

        self.add_tool_button(self.gui.toolbar_template, QtGui.QStyle.SP_DialogOpenButton, "Open template", self.on_open_template)
        self.add_tool_button(self.gui.toolbar_template, QtGui.QStyle.SP_DialogSaveButton, "Save resulting SVG", self.on_save_template)

        self.toggle_edit = QtGui.QAction(QtGui.QIcon.fromTheme('emblem-readonly'), "Toggle readonly mode", self)
        self.toggle_edit.setCheckable(True)
        self.toggle_edit.setChecked(True)
        self.gui.toolbar_palette.addAction(self.toggle_edit)
        self.toggle_edit.triggered.connect(self.on_toggle_edit)

        self.resize(800, 600)

    def add_tool_button(self, toolbar, icon_name, title, handler):
        action = QtGui.QAction(self.style().standardIcon(icon_name), title, self)
        toolbar.addAction(action)
        action.triggered.connect(handler)

    def on_save_palette(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save palette", ".", "*.gpl")
        if filename:
            GimpPalette(self.gui.palette.palette).save(str(filename))

    def on_open_palette(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open palette", ".", "*.gpl")
        if filename:
            self.gui.palette.palette = GimpPalette().load(mixers.MixerRGB, str(filename))
            self.gui.palette.selected_slot = None
            self.gui.palette.redraw()
            self.gui.update()

    def on_toggle_edit(self):
        self.gui.palette.editing_enabled = not self.gui.palette.editing_enabled
        self.gui.update()

    def on_open_template(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open SVG template", ".", "*.svg")
        if filename:
            self.gui.svg.loadTemplate(str(filename))
    
    def on_save_template(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save SVG", ".", "*.svg")
        if filename:
            content = self.gui.svg.get_svg()
            f = open(str(filename),'w')
            f.write(content)
            f.close()
    
class GUIWidget(QtGui.QWidget):
    
    GRADIENT_SIZE=10
    
    available_mixers = [("RGB", mixers.MixerRGB),
                        ("HSV", mixers.MixerHSV), 
                        ("HLS", mixers.MixerHLS), 
                        ("CMYK", mixers.MixerCMYK), 
                        ("CMY", mixers.MixerCMY), 
                        ("RYB (experimental)", mixers.MixerRYB),
                        ("HSI (experimental)", mixers.MixerHSI) ] + ([("LCh", mixers.MixerLCh), 
                          ("Lab", mixers.MixerLab), 
                          ("LCh Desaturate", mixers.MixerLChDesaturate)] if colors.use_lcms else [])
    
    available_selector_mixers = [("HLS", mixers.MixerHLS),
                                 ("RYB", mixers.MixerRYB) ] + ([("LCh", mixers.MixerLCh)] if colors.use_lcms else [])

    available_harmonies = [("Just opposite", harmonies.Opposite),
                           ("Three colors",  harmonies.NHues(3)),
                           ("Four colors",   harmonies.NHues(4)),
                           ("Three colors RYB", harmonies.NHuesRYB(3)),
                           ("Four colors RYB", harmonies.NHuesRYB(4)) ] + ([("Three colors LCh",   harmonies.NHuesLCh(3)),
                            ("Four colors LCh",   harmonies.NHuesLCh(4))] if colors.use_lcms else [])

    available_shaders = [("Saturation", harmonies.Saturation),
                         ("Value",      harmonies.Value),
                         ("Warmer",     harmonies.Warmer),
                         ("Cooler",     harmonies.Cooler) ]
    
    def __init__(self,*args):
        QtGui.QWidget.__init__(self, *args)

        self.mixer = mixers.MixerRGB

        vbox_left = QtGui.QVBoxLayout()

        self.toolbar_palette = QtGui.QToolBar()
        vbox_left.addWidget(self.toolbar_palette)

        palette = Palette(self.mixer, 7, 7)
        palette.paint(0, 0, Color(255.0, 0.0, 0.0))
        palette.paint(0, 6, Color(0.0, 0.0, 0.0))
        palette.paint(6, 0, Color(255.0, 255.0, 255.0))
        palette.paint(6, 6, Color(0.0, 255.0, 0.0))
        palette.recalc()

        self.palette = PaletteWidget(palette)
        self.palette.setMinimumSize(500,500)
        self.palette.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.palette.editing_enabled = False
        self.palette.selected.connect(self.on_select_from_palette)
        
        self.mixers = QtGui.QComboBox()
        self.mixers.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        for mixer, _ in self.available_mixers:
            self.mixers.addItem(mixer)
        self.mixers.currentIndexChanged.connect(self.on_select_mixer)
        vbox_left.addWidget(self.mixers)
        vbox_left.addWidget(self.palette)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addLayout(vbox_left)

        vbox_center = QtGui.QVBoxLayout()
        self.selector_mixers = QtGui.QComboBox()
        for mixer, _ in self.available_selector_mixers:
            self.selector_mixers.addItem(mixer)
        self.selector_mixers.currentIndexChanged.connect(self.on_select_selector_mixer)
        vbox_center.addWidget(self.selector_mixers)
        self.harmonies = QtGui.QComboBox() 
        for harmony, _ in self.available_harmonies:
            self.harmonies.addItem(harmony)
        self.harmonies.currentIndexChanged.connect(self.on_select_harmony)
        vbox_center.addWidget(self.harmonies)
        self.shaders = QtGui.QComboBox()
        for shader,_ in self.available_shaders:
            self.shaders.addItem(shader)
        self.shaders.currentIndexChanged.connect(self.on_select_shader)
        self.shader = harmonies.Saturation
        vbox_center.addWidget(self.shaders)

        self.selector = Selector(mixers.MixerHLS)
        self.selector.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.selector.setMinimumSize(300,300)
        self.selector.setMaximumSize(500,500)
        self.selector.setHarmony(harmonies.Opposite)
        self.selector.selected.connect(self.on_select_color)
        vbox_center.addWidget(self.selector)

        self.current_color = ColorWidget(self)
        self.current_color.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.current_color.setMaximumSize(100,100)
        self.current_color.selected.connect(self.on_set_current_color)
        vbox_center.addWidget(self.current_color)

        self.harmonized = []
        self.harmonizedBox = QtGui.QVBoxLayout()
        for j in range(4):
            hbox = QtGui.QHBoxLayout()
            for i in range(5):
                w = ColorWidget(self)
                w.setMaximumSize(50,50)
                self.harmonized.append(w)
                hbox.addWidget(w)
            self.harmonizedBox.addLayout(hbox)

        vbox_center.addLayout(self.harmonizedBox)
        do_harmony = QtGui.QPushButton("Harmony")
        vbox_center.addWidget(do_harmony)
        do_harmony.clicked.connect(self.on_harmony)
        self.hbox.addLayout(vbox_center)

        vbox_right = QtGui.QVBoxLayout()

        self.toolbar_template = QtGui.QToolBar()
        vbox_right.addWidget(self.toolbar_template)

        self.svg = SvgTemplateWidget(self)
        self.svg.setMinimumSize(500,500)
        self.svg.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.svg.loadTemplate("template.svg")
        self.svg.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        vbox_right.addWidget(self.svg)

        do_color_harmony = QtGui.QPushButton("Colorize from swatches")
        vbox_right.addWidget(do_color_harmony)
        do_color_harmony.clicked.connect(self.on_colorize_harmony)

        do_color_palette = QtGui.QPushButton("Colorize from palette")
        vbox_right.addWidget(do_color_palette)
        do_color_palette.clicked.connect(self.on_colorize_palette)

        reset_temploate = QtGui.QPushButton("Reload image")
        vbox_right.addWidget(reset_temploate)
        reset_temploate.clicked.connect(self.on_reset_template)

        self.hbox.addLayout(vbox_right)

        self.setLayout(self.hbox)

    def on_set_current_color(self):
        self.selector.setColor(self.current_color.getColor())

    def on_select_from_palette(self, row, col):
        color = self.palette.palette.getColor(row, col)
        print("Selected from palette: " + str(color))

    def on_select_color(self):
        color = self.selector.selected_color
        self.current_color.setColor(color)
        self.current_color.update()

    def on_select_harmony(self, idx):
        _, harmony = self.available_harmonies[idx]
        print("Selected harmony: " + str(harmony))
        self.selector.setHarmony(harmony)

    def on_select_shader(self, idx):
        _, shader = self.available_shaders[idx]
        print("Selected shader: " + str(shader))
        self.shader = shader
    
    def on_select_mixer(self, idx):
        _,  self.mixer = self.available_mixers[idx]
        print("Selected mixer: " + str(self.mixer))
        self.palette.setMixer(self.mixer)
    
    def on_select_selector_mixer(self, idx):
        _,  mixer = self.available_selector_mixers[idx]
        print("Selected selector mixer: " + str(mixer))
        self.selector.setMixer(mixer)
    
    def on_mix(self):
        c1 = self.color1.getColor()
        c2 = self.color2.getColor()
        q = 0
        for i in range(self.GRADIENT_SIZE):
            q += 1.0/self.GRADIENT_SIZE
            clr = self.mixer.mix(c1, c2, q)
            #print(str(clr))
            self.results[i].setColor(clr)
        self.update()

    def on_harmony(self):
        for i,clr in enumerate(harmonies.allShades(self.selector.harmonized, self.shader)):
            if i > 19:
                break
            self.harmonized[i].setColor(clr)
        self.update()

    def on_colorize_harmony(self):
        self.svg.setColors([w.getColor() for w in self.harmonized])
        self.update()

    def on_colorize_palette(self):
        xs = self.palette.palette.getColors()
        self.svg.setColors(sum(xs,[]))
        self.update()

    def on_reset_template(self):
        self.svg.resetColors()
        self.update()
    
    
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    w = GUI()
    w.show()
    sys.exit(app.exec_())

