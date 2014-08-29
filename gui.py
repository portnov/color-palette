#!/usr/bin/python

import sys
import os
from os.path import join, basename, dirname
#from gettext import gettext as _
import gettext

from PyQt4 import QtGui

sys.path.append(dirname(sys.argv[0]))

from widgets.widgets import *
from color import colors, mixers, harmonies
from color.colors import Color
from palette.palette import Palette
from palette.widget import PaletteWidget
from palette.image import PaletteImage
from matching.svg_widget import SvgTemplateWidget
from dialogs.open_palette import *

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

def compose_icon(icon, filename):
    icon_pixmap = icon.pixmap(24,24)
    qp = QtGui.QPainter(icon_pixmap)
    image = QtGui.QImage(locate_icon(filename))
    qp.drawImage(0, 0, image)
    qp.end()
    return QtGui.QIcon(icon_pixmap)

def create_action(parent, toolbar, menu, icon, title, handler):
    if type(icon) == str:
        action = QtGui.QAction(QtGui.QIcon(locate_icon( icon)), title, parent)
    elif type(icon) == QtGui.QIcon:
        action = QtGui.QAction(icon, title, parent)
    elif icon is not None:
        action = QtGui.QAction(parent.style().standardIcon(icon), title, parent)
    else:
        action = QtGui.QAction(title, parent)
    toolbar.addAction(action)
    menu.addAction(action)
    action.triggered.connect(handler)
    return action

class GUI(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.gui = GUIWidget(self)

        self._init_palette_actions()
        self._init_harmonies_actions()
        self._init_svg_actions()

        self.setCentralWidget(self.gui)

        self.setWindowTitle(_("Palette editor"))
        self.resize(800, 600)

    def _init_palette_actions(self):
        menu = self.menuBar().addMenu(_("&Palette"))
        open_palette = create_action(self, self.gui.toolbar_palette, menu,
                QtGui.QStyle.SP_DialogOpenButton,
                _("&Open palette"), self.gui.on_open_palette)
        create_action(self, self.gui.toolbar_palette, menu,
                QtGui.QStyle.SP_DialogSaveButton,
                _("&Save palette"), self.gui.on_save_palette)
        icon = compose_icon(self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton), "palette_small.png")
        create_action(self, self.gui.toolbar_palette, menu,
                icon, _("Save palette as &image"), self.gui.on_save_palette_image)
        menu.addSeparator()
        self.gui.toolbar_palette.addSeparator()
        toggle_edit = create_action(self, self.gui.toolbar_palette, menu,
                "Gnome-colors-gtk-edit.png",
                _("Toggle edit &mode"), self.gui.on_toggle_edit)
        toggle_edit.setCheckable(True)
        toggle_edit.setChecked(False)
        menu.addSeparator()
        self.gui.toolbar_palette.addSeparator()
        create_action(self, self.gui.toolbar_palette, menu,
                "darken.png", _("&Darker"), self.gui.on_palette_darker)
        create_action(self, self.gui.toolbar_palette, menu,
                "lighten.png", _("&Lighter"), self.gui.on_palette_lighter)
        create_action(self, self.gui.toolbar_palette, menu,
                "saturate.png", _("S&aturate"), self.gui.on_palette_saturate)
        create_action(self, self.gui.toolbar_palette, menu,
                "desaturate.png", _("D&esaturate"), self.gui.on_palette_desaturate)
        create_action(self, self.gui.toolbar_palette, menu,
                "hue-counterclockwise.png",
                _("&Rotate colors counterclockwise"), self.gui.on_palette_counterclockwise)
        create_action(self, self.gui.toolbar_palette, menu,
                "hue-clockwise.png",
                _("Rotate colors clock&wise"), self.gui.on_palette_clockwise)
        create_action(self, self.gui.toolbar_palette, menu,
                "contrast-up.png", _("Increase &contrast"), self.gui.on_palette_contrast_up)
        create_action(self, self.gui.toolbar_palette, menu,
                "contrast-down.png", _("Decrease contras&t"), self.gui.on_palette_contrast_down)

    def _init_harmonies_actions(self):
        menu = self.menuBar().addMenu(_("&Swatches"))
        create_action(self, self.gui.toolbar_swatches, menu,
                "harmony.png", _("&Harmony"), self.gui.on_harmony)
        menu.addSeparator()
        self.gui.toolbar_swatches.addSeparator()
        create_action(self, self.gui.toolbar_swatches, menu,
                "darken.png", _("&Darker"), self.gui.on_swatches_darker)
        create_action(self, self.gui.toolbar_swatches, menu,
                "lighten.png", _("&Lighter"), self.gui.on_swatches_lighter)
        create_action(self, self.gui.toolbar_swatches, menu,
                "saturate.png", _("S&aturate"), self.gui.on_swatches_saturate)
        create_action(self, self.gui.toolbar_swatches, menu,
                "desaturate.png", _("D&esaturate"), self.gui.on_swatches_desaturate)
        create_action(self, self.gui.toolbar_swatches, menu,
                "hue-counterclockwise.png", _("&Rotate colors counterclockwise"),
                self.gui.on_swatches_counterclockwise)
        create_action(self, self.gui.toolbar_swatches, menu,
                "hue-clockwise.png", _("Rotate colors clock&wise"), self.gui.on_swatches_clockwise)
        create_action(self, self.gui.toolbar_swatches, menu,
                "contrast-up.png", _("Increase &contrast"), self.gui.on_swatches_contrast_up)
        create_action(self, self.gui.toolbar_swatches, menu,
                "contrast-down.png", _("Decrease contras&t"), self.gui.on_swatches_contrast_down)
        menu.addSeparator()
        self.gui.toolbar_swatches.addSeparator()
        create_action(self, self.gui.toolbar_swatches, menu,
                "Edit-clear_mirrored.png", _("C&lear swatches"), self.gui.on_clear_swatches)
        create_action(self, self.gui.toolbar_swatches, menu,
                QtGui.QStyle.SP_DialogSaveButton, _("&Save as palette"), self.gui.on_swatches_save)

    def _init_svg_actions(self):
        menu = self.menuBar().addMenu(_("&Image"))
        create_action(self, self.gui.toolbar_template, menu,
                QtGui.QStyle.SP_DialogOpenButton,
                _("&Open template"), self.gui.on_open_template)
        create_action(self, self.gui.toolbar_template, menu,
                QtGui.QStyle.SP_DialogSaveButton,
                _("&Save resulting SVG"), self.gui.on_save_template)
        menu.addSeparator()
        create_action(self, self.gui.toolbar_template, menu,
                "colorize_swatches.png",
                _("Colorize from s&watches"), self.gui.on_colorize_harmony)
        create_action(self, self.gui.toolbar_template, menu,
                "colorize_palette.png", _("Colorize from &palette"), self.gui.on_colorize_palette)
        create_action(self, self.gui.toolbar_template, menu,
                "View-refresh.png", _("&Reset colors"), self.gui.on_reset_template)


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
                        (_("HCY"), mixers.MixerHCY), 
                        (_("HCY Desaturate"), mixers.MixerHCYDesaturate), 
                        (_("RYB"), mixers.MixerRYB),
                        (_("CMYK"), mixers.MixerCMYK), 
                        (_("CMY"), mixers.MixerCMY), 
                        (_("HSI (experimental)"), mixers.MixerHSI) ] + ([(_("LCh"), mixers.MixerLCh), 
                          (_("Lab"), mixers.MixerLab), 
                          (_("LCh Desaturate"), mixers.MixerLChDesaturate)] if colors.use_lcms else [])
    
    available_selector_mixers = [(_("HLS"), mixers.MixerHLS),
                                 (_("HCY"), mixers.MixerHCY),
                                 (_("RYB"), mixers.MixerRYB) ] + ([(_("LCh"), mixers.MixerLCh)] if colors.use_lcms else [])

    available_harmonies = [(_("Just opposite"), harmonies.Opposite),
                           (_("Two opposite"),  harmonies.TwoOpposite),
                           (_("Three colors"),  harmonies.NHues(3)),
                           (_("Four colors"),   harmonies.NHues(4)),
                           (_("Similar colors"),harmonies.Similar),
                           (_("Opposite colors RYB"), harmonies.NHuesRYB(2)),
                           (_("Three colors RYB"), harmonies.NHuesRYB(3)),
                           (_("Four colors RYB"), harmonies.NHuesRYB(4)) ] + ([(_("Three colors LCh"),   harmonies.NHuesLCh(3)),
                            (_("Four colors LCh"),   harmonies.NHuesLCh(4))] if colors.use_lcms else [])

    available_shaders = [(_("Saturation"), harmonies.Saturation),
                         (_("Value"),      harmonies.Value),
                         (_("Chroma"),     harmonies.Chroma),
                         (_("Luma"),       harmonies.Luma),
                         (_("Warmer"),     harmonies.Warmer),
                         (_("Cooler"),     harmonies.Cooler) ]
    
    def __init__(self,*args):
        QtGui.QWidget.__init__(self, *args)

        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        self.mixer = mixers.MixerRGB

        palette_widget = self._init_palette_widgets()
        harmonies_widget = self._init_harmonies_widgets()
        svg_widget = self._init_svg_widgets()

        splitter.addWidget(palette_widget)
        splitter.addWidget(harmonies_widget)
        splitter.addWidget(svg_widget)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(splitter)
        self.setLayout(hbox)

    def _init_svg_widgets(self):
        widget = QtGui.QWidget()
        vbox_right = QtGui.QVBoxLayout()

        self.toolbar_template = QtGui.QToolBar()
        vbox_right.addWidget(self.toolbar_template)


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

        vbox_right.addStretch()

        self.svg = SvgTemplateWidget(self)
        #self.svg.setMinimumSize(300,300)
        #self.svg.setMaximumSize(500,500)
        self.svg.template_loaded.connect(self.on_template_loaded)
        self.svg.colors_matched.connect(self.on_colors_matched)
        #self.svg.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.svg.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.svg.loadTemplate(locate_template("template.svg"))
        vbox_right.addWidget(self.svg)
        vbox_right.addStretch()
        
        widget.setLayout(vbox_right)
        return widget

    def _init_palette_widgets(self):
        widget = QtGui.QWidget()

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
        vbox_left.addLayout(labelled(_("Mixing model:"), self.mixers))
        vbox_left.addWidget(self.palette)

    
        widget.setLayout(vbox_left)
        return widget

    def _init_harmonies_widgets(self):
        widget = QtGui.QWidget()
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
        self.selector.setMinimumSize(150,150)
        self.selector.setMaximumSize(500,500)
        self.selector.setHarmony(harmonies.Opposite)
        self.selector.selected.connect(self.on_select_color)
        vbox_center.addWidget(self.selector, 3)

        self.current_color = ColorWidget(self)
        self.current_color.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.current_color.setMaximumSize(100,50)
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
        widget.setLayout(vbox_center)
        return widget

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
        filename = save_palette_filename(self, _("Save palette"))
        if filename:
            save_palette(self.palette.palette, filename)

    def on_save_palette_image(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, _("Save palette image"), ".", "*.png")
        if filename:
            image = self.palette.get_image()
            image.save(filename)

    def on_open_palette(self):
        palette = open_palette_dialog(self, _("Open palette"))
        if palette:
            self.mixers.setCurrentIndex(0)
            self.palette.palette = palette
            self.palette.selected_slot = None
            self.palette.redraw()
            self.update()

    def on_swatches_save(self):
        filename = save_palette_filename(self, _("Save palette"))
        if filename:
            clrs = [w.getColor() for w in self.harmonized if w.getColor() is not None]
            palette = Palette(mixers.MixerRGB, nrows=4, ncols=5)
            for row in range(4):
                for col in range(5):
                    palette.slots[row][col].color = clrs[row*5 + col]
                    palette.slots[row][col].mark(True)
            save_palette(palette, filename)
    
    def on_toggle_edit(self):
        self.palette.editing_enabled = not self.palette.editing_enabled
        self.update()

    def on_clear_swatches(self):
        for w in self.harmonized:
            w.setColor(None)
            w.update()

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

    def on_swatches_counterclockwise(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.increment_hue(clr, 0.03)
            w.setColor(clr)
            w.update()

    def on_swatches_clockwise(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.increment_hue(clr, -0.03)
            w.setColor(clr)
            w.update()

    def on_swatches_contrast_up(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.contrast(clr, 0.1)
            w.setColor(clr)
            w.update()

    def on_swatches_contrast_down(self):
        for w in self.harmonized:
            clr = w.getColor()
            if clr is None:
                continue
            clr = colors.contrast(clr, -0.1)
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

    def on_palette_counterclockwise(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.increment_hue(clr, 0.03)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_palette_clockwise(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.increment_hue(clr, -0.03)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_palette_contrast_up(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.contrast(clr, 0.1)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_palette_contrast_down(self):
        for row, col, slot in self.palette.palette.getUserDefinedSlots():
            clr = slot.getColor()
            clr = colors.contrast(clr, -0.1)
            slot.setColor(clr)
        self.palette.palette.recalc()
        self.palette.update()

    def on_template_loaded(self):
        for w in self.svg_colors:
            w.setColor(None)

        for i, clr in enumerate(self.svg.get_svg_colors()[:21]):
            #print(" #{} -> {}".format(i, str(clr)))
            self.svg_colors[i].setColor(clr)
        self.update()

    def on_set_current_color(self):
        self.selector.setColor(self.current_color.getColor())

    def on_select_from_palette(self, row, col):
        color = self.palette.palette.getColor(row, col)
        print(_("Selected from palette: ") + str(color))
        self.current_color.setColor(color)
        self.current_color.selected.emit()

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
        self.svg.setColors([w.getColor() for w in self.harmonized if w.getColor() is not None])
        self.update()

    def on_colorize_palette(self):
        xs = self.palette.palette.getColors()
        self.svg.setColors(sum(xs,[]))
        self.update()

    def on_reset_template(self):
        self.svg.resetColors()
        self.update()

    def on_open_template(self):
        filename = filedialog.get_image_filename(self, _("Open SVG template"), ".", "*.svg")
        if filename:
            self.svg.loadTemplate(str(filename))
    
    def on_save_template(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, _("Save SVG"), ".", "*.svg")
        if filename:
            content = self.svg.get_svg()
            f = open(unicode(filename),'w')
            f.write(content)
            f.close()
    
if __name__ == "__main__":
    
    app = QtGui.QApplication(sys.argv)
    w = GUI()
    w.show()
    sys.exit(app.exec_())

