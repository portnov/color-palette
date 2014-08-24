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

def add_tool_button(parent, toolbar, icon_name, title, handler):
    if type(icon_name) == str:
        action = QtGui.QAction(QtGui.QIcon("./icons/"+icon_name), title, parent)
    elif icon_name is not None:
        action = QtGui.QAction(parent.style().standardIcon(icon_name), title, parent)
    else:
        action = QtGui.QAction(title, parent)
    toolbar.addAction(action)
    action.triggered.connect(handler)
    return action

class GUI(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.gui = GUIWidget(self)
        self.setCentralWidget(self.gui)

        #QtGui.QIcon.setThemeName('Tango')

        add_tool_button(self, self.gui.toolbar_swatches, "harmony.svg", "Harmony", self.gui.on_harmony)
        add_tool_button(self, self.gui.toolbar_swatches, "darken.png", "Darker", self.gui.on_swatches_darker)
        add_tool_button(self, self.gui.toolbar_swatches, "lighten.png", "Lighter", self.gui.on_swatches_lighter)
        add_tool_button(self, self.gui.toolbar_swatches, "saturate.png", "Saturate", self.gui.on_swatches_saturate)
        add_tool_button(self, self.gui.toolbar_swatches, "desaturate.png", "Desaturate", self.gui.on_swatches_desaturate)

        self.resize(800, 600)


def labelled(label, widget):
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(QtGui.QLabel(label))
    hbox.addWidget(widget)
    return hbox
    
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
                           ("Similar colors",harmonies.Similar),
                           ("Opposite colors RYB", harmonies.NHuesRYB(2)),
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

        self.palette = PaletteWidget(self, palette)
        self.palette.setMinimumSize(400,400)
        self.palette.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.palette.editing_enabled = False
        self.palette.selected.connect(self.on_select_from_palette)
        
        self.mixers = QtGui.QComboBox()
        self.mixers.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        for mixer, _ in self.available_mixers:
            self.mixers.addItem(mixer)
        self.mixers.currentIndexChanged.connect(self.on_select_mixer)
        #vbox_left.addLayout(labelled("Palette mixing mode:", self.mixers))
        vbox_left.addWidget(self.palette)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addLayout(vbox_left)

        add_tool_button(self, self.toolbar_palette, QtGui.QStyle.SP_DialogOpenButton, "Open palette", self.on_open_palette)
        add_tool_button(self, self.toolbar_palette, QtGui.QStyle.SP_DialogSaveButton, "Save palette", self.on_save_palette)
        toggle_edit = add_tool_button(self, self.toolbar_palette, "Gnome-colors-gtk-edit.svg", "Toggle edit mode", self.on_toggle_edit)
        toggle_edit.setCheckable(True)
        toggle_edit.setChecked(False)

        self.toolbar_palette.addWidget(QtGui.QLabel("Palette mixing mode:"))
        self.toolbar_palette.addWidget(self.mixers)

        vbox_center = QtGui.QVBoxLayout()
        grid = QtGui.QGridLayout()
        self.selector_mixers = QtGui.QComboBox()
        for mixer, _ in self.available_selector_mixers:
            self.selector_mixers.addItem(mixer)
        self.selector_mixers.currentIndexChanged.connect(self.on_select_selector_mixer)
        grid.addWidget(QtGui.QLabel("Selector model:"), 0, 0)
        grid.addWidget(self.selector_mixers, 0, 1)
        self.harmonies = QtGui.QComboBox() 
        for harmony, _ in self.available_harmonies:
            self.harmonies.addItem(harmony)
        self.harmonies.currentIndexChanged.connect(self.on_select_harmony)
        grid.addWidget(QtGui.QLabel("Harmony:"), 1, 0)
        grid.addWidget(self.harmonies, 1, 1)
        self.shaders = QtGui.QComboBox()
        for shader,_ in self.available_shaders:
            self.shaders.addItem(shader)
        self.shaders.currentIndexChanged.connect(self.on_select_shader)
        self.shader = harmonies.Saturation
        grid.addWidget(QtGui.QLabel("Shades:"), 2, 0)
        grid.addWidget(self.shaders, 2,1)

        vbox_center.addLayout(grid)

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
        
        self.toolbar_swatches = QtGui.QToolBar()
        vbox_center.addWidget(self.toolbar_swatches)

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
        self.hbox.addLayout(vbox_center)

        vbox_right = QtGui.QVBoxLayout()

        self.toolbar_template = QtGui.QToolBar()
        vbox_right.addWidget(self.toolbar_template)

        add_tool_button(self, self.toolbar_template, QtGui.QStyle.SP_DialogOpenButton, "Open template", self.on_open_template)
        add_tool_button(self, self.toolbar_template, QtGui.QStyle.SP_DialogSaveButton, "Save resulting SVG", self.on_save_template)
        add_tool_button(self, self.toolbar_template, "colorize_swatches.svg", "Colorize from swatches", self.on_colorize_harmony)
        add_tool_button(self, self.toolbar_template, "colorize_palette.svg", "Colorize from palette", self.on_colorize_palette)
        add_tool_button(self, self.toolbar_template, "View-refresh.svg", "Reset colors", self.on_reset_template)

        self.svg_colors = []
        label = QtGui.QLabel("Colors from original image:")
        label.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        vbox_right.addWidget(label)
        vbox_svg = QtGui.QVBoxLayout()
        idx = 0
        for j in range(3):
            hbox_svg = QtGui.QHBoxLayout()
            for j in range(7):
                w = TwoColorsWidget(self)
                w.setMaximumSize(30,30)
                w.second_color_set.connect(self.on_dst_color_set(idx))
                idx += 1
                hbox_svg.addWidget(w)
                self.svg_colors.append(w)
            vbox_svg.addLayout(hbox_svg)
        vbox_right.addLayout(vbox_svg)

        self.svg = SvgTemplateWidget(self)
        self.svg.setMinimumSize(400,400)
        self.svg.template_loaded.connect(self.on_template_loaded)
        self.svg.colors_matched.connect(self.on_colors_matched)
        self.svg.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.svg.loadTemplate("template.svg")
        self.svg.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        vbox_right.addWidget(self.svg)

        self.hbox.addLayout(vbox_right)

        self.setLayout(self.hbox)

    def on_dst_color_set(self, idx):
        def handler():
            self.svg.set_color(idx, self.svg_colors[idx].second_color)
        return handler

    def on_colors_matched(self):
        dst_colors = self.svg.get_dst_colors()
        n = len(self.svg_colors)
        for i, clr in enumerate(dst_colors[:n]):
            self.svg_colors[i]._second_color = clr
        self.update()

    def on_save_palette(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save palette", ".", "*.gpl")
        if filename:
            GimpPalette(self.palette.palette).save(str(filename))

    def on_open_palette(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open palette", ".", "*.gpl")
        if filename:
            self.palette.palette = GimpPalette().load(mixers.MixerRGB, str(filename))
            self.palette.selected_slot = None
            self.palette.redraw()
            self.update()

    def on_toggle_edit(self):
        self.palette.editing_enabled = not self.palette.editing_enabled
        self.update()

    def on_swatches_darker(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.darker(clr, 0.1)
            w.setColor(clr)
            w.update()

    def on_swatches_lighter(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.lighter(clr, 0.1)
            w.setColor(clr)
            w.update()

    def on_swatches_saturate(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.saturate(clr, 0.1)
            w.setColor(clr)
            w.update()

    def on_swatches_desaturate(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.desaturate(clr, 0.1)
            w.setColor(clr)
            w.update()

    def on_template_loaded(self):
        for i, clr in enumerate(self.svg.get_svg_colors()[:21]):
            #print(" #{} -> {}".format(i, str(clr)))
            self.svg_colors[i].setColor(clr)
        self.update()

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

    def on_open_template(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open SVG template", ".", "*.svg")
        if filename:
            self.svg.loadTemplate(str(filename))
    
    def on_save_template(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save SVG", ".", "*.svg")
        if filename:
            content = self.svg.get_svg()
            f = open(str(filename),'w')
            f.write(content)
            f.close()
    
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    w = GUI()
    w.show()
    sys.exit(app.exec_())

