#!/usr/bin/python

import sys

from PyQt4 import QtGui

from widgets import *
import colors
import mixers
import harmonies
    
class GUI(QtGui.QWidget):
    
    GRADIENT_SIZE=10
    
    available_mixers = [("RGB", mixers.MixerRGB),
                        ("RYB", mixers.MixerRYB),
                        ("HLS", mixers.MixerHLS), 
                        ("Lab", mixers.MixerLab), 
                        ("LCh", mixers.MixerLCh), 
                        ("LCh Desaturate", mixers.MixerLChDesaturate), 
                        ("CMYK", mixers.MixerCMYK), 
                        ("CMY", mixers.MixerCMY), 
                        ("HSI", mixers.MixerHSI)]
    
    available_selector_mixers = [("HLS", mixers.MixerHLS), ("LCh", mixers.MixerLCh) ]

    available_harmonies = [("Just opposite", harmonies.Opposite),
                           ("Three colors",  harmonies.NHues(3)),
                           ("Four colors",   harmonies.NHues(4)),
                           ("Simple LCh",    harmonies.SimpleHarmony)]
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.vbox_left = QtGui.QVBoxLayout()
        self.colors1 = QtGui.QHBoxLayout()
        self.color1 = ColorWidget(self)
        self.color1.selected.connect(self.on_select(self.color1, 1))
        self.color2 = ColorWidget(self)
        self.color2.selected.connect(self.on_select(self.color2, 2))
        self.color3 = ColorWidget(self)
        self.color3.selected.connect(self.on_select(self.color3, 3))
        self.color4 = ColorWidget(self)
        self.color4.selected.connect(self.on_select(self.color4, 4))
        
        self.colors1.addWidget(self.color1)
        self.colors1.addWidget(self.color2)
        
        self.colors2 = QtGui.QHBoxLayout()
        self.colors2.addWidget(self.color3)
        self.colors2.addWidget(self.color4)
        
        self.mixers = QtGui.QComboBox()
        for mixer, _ in self.available_mixers:
            self.mixers.addItem(mixer)
        self.mixers.currentIndexChanged.connect(self.on_select_mixer)
        self.vbox_left.addWidget(self.mixers)
        self.vbox_left.addLayout(self.colors1)
        self.vbox_left.addLayout(self.colors2)
        self.gradient = QtGui.QHBoxLayout()
        self.results = []
        for i in range(self.GRADIENT_SIZE):
            w = ColorWidget(self)
            self.results.append(w)
            self.gradient.addWidget(w)
        self.vbox_left.addLayout(self.gradient)
        self.mixer = mixers.MixerRGB
        self.gw = GradientWidget(Gradient(self.mixer))
        self.vbox_left.addWidget(self.gw)
        self.button = QtGui.QPushButton("Mix!")
        self.button.clicked.connect(self.on_mix)
        self.vbox_left.addWidget(self.button)
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
        self.selector = Selector(mixers.MixerHLS)
        self.selector.setHarmony(harmonies.Opposite)
        self.selector.selected.connect(self.on_select_color)
        self.vbox_right.addWidget(self.selector)
        self.harmonized = []
        self.harmonizedBox = QtGui.QHBoxLayout()
        for i in range(10):
            w = ColorWidget(self)
            self.harmonized.append(w)
            self.harmonizedBox.addWidget(w)
        self.vbox_right.addLayout(self.harmonizedBox)
        self.do_harmony = QtGui.QPushButton("Harmony")
        self.vbox_right.addWidget(self.do_harmony)
        self.do_harmony.clicked.connect(self.on_harmony)
        self.hbox.addLayout(self.vbox_right)
        self.setLayout(self.hbox)
    
    def on_select_color(self):
        color = self.selector.selected_color
        self.harmonized[9].setColor(color)
        self.harmonized[9].update()

    def on_select_harmony(self, idx):
        _, harmony = self.available_harmonies[idx]
        print("Selected harmony: " + str(harmony))
        self.selector.setHarmony(harmony)
    
    def on_select(self, colorwidget, idx):
        def handler():
            color = colorwidget.getColor()
            self.gw.setColor(idx, color)
        return handler
    
    def on_select_mixer(self, idx):
        _,  self.mixer = self.available_mixers[idx]
        print("Selected mixer: " + str(self.mixer))
        self.gw.setMixer(self.mixer)
    
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
        for i,clr in enumerate(self.selector.harmonized):
            if i > 9:
                break
            self.harmonized[i].setColor(clr)
        self.update()
    
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    w = GUI()
    w.show()
    sys.exit(app.exec_())

