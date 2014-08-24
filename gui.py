#!/usr/bin/python

import sys
import os
from os.path import join, basename, dirname
#from gettext import gettext as _
import gettext

from PyQt4 import QtGui

from widgets import *
import colors
from colors import Color
import mixers
import harmonies
from palette import Palette, GimpPalette, save_gpl
from palette_widget import PaletteWidget
from svg_widget import SvgTemplateWidget

def locate_icon(name):
    thisdir = dirname(sys.argv[0])
    return join(thisdir, "icons", name)

def locate_template(name):
    thisdir = dirname(sys.argv[0])
    return join(thisdir, "templates", name)

def locate_locales():
    thisdir = dirname(sys.argv[0])
    d = join(thisdir, "po")
    print("Using locales at " + d)
    return d

if sys.platform.startswith('win'):
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang

gettext.install("colors", localedir=locate_locales(), unicode=True)

def add_tool_button(parent, toolbar, icon_name, title, handler):
    if type(icon_name) == str:
        action = QtGui.QAction(QtGui.QIcon(locate_icon(icon_name)), title, parent)
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

        self.setWindowTitie(_("Palette editor"))
        self.resize(800, 600)


def labelled(label, widget):
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(QtGui.QLabel(label))
    hbox.addWidget(widget)
    return hbox
    
class GUIWidget(QtGui.QWidget):
    
    GRADIENT_SIZE=10
    
    available_mixers = [(_("RGB"), mixers.MixerRGB),
                        (_("HSV"), mixers.MixerHSV), 
                        (_("HLS"), mixers.MixerHLS), 
                        (_("CMYK"), mixers.MixerCMYK), 
                        (_("CMY"), mixers.MixerCMY), 
                        (_("RYB (experimental)"), mixers.MixerRYB),
                        (_("HSI (experimental)"), mixers.MixerHSI) ] + ([(_("LCh"), mixers.MixerLCh), 
                          (_("Lab"), mixers.MixerLab), 
                          (_("LCh Desaturate (experimental)"), mixers.MixerLChDesaturate)] if colors.use_lcms else [])
    
    available_selector_mixers = [(_("HLS"), mixers.MixerHLS),
                                 (_("RYB"), mixers.MixerRYB) ] + ([(_("LCh"), mixers.MixerLCh)] if colors.use_lcms else [])

    available_harmonies = [(_("Just opposite"), harmonies.Opposite),
                           (_("Three colors"),  harmonies.NHues(3)),
                           (_("Four colors"),   harmonies.NHues(4)),
                           (_("Similar colors"),harmonies.Similar),
                           (_("Opposite colors RYB"), harmonies.NHuesRYB(2)),
                           (_("Three colors RYB"), harmonies.NHuesRYB(3)),
                           (_("Four colors RYB"), harmonies.NHuesRYB(4)) ] + ([(_("Three colors LCh"),   harmonies.NHuesLCh(3)),
                            (_("Four colors LCh"),   harmonies.NHuesLCh(4))] if colors.use_lcms else [])

    available_shaders = [(_("Saturation"), harmonies.Saturation),
                         (_("Value"),      harmonies.Value),
                         (_("Warmer"),     harmonies.Warmer),
                         (_("Cooler"),     harmonies.Cooler) ]
    
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
        self.palette.setMinimumSize(300,300)
        self.palette.setMaximumSize(700,700)
        self.palette.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.palette.editing_enabled = False
        self.palette.selected.connect(self.on_select_from_palette)
        
        self.mixers = QtGui.QComboBox()
        self.mixers.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        for mixer, nothing in self.available_mixers:
            self.mixers.addItem(mixer)
        self.mixers.currentIndexChanged.connect(self.on_select_mixer)
        vbox_left.addLayout(labelled(_("Palette mixing model:"), self.mixers))
        vbox_left.addWidget(self.palette)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addLayout(vbox_left)

        add_tool_button(self, self.toolbar_palette, QtGui.QStyle.SP_DialogOpenButton, _("Open palette"), self.on_open_palette)
        add_tool_button(self, self.toolbar_palette, QtGui.QStyle.SP_DialogSaveButton, _("Save palette"), self.on_save_palette)
        add_tool_button(self, self.toolbar_palette, "darken.png", _("Darker"), self.on_palette_darker)
        add_tool_button(self, self.toolbar_palette, "lighten.png", _("Lighter"), self.on_palette_lighter)
        add_tool_button(self, self.toolbar_palette, "saturate.png", _("Saturate"), self.on_palette_saturate)
        add_tool_button(self, self.toolbar_palette, "desaturate.png", _("Desaturate"), self.on_palette_desaturate)
        toggle_edit = add_tool_button(self, self.toolbar_palette, "Gnome-colors-gtk-edit.png", _("Toggle edit mode"), self.on_toggle_edit)
        toggle_edit.setCheckable(True)
        toggle_edit.setChecked(False)

        vbox_center = QtGui.QVBoxLayout()
        grid = QtGui.QGridLayout()
        self.selector_mixers = QtGui.QComboBox()
        for mixer, nothing in self.available_selector_mixers:
            self.selector_mixers.addItem(mixer)
        self.selector_mixers.currentIndexChanged.connect(self.on_select_selector_mixer)
        grid.addWidget(QtGui.QLabel(_("Selector model:")), 0, 0)
        grid.addWidget(self.selector_mixers, 0, 1)
        self.harmonies = QtGui.QComboBox() 
        for harmony, nothing in self.available_harmonies:
            self.harmonies.addItem(harmony)
        self.harmonies.currentIndexChanged.connect(self.on_select_harmony)
        grid.addWidget(QtGui.QLabel(_("Harmony:")), 1, 0)
        grid.addWidget(self.harmonies, 1, 1)
        self.shaders = QtGui.QComboBox()
        for shader,nothing in self.available_shaders:
            self.shaders.addItem(shader)
        self.shaders.currentIndexChanged.connect(self.on_select_shader)
        self.shader = harmonies.Saturation
        grid.addWidget(QtGui.QLabel(_("Shades:")), 2, 0)
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

        add_tool_button(self, self.toolbar_swatches, "harmony.png", _("Harmony"), self.on_harmony)
        add_tool_button(self, self.toolbar_swatches, "darken.png", _("Darker"), self.on_swatches_darker)
        add_tool_button(self, self.toolbar_swatches, "lighten.png", _("Lighter"), self.on_swatches_lighter)
        add_tool_button(self, self.toolbar_swatches, "saturate.png", _("Saturate"), self.on_swatches_saturate)
        add_tool_button(self, self.toolbar_swatches, "desaturate.png", _("Desaturate"), self.on_swatches_desaturate)
        add_tool_button(self, self.toolbar_swatches, QtGui.QStyle.SP_DialogSaveButton, _("Save as palette"), self.on_swatches_save)

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

        add_tool_button(self, self.toolbar_template, QtGui.QStyle.SP_DialogOpenButton, _("Open template"), self.on_open_template)
        add_tool_button(self, self.toolbar_template, QtGui.QStyle.SP_DialogSaveButton, _("Save resulting SVG"), self.on_save_template)
        add_tool_button(self, self.toolbar_template, "colorize_swatches.png", _("Colorize from swatches"), self.on_colorize_harmony)
        add_tool_button(self, self.toolbar_template, "colorize_palette.png", _("Colorize from palette"), self.on_colorize_palette)
        add_tool_button(self, self.toolbar_template, "View-refresh.png", _("Reset colors"), self.on_reset_template)

        self.svg_colors = []
        label = QtGui.QLabel(_("Colors from original image:"))
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
        self.svg.loadTemplate(locate_template("template.svg"))
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
        filename = QtGui.QFileDialog.getSaveFileName(self, _("Save palette"), ".", "*.gpl")
        if filename:
            GimpPalette(self.palette.palette).save(str(filename))

    def on_open_palette(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, _("Open palette"), ".", "*.gpl")
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

    def on_palette_darker(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.darker(clr, 0.1)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_palette_lighter(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.lighter(clr, 0.1)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_palette_saturate(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.saturate(clr, 0.1)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_palette_desaturate(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.desaturate(clr, 0.1)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_template_loaded(self):
        for i, clr in enumerate(self.svg.get_svg_colors()[:21]):
            #print(" #{} -> {}".format(i, str(clr)))
            self.svg_colors[i].setColor(clr)
        self.update()

    def on_set_current_color(self):
        self.selector.setColor(self.current_color.getColor())

    def on_select_from_palette(self, row, col):
        color = self.palette.palette.getColor(row, col)
        print(_("Selected from palette: ") + str(color))

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
        filename = QtGui.QFileDialog.getOpenFileName(self, _("Open SVG template"), ".", "*.svg")
        if filename:
            self.svg.loadTemplate(str(filename))
    
    def on_save_template(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, _("Save SVG"), ".", "*.svg")
        if filename:
            content = self.svg.get_svg()
            f = open(str(filename),'w')
            f.write(content)
            f.close()
    
    def on_swatches_save(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, _("Save palette"), ".", "*.gpl")
        if filename:
            clrs = [w.getColor() for w in self.harmonized if w.getColor() is not None]
            save_gpl("Swatches", 5, clrs, str(filename))
    
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    w = GUI()
    w.show()
    sys.exit(app.exec_())

