#!/usr/bin/python

import sys
import os
from os.path import join, basename, dirname, abspath, exists
import gettext

from PyQt4 import QtGui

bindir = dirname(sys.argv[0])
rootdir = dirname(bindir)
sys.path.append(rootdir)

datarootdir = join( rootdir, "share" )
if not sys.platform.startswith('win'):
    datarootdir_installed = join( datarootdir, "palette-editor" )
    if exists(datarootdir_installed):
        datarootdir = datarootdir_installed
else:
    datarootdir_compiled = join( bindir, "share" )
    if exists(datarootdir_compiled):
        datarootdir = datarootdir_compiled

def locate_locales():
    d = abspath( join(rootdir, "share", "locale") )
    if sys.platform.startswith('win'):
        if not exists(d):
            d = abspath( join(bindir, "share", "locale") )
    print("Using locales at " + d)
    return d

if sys.platform.startswith('win'):
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang

# translation = gettext.translation("colors", localedir=locate_locales(), fallback=True)
# _ = translation.ugettext


gettext.install("colors", localedir=locate_locales(), unicode=True)

from widgets.widgets import *
from widgets.wheel import HCYSelector
from color import colors, mixers, harmonies
from color.colors import Color
from color.spaces import *
from palette.palette import Palette
from palette.widget import PaletteWidget
from palette.image import PaletteImage
from matching.svg_widget import SvgTemplateWidget
from dialogs.open_palette import *
from dialogs import filedialog
from dialogs.colorlovers import *

def locate_icon(name):
    return join(datarootdir, "icons", name)

def locate_template(name):
    return join(datarootdir, "templates", name)

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
        create_action(self, self.gui.toolbar_palette, menu,
                QtGui.QStyle.SP_DialogOpenButton,
                _("&Open palette"), self.gui.on_open_palette)
        if colorlovers_available:
            create_action(self, self.gui.toolbar_palette, menu,
                    "download.png",
                    _("Download palette from Colorlovers.com"),
                    self.gui.on_download_colorlovers)
        create_action(self, self.gui.toolbar_palette, menu,
                QtGui.QStyle.SP_DialogSaveButton,
                _("&Save palette"), self.gui.on_save_palette)
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
                "swatches_to_palette.png", _("To &palette"), self.gui.on_swatches_to_palette)
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
                          (_("Lab"), mixers.MixerLab) ] if colors.use_lcms else [])
    
    available_selector_mixers = [(_("HLS"), mixers.MixerHLS),
                                 (_("HCY"), mixers.MixerHCY),
                                 (_("RYB"), mixers.MixerRYB) ] + ([(_("LCh"), mixers.MixerLCh)] if colors.use_lcms else [])

    harmonies_LCh = [(_("Opposite colors LCh"), harmonies.Opposite(LCh)),
                     (_("Split complimentary LCh"),  harmonies.SplitComplimentary(LCh)),
                     (_("Similar colors LCh"),harmonies.Similar(LCh)),
                     (_("Similar and opposite LCh"),harmonies.SimilarAndOpposite(LCh)),
                     (_("Rectangle LCh"),   harmonies.Rectangle(LCh)),
                     (_("Three colors LCh"),   harmonies.NHues(LCh, 3)),
                     (_("Four colors LCh"),   harmonies.NHues(LCh, 4)),
                     (_("Five colors LCh"),   harmonies.FiveColors(LCh))
                    ] 

    available_harmonies = [(_("Just opposite"), harmonies.Opposite(HSV)),
                           (_("Split complimentary"),  harmonies.SplitComplimentary(HSV)),
                           (_("Three colors"),  harmonies.NHues(HSV, 3)),
                           (_("Four colors"),   harmonies.NHues(HSV, 4)),
                           (_("Rectangle"),     harmonies.Rectangle(HCY)),
                           (_("Five colors"),   harmonies.FiveColors(HCY)),
                           (_("Similar colors"),harmonies.Similar(HCY)),
                           (_("Similar and opposite"),harmonies.SimilarAndOpposite(HCY)),
                           (_("Split complimentary RYB"),  harmonies.SplitComplimentary(RYB)),
                           (_("Similar colors RYB"),harmonies.Similar(RYB)),
                           (_("Similar and opposite RYB"),harmonies.SimilarAndOpposite(RYB)),
                           (_("Opposite colors RYB"), harmonies.NHues(RYB, 2)),
                           (_("Three colors RYB"), harmonies.NHues(RYB, 3)),
                           (_("Four colors RYB"), harmonies.NHues(RYB, 4)),
                           (_("Rectangle RYB"),   harmonies.Rectangle(RYB)),
                           (_("Five colors RYB"),   harmonies.FiveColors(RYB)) ] + (harmonies_LCh if colors.use_lcms else [])
    
    available_shaders = [(_("Saturation"), harmonies.Saturation),
                         (_("Value"),      harmonies.Value),
                         (_("Chroma"),     harmonies.Chroma),
                         (_("Luma"),       harmonies.Luma),
                         (_("Hue"),        harmonies.Hue),
                         (_("Hue + Luma"), harmonies.HueLuma),
                         (_("Chroma + Luma"), harmonies.LumaPlusChroma),
                         (_("Chroma - Luma"), harmonies.LumaMinusChroma),
                         (_("Warmer"),     harmonies.Warmer),
                         (_("Cooler"),     harmonies.Cooler) ]
    
    def __init__(self,*args):
        QtGui.QWidget.__init__(self, *args)

        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        self.mixer = mixers.MixerRGB

        self._shades_parameter = 0.5

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
        self.svg.file_dropped.connect(self.on_svg_file_dropped)
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
        self.palette.file_dropped.connect(self.on_palette_file_dropped)
        
        self.mixers = QtGui.QComboBox()
        self.mixers.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        for mixer, nothing in self.available_mixers:
            self.mixers.addItem(mixer)
        self.mixers.currentIndexChanged.connect(self.on_select_mixer)
        vbox_left.addLayout(labelled(_("Mixing model:"), self.mixers))
        vbox_left.addWidget(self.palette, 9)

        box = QtGui.QHBoxLayout()
        label = QtGui.QLabel(_("Scratchpad:"))
        box.addWidget(label)
        mk_shades = QtGui.QPushButton(_("Shades >>"))
        mk_shades.clicked.connect(self.on_shades_from_scratchpad)
        box.addWidget(mk_shades)
        vbox_left.addLayout(box)

        scratch = QtGui.QHBoxLayout()
        self.scratchpad = []
        for i in range(7):
            w = ColorWidget(self)
            w.selected.connect(self.on_change_scratchpad)
            self.scratchpad.append(w)
            w.border_color = Color(0,0,0)
            w.setMaximumSize(100,100)
            scratch.addWidget(w)
        vbox_left.addLayout(scratch, 1)
    
        widget.setLayout(vbox_left)
        return widget

    def _init_harmonies_widgets(self):
        widget = QtGui.QWidget()
        vbox_center = QtGui.QVBoxLayout()

        self.tabs = QtGui.QTabWidget()

        selector_box = QtGui.QVBoxLayout()
        selector_w = QtGui.QWidget()
        form = QtGui.QFormLayout()

        self.selector_mixers = QtGui.QComboBox()
        for mixer, nothing in self.available_selector_mixers:
            self.selector_mixers.addItem(mixer)
        self.selector_mixers.currentIndexChanged.connect(self.on_select_selector_mixer)

        form.addRow(_("Selector model:"), self.selector_mixers)

        self.harmonies = QtGui.QComboBox() 
        for harmony, nothing in self.available_harmonies:
            self.harmonies.addItem(harmony)
        self.harmonies.currentIndexChanged.connect(self.on_select_harmony)

        form.addRow(_("Harmony:"), self.harmonies)
        selector_box.addLayout(form)

        self.harmony_slider = slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.valueChanged.connect(self.on_harmony_parameter)
        slider.setEnabled(False)
        selector_box.addWidget(slider,1)

        self.selector = Selector(mixers.MixerHLS)
        self.selector.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.selector.setMinimumSize(150,150)
        self.selector.setMaximumSize(500,500)
        self.selector.setHarmony(harmonies.Opposite(HSV))
        self.selector.selected.connect(self.on_select_color)

        selector_box.addWidget(self.selector)
        selector_w.setLayout(selector_box)

        self.tabs.addTab(selector_w, _("Square"))

        hcy_widget = QtGui.QWidget()
        hcy_box = QtGui.QVBoxLayout()

        self.hcy_harmonies = hcy_harmonies = QtGui.QComboBox() 
        for harmony, nothing in self.available_harmonies:
            hcy_harmonies.addItem(harmony)
        hcy_harmonies.addItem(_("Manual"))
        hcy_harmonies.currentIndexChanged.connect(self.on_select_hcy_harmony)
        hcy_box.addLayout(labelled(_("Harmony:"), hcy_harmonies), 1)

        self.hcy_harmony_slider = slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.valueChanged.connect(self.on_harmony_parameter)
        slider.setEnabled(False)
        hcy_box.addWidget(slider,1)

        self.hcy_selector = HCYSelector()
        self.hcy_selector.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.hcy_selector.setMinimumSize(150,150)
        self.hcy_selector.setMaximumSize(500,500)
        self.hcy_selector.enable_editing = True
        self.hcy_selector.set_harmony(harmonies.Opposite(HSV))
        self.hcy_selector.selected.connect(self.on_select_hcy)
        self.hcy_selector.edited.connect(self.on_hcy_edit)

        hcy_box.addWidget(self.hcy_selector, 5)

#         toggle = QtGui.QPushButton("Edit")
#         toggle.setIcon(QtGui.QIcon(locate_icon("Gnome-colors-gtk-edit.png")))
#         toggle.setCheckable(True)
#         toggle.toggled.connect(self.on_hcy_edit_toggled)

        #hcy_box.addWidget(toggle, 1)
        hcy_widget.setLayout(hcy_box)

        self.tabs.addTab(hcy_widget, _("HCY Wheel"))

        vbox_center.addWidget(self.tabs, 2)

        box = QtGui.QHBoxLayout()

        self.current_color = ColorWidget(self)
        self.current_color.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.current_color.setMaximumSize(100,50)
        self.current_color.selected.connect(self.on_set_current_color)
        box.addWidget(self.current_color)

        self.auto_harmony = QtGui.QPushButton(_("Auto"))
        self.auto_harmony.setIcon(self.style().standardIcon(QtGui.QStyle.SP_ArrowDown))
        self.auto_harmony.setCheckable(True)
        box.addWidget(self.auto_harmony)

        vbox_center.addLayout(box)
        
        self.shaders = QtGui.QComboBox()
        for shader,nothing in self.available_shaders:
            self.shaders.addItem(shader)
        self.shaders.currentIndexChanged.connect(self.on_select_shader)
        self.shader = harmonies.Saturation

        vbox_center.addLayout(labelled(_("Shades:"), self.shaders))

        self.shades_slider = slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)
        slider.valueChanged.connect(self.on_shades_parameter)
        vbox_center.addWidget(slider,1)

        self.toolbar_swatches = QtGui.QToolBar()
        vbox_center.addWidget(self.toolbar_swatches)

        self.base_colors = {}
        self.base_swatches = []
        self.harmonized = []
        self.swatches = []
        self.harmonizedBox = QtGui.QVBoxLayout()
        for j in range(5):
            row = []
            hbox = QtGui.QHBoxLayout()
            for i in range(5):
                w = ColorWidget(self)
                w.setMinimumSize(30,30)
                w.setMaximumSize(50,50)
                if i == 2:
                    w.border_color = Color(0,0,0)
                    w.selected.connect(self.on_shade_selected(j))
                    self.base_swatches.append(w)
                self.harmonized.append(w)
                row.append(w)
                hbox.addWidget(w)
            self.swatches.append(row)
            self.harmonizedBox.addLayout(hbox)

        vbox_center.addLayout(self.harmonizedBox, 1)
        widget.setLayout(vbox_center)
        return widget

    def on_shade_selected(self, row):
        def handler():
            clr = self.base_swatches[row].getColor()
            self.base_colors[row] = clr
            self._do_harmony()
            self.update()
        return handler

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

    def _load_palette(self, palette):
        self.mixers.setCurrentIndex(0)
        self.palette.palette = palette
        self.palette.selected_slot = None
        self.palette.redraw()
        self.update()

    def on_open_palette(self):
        palette = open_palette_dialog(self, _("Open palette"))
        if palette:
            self._load_palette(palette)

    def on_download_colorlovers(self):
        to_scratchpad, palette = download_palette(self)
        if palette:
            if to_scratchpad:
                colors = sum( palette.getColors(), [] )
                self._set_scratchpad(colors)
            else:
                self._load_palette(palette)

    def _set_scratchpad(self, colors):
        for i, clr in enumerate(colors[:7]):
            self.scratchpad[i].setColor(clr)
            #self.scratchpad[i].update()
        self.update()

    def on_palette_file_dropped(self, path):
        path = unicode(path)
        palette = load_palette(path)
        if palette:
            self._load_palette(palette)

    def on_svg_file_dropped(self, path):
        path = unicode(path)
        if path.endswith(".svg"):
            self.svg.loadTemplate(path)

    def on_swatches_save(self):
        filename = save_palette_filename(self, _("Save palette"))
        if filename:
            palette = Palette(mixers.MixerRGB, nrows=len(self.swatches), ncols=len(self.swatches[0]))
            for i,row in enumerate(self.swatches):
                for j,w in enumerate(row):
                    palette.slots[i][j].color = w.getColor()
                    palette.slots[i][j].mark(True)
            save_palette(palette, filename)

    def on_swatches_to_palette(self):
        palette = Palette(self.mixer, nrows=len(self.swatches), ncols=len(self.swatches[0]))
        for i,row in enumerate(self.swatches):
            for j,w in enumerate(row):
                clr = w.getColor()
                if clr is None:
                    palette.slots[i][j].mark(False)
                else:
                    palette.slots[i][j].color = clr
                    palette.slots[i][j].mark(True)
        self.palette.palette = palette
        self.palette.selected_slot = None
        self.palette.redraw()
        self.update()
    
    def on_toggle_edit(self):
        self.palette.editing_enabled = not self.palette.editing_enabled
        self.update()

    def on_hcy_edit_toggled(self,val):
        self.hcy_selector.enable_editing = val
        self.hcy_selector.repaint()

    def on_hcy_edit(self):
        self._auto_harmony()
        #n = len(self.available_harmonies)
        #self.hcy_harmonies.setCurrentIndex(n)

    def on_clear_swatches(self):
        for row in self.swatches:
            for w in row:
                w.setColor(None)
                w.update()

    def _map_swatches(self, fn):
        for row in self.swatches:
            for w in row:
                clr = w.getColor()
                if clr is None:
                    continue
                clr = fn(clr)
                w.setColor(clr)
        self.update()

    def on_swatches_darker(self):
        self._map_swatches(lambda clr: colors.darker(clr, 0.1))

    def on_swatches_lighter(self):
        self._map_swatches(lambda clr: colors.lighter(clr, 0.1))

    def on_swatches_saturate(self):
        self._map_swatches(lambda clr: colors.saturate(clr, 0.1))

    def on_swatches_desaturate(self):
        self._map_swatches(lambda clr: colors.desaturate(clr, 0.1))

    def on_swatches_counterclockwise(self):
        self._map_swatches(lambda clr: colors.increment_hue(clr, 0.03))

    def on_swatches_clockwise(self):
        self._map_swatches(lambda clr: colors.increment_hue(clr, -0.03))

    def on_swatches_contrast_up(self):
        self._map_swatches(lambda clr: colors.contrast(clr, 0.1))

    def on_swatches_contrast_down(self):
        self._map_swatches(lambda clr: colors.contrast(clr, -0.1))

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

    def _auto_harmony(self):
        if self.auto_harmony.isChecked():
            self.on_harmony()

    def on_set_current_color(self):
        self.base_colors = {}
        self.selector.setColor(self.current_color.getColor())
        self.hcy_selector.setColor(self.current_color.getColor())
        self._auto_harmony()

    def on_select_from_palette(self, row, col):
        color = self.palette.palette.getColor(row, col)
        print(_("Selected from palette: ") + str(color))
        self.current_color.setColor(color)
        self.current_color.selected.emit()

    def on_select_color(self):
        self.base_colors = {}
        color = self.selector.selected_color
        self.current_color.setColor(color)
        self.current_color.update()
        self.hcy_selector.setColor(color)
        self._auto_harmony()

    def on_select_hcy(self, h, c, y):
        #print("H: {:.2f}, C: {:.2f}, Y: {:.2f}".format(h,c,y))
        self.base_colors = {}
        color = colors.hcy(h,c,y)
        self.current_color.setColor(color)
        self.current_color.update()
        self.selector.setColor(color)
        self._auto_harmony()

    def on_select_harmony(self, idx):
        _, harmony = self.available_harmonies[idx]
        print("Selected harmony: " + str(harmony))
        self.selector.setHarmony(harmony)
        self.harmony_slider.setEnabled(harmony.uses_parameter)
        self._auto_harmony()

    def on_select_hcy_harmony(self, idx):
        if idx >= len(self.available_harmonies):
            self.hcy_selector.set_harmony(None)
            return
        _, harmony = self.available_harmonies[idx]
        print("Selected harmony: " + str(harmony))
        self.hcy_selector.set_harmony(harmony)
        self.hcy_harmony_slider.setEnabled(harmony.uses_parameter)

    def on_select_shader(self, idx):
        _, shader = self.available_shaders[idx]
        print("Selected shader: " + str(shader))
        self.shader = shader
        self._auto_harmony()
    
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

    def _get_base_colors(self):
        if self.tabs.currentIndex() != 1:
            colors = self.selector.harmonized
        else:
            colors = self.hcy_selector.get_harmonized()
        if colors is None:
            return None
        for i in self.base_colors.iterkeys():
            n = len(colors)
            if i > n-1:
                for t in range(i-n+1):
                    colors.append(None)
            colors[i] = self.base_colors[i]
        return colors

    def _do_harmony(self):
        base = self._get_base_colors()
        if base is None:
            return
        colors = []
        for c in base:
            if c is None:
                colors.append([])
            else:
                colors.append(self.shader.shades(c, self._shades_parameter))

        for i,row in enumerate(colors):
            for j, clr in enumerate(row):
                self.swatches[i][j].setColor(clr)
        #self.hcy_selector.set_harmonized(colors)

    def _do_shades_from_scratchpad(self):
        colors = [w.getColor() for w in self.scratchpad if w.getColor() is not None]
        for i, clr in enumerate(colors):
            self.base_colors[i] = clr
        self._do_harmony()
        self.update()

    def on_shades_from_scratchpad(self):
        self._do_shades_from_scratchpad()

    def on_change_scratchpad(self):
        pass
#         if self.auto_harmony.isChecked():
#             self._do_shades_from_scratchpad()

    def on_harmony(self):
        self._do_harmony()
        self.update()

    def on_harmony_parameter(self, value):
        p = float(value)/100.0
        self.selector.set_harmony_parameter(p)
        self.hcy_selector.set_harmony_parameter(p)
        self._auto_harmony()

    def on_shades_parameter(self, value):
        p = float(value)/100.0
        self._shades_parameter = p
        self._auto_harmony()

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
        filename = filedialog.get_image_filename(self, _("Open SVG template"), directory="", filter="*.svg")
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

