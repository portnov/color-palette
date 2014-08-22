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
        self.toolbar = self.addToolBar('Main')

        QtGui.QIcon.setThemeName('Tango')

        self.open = QtGui.QAction(QtGui.QIcon.fromTheme('document-open'), "Open palette", self)
        self.toolbar.addAction(self.open)
        self.open.triggered.connect(self.on_open)

        self.save = QtGui.QAction(QtGui.QIcon.fromTheme('document-save'), "Save palette", self)
        self.toolbar.addAction(self.save)
        self.save.triggered.connect(self.on_save)

        self.toggle_edit = QtGui.QAction(QtGui.QIcon.fromTheme('emblem-readonly'), "Toggle readonly mode", self)
        self.toggle_edit.setCheckable(True)
        self.toggle_edit.setChecked(True)
        self.toolbar.addAction(self.toggle_edit)
        self.toggle_edit.triggered.connect(self.on_toggle_edit)

        self.resize(800, 600)

    def on_save(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save palette", ".", "*.gpl")
        if filename:
            GimpPalette(self.gui.palette.palette).save(str(filename))

    def on_open(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open palette", ".", "*.gpl")
        if filename:
            self.gui.palette.palette = GimpPalette().load(mixers.MixerRGB, str(filename))
            self.gui.palette.selected_slot = None
            self.gui.palette.redraw()
            self.gui.update()

    def on_toggle_edit(self):
        self.gui.palette.editing_enabled = not self.gui.palette.editing_enabled
        self.gui.update()
    
    
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

        self.vbox_left = QtGui.QVBoxLayout()

        palette = Palette(self.mixer, 7, 7)
        palette.paint(0, 0, Color(255.0, 0.0, 0.0))
        palette.paint(0, 6, Color(0.0, 0.0, 0.0))
        palette.paint(6, 0, Color(255.0, 255.0, 255.0))
        palette.paint(6, 6, Color(0.0, 255.0, 0.0))
        palette.recalc()

        self.palette = PaletteWidget(palette)
        self.palette.editing_enabled = False
        self.palette.selected.connect(self.on_select_from_palette)
        
        self.mixers = QtGui.QComboBox()
        for mixer, _ in self.available_mixers:
            self.mixers.addItem(mixer)
        self.mixers.currentIndexChanged.connect(self.on_select_mixer)
        self.vbox_left.addWidget(self.mixers)
        self.vbox_left.addWidget(self.palette)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addLayout(self.vbox_left)

        self.vbox_right = QtGui.QVBoxLayout()
        self.selector_mixers = QtGui.QComboBox()
        for mixer, _ in self.available_selector_mixers:
            self.selector_mixers.addItem(mixer)
        self.selector_mixers.currentIndexChanged.connect(self.on_select_selector_mixer)
        self.vbox_right.addWidget(self.selector_mixers)
        self.harmonies = QtGui.QComboBox() 
        for harmony, _ in self.available_harmonies:
            self.harmonies.addItem(harmony)
        self.harmonies.currentIndexChanged.connect(self.on_select_harmony)
        self.vbox_right.addWidget(self.harmonies)
        self.shaders = QtGui.QComboBox()
        for shader,_ in self.available_shaders:
            self.shaders.addItem(shader)
        self.shaders.currentIndexChanged.connect(self.on_select_shader)
        self.shader = harmonies.Saturation
        self.vbox_right.addWidget(self.shaders)

        self.selector = Selector(mixers.MixerHLS)
        self.selector.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.selector.setMinimumSize(300,300)
        self.selector.setHarmony(harmonies.Opposite)
        self.selector.selected.connect(self.on_select_color)
        self.vbox_right.addWidget(self.selector)

        self.current_color = ColorWidget(self)
        self.current_color.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.current_color.setMaximumSize(100,100)
        self.current_color.selected.connect(self.on_set_current_color)
        self.vbox_right.addWidget(self.current_color)

        self.harmonized = []
        self.harmonizedBox = QtGui.QVBoxLayout()
        harmonizedHBox1 = QtGui.QHBoxLayout()
        harmonizedHBox2 = QtGui.QHBoxLayout()
        for i in range(10):
            w = ColorWidget(self)
            w.setMaximumSize(50,50)
            self.harmonized.append(w)
            harmonizedHBox1.addWidget(w)
        for i in range(10):
            w = ColorWidget(self)
            w.setMaximumSize(50,50)
            self.harmonized.append(w)
            harmonizedHBox2.addWidget(w)
        self.harmonizedBox.addLayout(harmonizedHBox1)
        self.harmonizedBox.addLayout(harmonizedHBox2)
        self.vbox_right.addLayout(self.harmonizedBox)
        self.do_harmony = QtGui.QPushButton("Harmony")
        self.vbox_right.addWidget(self.do_harmony)
        self.do_harmony.clicked.connect(self.on_harmony)
        self.hbox.addLayout(self.vbox_right)

        self.svg = SvgTemplateWidget(self)
        self.svg.setMinimumSize(300,300)
        self.svg.loadTemplate("template2.svg")
        self.svg.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.hbox.addWidget(self.svg)
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
        self.svg.setColors([w.getColor() for w in self.harmonized])
        self.update()
    
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    w = GUI()
    w.show()
    sys.exit(app.exec_())

