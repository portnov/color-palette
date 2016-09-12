#!/usr/bin/python

import sys
import os
from os.path import join, basename, dirname, abspath, exists, expanduser
from copy import copy
import gettext
import appdirs
import argparse
import webbrowser

from PyQt4 import QtGui

print("Using Python " + sys.version)

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
from widgets.scratchpad import *
from widgets.picker import Picker
from widgets.commands.swatches import *
from widgets.commands.general import *
from widgets.wheel import HCYSelector
from widgets.labselector import LabSelector
from widgets.expander import ExpanderWidget
from color import colors, mixers, harmonies
from color.colors import Color
from color.spaces import *
from palette.palette import Palette
from palette.widget import PaletteWidget
from palette.image import PaletteImage
from palette.commands import ChangeColors, SwatchesToPalette, SortBy
from matching.svg_widget import SvgTemplateWidget
from dialogs.open_palette import *
from dialogs import filedialog
from dialogs.colorlovers import *
from dialogs.meta import MetaDialog, edit_meta
from dialogs.options import OptionsDialog
from models.models import *
from models.options import Options

__version__ = '0.0.7'

def locate_icon(name):
    path = join(datarootdir, "icons", name)
    if not exists(path):
        print("Icon not found: " + path)
    return path
try:
    __builtins__.locate_icon = locate_icon
except AttributeError:
    __builtins__['locate_icon'] = locate_icon

def locate_template(name):
    path = join(datarootdir, "templates", name) 
    if exists(path):
        return path
    else:
        return None

def locate_palette(name):
    base = appdirs.user_config_dir("palette-editor", "palette-editor")
    if not exists(base):
        os.makedirs(base)
    return join(base, name)

def compose_icon(icon, filename):
    icon_pixmap = icon.pixmap(24,24)
    qp = QtGui.QPainter(icon_pixmap)
    image = QtGui.QImage(locate_icon(filename))
    qp.drawImage(0, 0, image)
    qp.end()
    return QtGui.QIcon(icon_pixmap)

def create_action(parent, toolbar, menu, icon, title, handler, key=None):
    if type(icon) == str:
        action = QtGui.QAction(QtGui.QIcon(locate_icon( icon)), title, parent)
    elif type(icon) == QtGui.QIcon:
        action = QtGui.QAction(icon, title, parent)
    elif icon is not None:
        action = QtGui.QAction(parent.style().standardIcon(icon), title, parent)
    else:
        action = QtGui.QAction(title, parent)
    if key is not None:
        action.setShortcut(key)
    if toolbar:
        toolbar.addAction(action)
    menu.addAction(action)
    if handler:
        action.triggered.connect(handler)
    return action

def labelled(label, widget):
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(QtGui.QLabel(label))
    hbox.addWidget(widget)
    return hbox
    
class GUI(QtGui.QMainWindow):

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
                     (_("Similar colors LCh"),harmonies.Similar(LCh,3)),
                     (_("Five similar LCh"),harmonies.Similar(LCh,5)),
                     (_("Similar and opposite LCh"),harmonies.SimilarAndOpposite(LCh)),
                     (_("Rectangle LCh"),   harmonies.Rectangle(LCh)),
                     (_("Three colors LCh"),   harmonies.NHues(LCh, 3)),
                     (_("Four colors LCh"),   harmonies.NHues(LCh, 4)),
                     (_("Five colors LCh"),   harmonies.FiveColors(LCh)),
                     (_("Similar colors Lab"),   harmonies.LabSimilar),
                     (_("Similar and opposite Lab"),   harmonies.SimilarAndOppositeLab),
                     (_("Rectangle Lab"),   harmonies.RectangleLab),
                     (_("Five colors Lab"),   harmonies.Lab5),
                    ] 

    available_harmonies = [(_("Just opposite"), harmonies.Opposite(HSV)),
                           (_("Split complimentary"),  harmonies.SplitComplimentary(HSV)),
                           (_("Three colors"),  harmonies.NHues(HSV, 3)),
                           (_("Four colors"),   harmonies.NHues(HSV, 4)),
                           (_("Rectangle"),     harmonies.Rectangle(HCY)),
                           (_("Five colors"),   harmonies.FiveColors(HCY)),
                           (_("Similar colors"),harmonies.Similar(HCY,3)),
                           (_("Five similar"),harmonies.Similar(HCY,5)),
                           (_("Similar and opposite"),harmonies.SimilarAndOpposite(HCY)),
                           (_("Split complimentary RYB"),  harmonies.SplitComplimentary(RYB)),
                           (_("Similar colors RYB"),harmonies.Similar(RYB,3)),
                           (_("Five similar RYB"),harmonies.Similar(RYB,5)),
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
    
    def __init__(self, template_path=None):
        QtGui.QMainWindow.__init__(self)

        self.settings = QtCore.QSettings("palette-editor", "palette-editor")
        self.options = Options(self.settings)

        self.model = Document(self, self.options)
        self.undoStack = self.model.get_undo_stack()

        self.mixer = mixers.MixerRGB

        self._shades_parameter = 0.5

        palette_widget = self._init_palette_widgets()
        scratchbox = self._init_scratchbox()
        harmonies_widget = self._init_harmonies_widgets()
        swatches = self._init_swatches()
        svg_widget = self._init_svg_widgets(template_path)
        history = self._init_color_history()

        self.setTabPosition( QtCore.Qt.TopDockWidgetArea , QtGui.QTabWidget.North )
        #self.setDockOptions( QtGui.QMainWindow.ForceTabbedDocks )
        self.setDockNestingEnabled(True)

#         central_widget = QtGui.QWidget()
#         self.setCentralWidget(central_widget)
#         central_widget.hide()

        self._dock("Palette", _("Palette"), QtCore.Qt.TopDockWidgetArea, palette_widget)
        self._dock("Scratchpad", _("Scratchpad"), QtCore.Qt.BottomDockWidgetArea, scratchbox)
        self._dock("Harmonies", _("Harmonies"), QtCore.Qt.TopDockWidgetArea, harmonies_widget)
        self._dock("Swatches", _("Color swatches"), QtCore.Qt.BottomDockWidgetArea, swatches)
        self._dock("Preview", _("Preview"), QtCore.Qt.TopDockWidgetArea, svg_widget)
        self._dock("History", _("Color history"), QtCore.Qt.BottomDockWidgetArea, history)


        self.harmonies.set_last_enabled(False)
        self.harmonies.selected.connect(self.on_select_harmony)
        self.tabs.currentChanged.connect(self.on_change_tab)

        self._init_menu()

        self._init_palette_actions()
        self._init_harmonies_actions()
        self._init_svg_actions()
        self._help_menu()

        self.setWindowTitle(_("Palette editor"))
        #self.resize(600, 800)
        #self._restore()

    def _get_settings_color(self, settings, name):
        s = unicode(settings.value(name).toString()) 
        if not s:
            return None
        return colors.fromHex(s)
    
    def _put_settings_color(self, settings, name, clr):
        if clr:
            s = clr.hex()
            settings.setValue(name, s)

    def restore(self, palette_filename=None):
        if palette_filename is None:
            palette_filename = locate_palette("default.gpl")
        if exists(palette_filename):
            palette = load_palette(palette_filename)
            self._load_palette(palette)

        settings = self.settings
        self.restoreGeometry(settings.value("geometry").toByteArray())
        self.restoreState(settings.value("windowState").toByteArray())

        selector_idx, ok = settings.value("selector/tab").toUInt()
        if ok:
            self.tabs.setCurrentIndex(selector_idx)

        mixer_idx, ok = settings.value("selector/mixer").toUInt()
        if ok:
            _, mixer = self.available_selector_mixers[mixer_idx]
            self.selector.setMixer(mixer, mixer_idx)

        clr = self._get_settings_color(settings, "current_color")
        if clr:
            self._select_color(clr)

        mixer_idx, ok = settings.value("palette/mixer").toUInt()
        if ok:
            _, mixer = self.available_mixers[mixer_idx]
            self.setMixer(mixer, mixer_idx)

        space_idx, ok = settings.value("matching/space").toUInt()
        if ok:
            self.matching_spaces.setCurrentIndex(space_idx)

        harmony_idx, ok = settings.value("harmonies/harmony").toUInt()
        if ok:
            self.harmonies.setCurrentIndex(harmony_idx)

        shader_idx, ok = settings.value("harmonies/shader").toUInt()
        if ok:
            self.shaders.setCurrentIndex(shader_idx)

        auto = settings.value("harmonies/auto").toBool()
        self.auto_harmony.setChecked(auto)

        harmony_param, ok = settings.value("harmonies/harmony_param").toUInt()
        if ok:
            self.harmony_slider.setValue(harmony_param)

        shader_param, ok = settings.value("harmonies/shader_param").toUInt()
        if ok:
            self.shades_slider.setValue(shader_param)

        nswatches = settings.beginReadArray("swatches")
        for idx in range(nswatches):
            settings.setArrayIndex(idx)
            j = idx % 5
            i = idx // 5
            clr = self._get_settings_color(settings, "color")
            if clr:
                self.swatches[i][j].setColor_(clr)
        settings.endArray()

        nclrs = settings.beginReadArray("scratchpad")
        colors = []
        for idx in range(nclrs):
            settings.setArrayIndex(idx)
            clr = self._get_settings_color(settings, "color")
            w,ok = settings.value("width").toReal()
            if clr and ok:
                colors.append((clr, w))
        self.scratchpad.colors = colors
        settings.endArray()

        self.undoStack.clear()

    def _store(self):
        if not self.settings:
            settings = QtCore.QSettings("palette-editor", "palette-editor")
        else:
            settings = self.settings

        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState());

        settings.setValue("selector/tab", self.tabs.currentIndex())

        mixer_idx = self.selector_mixers.currentIndex()
        settings.setValue("selector/mixer", mixer_idx)

        mixer_idx = self.mixers.currentIndex()
        settings.setValue("palette/mixer", mixer_idx)

        space_idx = self.matching_spaces.currentIndex()
        settings.setValue("matching/space", space_idx)

        harmony_idx = self.harmonies.currentIndex()
        settings.setValue("harmonies/harmony", harmony_idx)

        shader_idx = self.shaders.currentIndex()
        settings.setValue("harmonies/shader", shader_idx)

        auto = self.auto_harmony.isChecked()
        settings.setValue("harmonies/auto", auto)

        harmony_param = self.harmony_slider.value()
        settings.setValue("harmonies/harmony_param", harmony_param)

        shader_param = self.shades_slider.value()
        settings.setValue("harmonies/shader_param", shader_param)

        clr = self.current_color.getColor()
        self._put_settings_color(settings, "current_color", clr)

        settings.beginWriteArray("swatches")
        i = 0
        for row in self.swatches:
            for w in row:
                clr = w.getColor()
                settings.setArrayIndex(i)
                self._put_settings_color(settings, "color", clr)
                i += 1
        settings.endArray()

        settings.beginWriteArray("scratchpad")
        i = 0
        for clr,w in self.scratchpad.colors:
            settings.setArrayIndex(i)
            self._put_settings_color(settings, "color", clr)
            settings.setValue("width", w)
            i += 1
        settings.endArray()

        palette_filename = locate_palette("default.gpl")
        save_palette(self.palette.palette, palette_filename)

        settings.setValue("template/path", abspath(self.template_path))

    def _dock(self, name, title, area, widget):
        dock = QtGui.QDockWidget(title, self)
        dock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        dock.setWidget(widget)
        dock.setObjectName(name)
        self.addDockWidget(area, dock)

    def _select_color(self, clr):
        self.selector.setColor(clr)
        self.current_color.setColor(clr)

    def _init_menu(self):
        menu = self.menuBar().addMenu(_("&Edit"))
        self.undo_action = undo = self.undoStack.createUndoAction(self, _("&Undo"))
        undo.setShortcut(QtGui.QKeySequence.Undo)
        undo.setIcon(QtGui.QIcon(locate_icon("Edit-undo.png")))
        self.redo_action = redo = self.undoStack.createRedoAction(self, _("&Redo"))
        redo.setShortcut(QtGui.QKeySequence.Redo)
        redo.setIcon(QtGui.QIcon(locate_icon("Edit-redo.png")))
        menu.addAction(undo)
        menu.addAction(redo)

        menu.addAction(_("&Preferences"), self.on_show_options)

    def _init_palette_actions(self):
        menu = self.menuBar().addMenu(_("&Palette"))
        create_action(self, self.toolbar_palette, menu,
                QtGui.QStyle.SP_DialogOpenButton,
                _("&Open palette"), self.on_open_palette, key="Ctrl+O")
        if colorlovers_available:
            create_action(self, self.toolbar_palette, menu,
                    "download.png",
                    _("Download palette from Colorlovers.com"),
                    self.on_download_colorlovers)
        create_action(self, self.toolbar_palette, menu,
                QtGui.QStyle.SP_DialogSaveButton,
                _("&Save palette"), self.on_save_palette, key="Ctrl+S")
        menu.addSeparator()
        self.toolbar_palette.addSeparator()
        self.toolbar_palette.addAction(self.undo_action)
        self.toolbar_palette.addAction(self.redo_action)
        self.toolbar_palette.addSeparator()
        toggle_edit = create_action(self, self.toolbar_palette, menu,
                "Gnome-colors-gtk-edit.png",
                _("Toggle edit &mode"), self.on_toggle_edit, key="Ctrl+L")
        toggle_edit.setCheckable(True)
        toggle_edit.setChecked(False)
        menu.addSeparator()
        self.toolbar_palette.addSeparator()
        create_action(self, self.toolbar_palette, menu,
                "darken.png", _("&Darker"), self.on_palette_darker)
        create_action(self, self.toolbar_palette, menu,
                "lighten.png", _("&Lighter"), self.on_palette_lighter)
        create_action(self, self.toolbar_palette, menu,
                "saturate.png", _("S&aturate"), self.on_palette_saturate)
        create_action(self, self.toolbar_palette, menu,
                "desaturate.png", _("D&esaturate"), self.on_palette_desaturate)
        create_action(self, self.toolbar_palette, menu,
                "hue-counterclockwise.png",
                _("&Rotate colors counterclockwise"), self.on_palette_counterclockwise)
        create_action(self, self.toolbar_palette, menu,
                "hue-clockwise.png",
                _("Rotate colors clock&wise"), self.on_palette_clockwise)
        create_action(self, self.toolbar_palette, menu,
                "contrast-up.png", _("Increase &contrast"), self.on_palette_contrast_up)
        create_action(self, self.toolbar_palette, menu,
                "contrast-down.png", _("Decrease contras&t"), self.on_palette_contrast_down)

        create_action(self, None, menu, None, _("Edit palette metainformation"), self.on_edit_palette_meta)
        create_action(self, None, menu, None, _("Edit color metainformation"), self.on_edit_color_meta)

        sort_icon = QtGui.QIcon(locate_icon("sorting.png"))
        sort_menu = menu.addMenu(sort_icon, _("Sort colors"))
        create_action(self, None, sort_menu, None, _("By hue"), self.on_palette_sort_hue)
        create_action(self, None, sort_menu, None, _("By saturation"), self.on_palette_sort_saturation)
        create_action(self, None, sort_menu, None, _("By value"), self.on_palette_sort_value)

        sort_button = QtGui.QToolButton(self)
        sort_button.setText(_("Sort colors"))
        sort_button.setToolTip(_("Sort colors"))
        sort_button.setIcon(sort_icon)
        self.toolbar_palette.addWidget(sort_button)
        sort_button.setMenu(sort_menu)
        sort_button.setPopupMode(QtGui.QToolButton.InstantPopup)

    def _init_harmonies_actions(self):
        menu = self.menuBar().addMenu(_("&Swatches"))
        create_action(self, self.toolbar_swatches, menu,
                "harmony.png", _("&Harmony"), self.on_harmony)
        menu.addSeparator()
        self.toolbar_swatches.addSeparator()
        create_action(self, self.toolbar_swatches, menu,
                "darken.png", _("&Darker"), self.on_swatches_darker)
        create_action(self, self.toolbar_swatches, menu,
                "lighten.png", _("&Lighter"), self.on_swatches_lighter)
        create_action(self, self.toolbar_swatches, menu,
                "saturate.png", _("S&aturate"), self.on_swatches_saturate)
        create_action(self, self.toolbar_swatches, menu,
                "desaturate.png", _("D&esaturate"), self.on_swatches_desaturate)
        create_action(self, self.toolbar_swatches, menu,
                "hue-counterclockwise.png", _("&Rotate colors counterclockwise"),
                self.on_swatches_counterclockwise)
        create_action(self, self.toolbar_swatches, menu,
                "hue-clockwise.png", _("Rotate colors clock&wise"), self.on_swatches_clockwise)
        create_action(self, self.toolbar_swatches, menu,
                "contrast-up.png", _("Increase &contrast"), self.on_swatches_contrast_up)
        create_action(self, self.toolbar_swatches, menu,
                "contrast-down.png", _("Decrease contras&t"), self.on_swatches_contrast_down)
        menu.addSeparator()
        self.toolbar_swatches.addSeparator()
        create_action(self, self.toolbar_swatches, menu,
                "swatches_to_palette.png", _("To &palette"), self.on_swatches_to_palette)
        create_action(self, self.toolbar_swatches, menu,
                "Edit-clear_mirrored.png", _("C&lear swatches"), self.on_clear_swatches)
        create_action(self, self.toolbar_swatches, menu,
                QtGui.QStyle.SP_DialogSaveButton, _("&Save as palette"), self.on_swatches_save)

    def _init_svg_actions(self):
        menu = self.menuBar().addMenu(_("&Image"))
        create_action(self, self.toolbar_template, menu,
                QtGui.QStyle.SP_DialogOpenButton,
                _("&Open template"), self.on_open_template)
        create_action(self, self.toolbar_template, menu,
                QtGui.QStyle.SP_DialogSaveButton,
                _("&Save resulting SVG"), self.on_save_template)
        menu.addSeparator()
        create_action(self, self.toolbar_template, menu,
                "colorize_swatches.png",
                _("Colorize from s&watches"), self.on_colorize_harmony)
        create_action(self, self.toolbar_template, menu,
                "colorize_palette.png", _("Colorize from &palette"), self.on_colorize_palette)
        create_action(self, self.toolbar_template, menu,
                "View-refresh.png", _("&Reset colors"), self.on_reset_template)

    def _help_menu(self):
        menu = self.menuBar().addMenu(_("&Help"))
        menu.addAction(_("&Wiki documentation"), self.on_help)
        menu.addAction(_("&About Palette Editor"), self.on_about)

    def _init_svg_widgets(self, template_path=None):
        vbox_right = QtGui.QVBoxLayout()

        self.toolbar_template = QtGui.QToolBar()
        self.toolbar_palette.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Maximum)
        vbox_right.addWidget(self.toolbar_template)

        matching_spaces = [(_("HCY"), HCY),
                           (_("HSV"), HSV),
                           (_("HLS"), HLS),
                           (_("RGB"), RGB),
                           (_("RYB"), RYB)]
        if use_lcms:
            matching_spaces.append((_("LCh"), LCh))
            matching_spaces.append((_("Lab"), Lab))

        self.matching_spaces = ClassSelector(pairs = matching_spaces)
        vbox_right.addLayout(labelled(_("Colors matching space:"), self.matching_spaces))

        self.svg_colors = []
        label = QtGui.QLabel(_("Colors from original image:"))
        label.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        vbox_right.addWidget(label)
        vbox_svg = QtGui.QVBoxLayout()
        idx = 0
        for i in range(3):
            hbox_svg = QtGui.QHBoxLayout()
            for j in range(7):
                w = TwoColorsWidget(self, self.model.svg_colors[i][j])
                w.setMaximumSize(30,30)
                w.second_color_set.connect(self.on_dst_color_set(idx))
                idx += 1
                hbox_svg.addWidget(w)
                self.svg_colors.append(w)
            vbox_svg.addLayout(hbox_svg)
        vbox_right.addLayout(vbox_svg)

        #vbox_right.addStretch()

        self.svg = SvgTemplateWidget(self)
        #self.svg.setMinimumSize(300,300)
        #self.svg.setMaximumSize(500,500)
        self.svg.template_loaded.connect(self.on_template_loaded)
        self.svg.colors_matched.connect(self.on_colors_matched)
        self.svg.file_dropped.connect(self.on_svg_file_dropped)
        #self.svg.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.svg.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        if template_path is None:
            template_path = self.settings.value("template/path").toString()
            if template_path:
                template_path = unicode(template_path)
            else:
                template_path = locate_template("template.svg")
        else:
            template_path = template_path[0]
        if template_path:
            self.svg.loadTemplate(template_path)
            self.template_path = template_path
        vbox_right.addWidget(self.svg)

        #vbox_right.addStretch()
        vbox_right.addSpacerItem(QtGui.QSpacerItem(0,0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        widget = QtGui.QWidget()
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

        self.palette = PaletteWidget(self, palette, self.options, undoStack=self.undoStack)
        self.palette.setMinimumSize(300,300)
        self.palette.setMaximumSize(700,700)
        self.palette.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.palette.editing_enabled = False
        self.palette.selected.connect(self.on_select_from_palette)
        self.palette.file_dropped.connect(self.on_palette_file_dropped)
        
        self.mixers = ClassSelector(pairs = self.available_mixers)
        self.mixers.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.mixers.selected.connect(self.on_select_mixer)
        vbox_left.addLayout(labelled(_("Mixing model:"), self.mixers))
        vbox_left.addWidget(self.palette)

        vbox_left.addSpacerItem(QtGui.QSpacerItem(0,0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        #vbox_left.addStretch(1)
    
        widget.setLayout(vbox_left)
        return widget

    def _init_scratchbox(self):
        scratchpad_box = QtGui.QVBoxLayout()
        mk_shades = QtGui.QPushButton(_("Shades >>"))
        mk_shades.clicked.connect(self.on_shades_from_scratchpad)
        scratchpad_box.addWidget(mk_shades)

        self.scratchpad = Scratchpad(self.model.scratchpad)
        scratchpad_box.addWidget(self.scratchpad,1)
        #expander = ExpanderWidget(_("Scratchpad"), scratchpad_box)
        widget = QtGui.QWidget(self)
        widget.setLayout(scratchpad_box)
        return widget
    
    def _init_color_history(self):
        return ColorHistoryWidget(self.model.get_color_history(), vertical=False, parent=self)

    def _init_harmonies_widgets(self):
        widget = QtGui.QWidget()
        vbox_center = QtGui.QVBoxLayout()

        self.harmonies = ClassSelector(pairs=self.available_harmonies)
        self.harmonies.addItem(_("Manual"))
        vbox_center.addLayout(labelled(_("Harmony:"), self.harmonies))
        
        self.harmony_slider = slider = ParamSlider()
        slider.changed.connect(self.on_harmony_parameter)
        slider.setEnabled(False)
        vbox_center.addWidget(slider,1)

        self.tabs = QtGui.QTabWidget()

        selector_box = QtGui.QVBoxLayout()
        selector_w = QtGui.QWidget()
        form = QtGui.QFormLayout()

        self.selector_mixers = ClassSelector(pairs=self.available_selector_mixers)
        self.selector_mixers.selected.connect(self.on_select_selector_mixer)

        form.addRow(_("Selector model:"), self.selector_mixers)

        selector_box.addLayout(form)

        self.selector = Selector(mixers.MixerHLS)
        self.selector.class_selector = self.selector_mixers
        self.selector.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.selector.setMinimumSize(150,150)
        self.selector.setMaximumSize(500,500)
        self.selector.setHarmony(harmonies.Opposite(HSV))
        self.selector.harmonies_selector = self.harmonies
        self.selector.selected.connect(self.on_select_color)

        selector_box.addWidget(self.selector)
        selector_w.setLayout(selector_box)

        self.tabs.addTab(selector_w, _("Square"))

        hcy_widget = QtGui.QWidget()
        hcy_box = QtGui.QVBoxLayout()

        self.hcy_selector = HCYSelector()
        self.hcy_selector.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.hcy_selector.setMinimumSize(150,150)
        self.hcy_selector.setMaximumSize(500,500)
        self.hcy_selector.enable_editing = True
        self.hcy_selector.set_harmony(harmonies.Opposite(HSV))
        self.hcy_selector.selected.connect(self.on_select_hcy)
        self.hcy_selector.harmonies_selector = self.harmonies
        self.hcy_selector.edited.connect(self.on_hcy_edit)

        hcy_box.addWidget(self.hcy_selector, 5)

#         toggle = QtGui.QPushButton("Edit")
#         toggle.setIcon(QtGui.QIcon(locate_icon("Gnome-colors-gtk-edit.png")))
#         toggle.setCheckable(True)
#         toggle.toggled.connect(self.on_hcy_edit_toggled)

        #hcy_box.addWidget(toggle, 1)
        hcy_widget.setLayout(hcy_box)

        self.tabs.addTab(hcy_widget, _("HCY Wheel"))

        if use_lcms:
            self.lab_selector = LabSelector()
            self.lab_selector.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
            self.lab_selector.setHarmony(harmonies.Opposite(HSV))
            self.lab_selector.setMinimumSize(150,150)
            self.lab_selector.setMaximumSize(500,500)
            self.lab_selector.selected.connect(self.on_select_lab)
            self.tabs.addTab(self.lab_selector, _("Lab Square"))

        self.tabs.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        vbox_center.addWidget(self.tabs,5)

        current_color_box = QtGui.QWidget(self)
        current_color_hbox = QtGui.QHBoxLayout(current_color_box)
        current_color_box.setLayout(current_color_hbox)

        self.current_color = ColorWidget(self, self.model.current_color)
        self.current_color.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.current_color.setMaximumSize(100,50)
        self.current_color.selected.connect(self.on_set_current_color)
        current_color_hbox.addWidget(self.current_color)

        self.picker = Picker(self, _("Pic&k"), self.model.current_color)
        picker_shortcut = QtGui.QShortcut("Ctrl+I", self)
        picker_shortcut.activated.connect(lambda: self.picker.clicked.emit(False))
        current_color_hbox.addWidget(self.picker)

        vbox_center.addWidget(current_color_box)

        widget.setLayout(vbox_center)
        return widget

    def _init_swatches(self):
        swatches_vbox = QtGui.QVBoxLayout()
        
        self.shaders = ClassSelector(pairs = self.available_shaders)
        self.shaders.selected.connect(self.on_select_shader)
        self.shader = harmonies.Saturation

        box = QtGui.QHBoxLayout()
        box.addWidget(QtGui.QLabel(_("Shades:")), 1)
        box.addWidget(self.shaders, 3)

        self.auto_harmony = QtGui.QPushButton(_("Auto"))
        self.auto_harmony.setIcon(self.style().standardIcon(QtGui.QStyle.SP_ArrowDown))
        self.auto_harmony.setCheckable(True)
        box.addWidget(self.auto_harmony, 1)
        swatches_vbox.addLayout(box)

        self.shades_slider = slider = ParamSlider()
        slider.changed.connect(self.on_shades_parameter)
        swatches_vbox.addWidget(slider)

        self.toolbar_swatches = QtGui.QToolBar()
        swatches_vbox.addWidget(self.toolbar_swatches)

        self.base_colors = {}
        self.base_swatches = []
        self.harmonized = []
        self.swatches = []
        harmonizedBox = QtGui.QVBoxLayout()
        for j in range(5):
            row = []
            hbox = QtGui.QHBoxLayout()
            for i in range(5):
                swatch = self.model.swatches[i][j]
                w = ColorWidget(self, swatch)
                w.setMinimumSize(20,20)
                w.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.MinimumExpanding)
                w.setMaximumSize(50,40)
                if i == 2:
                    swatch.set_color_enabled = False
                    w.border_color = Color(0,0,0)
                    w.dropped.connect(self.on_shade_selected(j))
                    self.base_swatches.append(w)
                self.harmonized.append(w)
                row.append(w)
                hbox.addWidget(w)
            self.swatches.append(row)
            harmonizedBox.addLayout(hbox,1)
        swatches_vbox.addLayout(harmonizedBox)
        
        widget = QtGui.QWidget(self)
        widget.setLayout(swatches_vbox)
        return widget

    def on_change_tab(self, tabidx):
        selector = self._get_selectors()[tabidx]
        self.harmonies.set_last_enabled(selector.manual_edit_implemented)

    def on_shade_selected(self, row):
        def handler(r,g,b):
            color = Color(r,g,b)
            command = MakeShades(self, row, color)
            self.undoStack.push(command)
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
        filename, format = save_palette_filename(self, _("Save palette"))
        if filename:
            save_palette(self.palette.palette, filename, format)

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
                self.undoStack.beginMacro(_("adding colors to scratchpad"))
                for clr in colors:
                    self.scratchpad.add_color(clr)
                self.undoStack.endMacro()
                self.scratchpad.repaint()
            else:
                self._load_palette(palette)

    def on_edit_palette_meta(self):
        meta = edit_meta(self.palette.palette, self)
        print meta

    def on_edit_color_meta(self):
        if self.palette.get_selected_slot() is not None:
            meta = edit_meta(self.palette.get_selected_slot().getColor(), self)
            print meta

    def on_palette_file_dropped(self, path):
        path = unicode(path)
        palette = load_palette(path)
        if palette:
            self._load_palette(palette)

    def on_svg_file_dropped(self, path):
        path = unicode(path)
        if path.endswith(".svg"):
            self.svg.loadTemplate(path)
            self.template_path = path

    def on_swatches_save(self):
        filename, format = save_palette_filename(self, _("Save palette"))
        if filename:
            palette = Palette(mixers.MixerRGB, nrows=len(self.swatches), ncols=len(self.swatches[0]))
            for i,row in enumerate(self.swatches):
                for j,w in enumerate(row):
                    palette.slots[i][j].color = w.getColor()
                    palette.slots[i][j].mark(True)
            save_palette(palette, filename, format)

    def on_swatches_to_palette(self):
        command = SwatchesToPalette(self.palette, self.mixer, self.swatches)
        self.undoStack.push(command)
    
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
        command = ClearSwatches(self)
        self.undoStack.push(command)

    def on_swatches_darker(self):
        command = ChangeSwatchesColors(self, _("making color swatches darker"), 
                                        (lambda clr: colors.darker(clr, 0.1)))
        self.undoStack.push(command)

    def on_swatches_lighter(self):
        command = ChangeSwatchesColors(self, _("making color swatches lighter"),
                                         (lambda clr: colors.lighter(clr, 0.1)))
        self.undoStack.push(command)

    def on_swatches_saturate(self):
        command = ChangeSwatchesColors(self, _("saturating color swatches"),
                                         (lambda clr: colors.saturate(clr, 0.1)))
        self.undoStack.push(command)

    def on_swatches_desaturate(self):
        command = ChangeSwatchesColors(self, _("desaturating color swatches"),
                                         (lambda clr: colors.desaturate(clr, 0.1)))
        self.undoStack.push(command)

    def on_swatches_counterclockwise(self):
        command = ChangeSwatchesColors(self, _("rotating swatches colors counterclockwise"),
                                        (lambda clr: colors.increment_hue(clr, 0.03)))
        self.undoStack.push(command)

    def on_swatches_clockwise(self):
        command = ChangeSwatchesColors(self, _("rotating swatches colors clockwise"),
                                        (lambda clr: colors.increment_hue(clr, -0.03)))
        self.undoStack.push(command)

    def on_swatches_contrast_up(self):
        command = ChangeSwatchesColors(self, _("increasing swatches contrast"),
                                         (lambda clr: colors.contrast(clr, 0.1)))
        self.undoStack.push(command)

    def on_swatches_contrast_down(self):
        command = ChangeSwatchesColors(self, _("decreasing swatches contrast"),
                                         (lambda clr: colors.contrast(clr, -0.1)))
        self.undoStack.push(command)

    def on_palette_darker(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("making palette colors darker"),
                               lambda clr : colors.darker(clr, 0.1))
        self.undoStack.push(command)

    def on_palette_lighter(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("making palette colors lighter"),
                               lambda clr : colors.lighter(clr, 0.1))
        self.undoStack.push(command)

    def on_palette_saturate(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("saturating palette colors"),
                               lambda clr : colors.saturate(clr, 0.1))
        self.undoStack.push(command)

    def on_palette_desaturate(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("desaturating palette colors"),
                               lambda clr : colors.desaturate(clr, 0.1))
        self.undoStack.push(command)

    def on_palette_counterclockwise(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("rotating palette colors counterclockwise"),
                               lambda clr : colors.increment_hue(clr, 0.03))
        self.undoStack.push(command)

    def on_palette_clockwise(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("rotating palette colors clockwise"),
                               lambda clr : colors.increment_hue(clr, -0.03))
        self.undoStack.push(command)

    def on_palette_contrast_up(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("increasing palette contrast"),
                               lambda clr : colors.contrast(clr, 0.1))
        self.undoStack.push(command)

    def on_palette_contrast_down(self):
        command = ChangeColors(self.palette, self.palette.palette,
                               _("decreasing palette contrast"),
                               lambda clr : colors.contrast(clr, -0.1))
        self.undoStack.push(command)

    def on_palette_sort_hue(self):
        command = SortBy(self.palette, self.palette.palette,
                               _("sorting colors by hue"),
                               lambda clr : clr.getHSV()[0])
        self.undoStack.push(command)

    def on_palette_sort_saturation(self):
        command = SortBy(self.palette, self.palette.palette,
                               _("sorting colors by saturation"),
                               lambda clr : clr.getHSV()[1])
        self.undoStack.push(command)

    def on_palette_sort_value(self):
        command = SortBy(self.palette, self.palette.palette,
                               _("sorting colors by value"),
                               lambda clr : clr.getHSV()[2])
        self.undoStack.push(command)

    def on_template_loaded(self):
        for w in self.svg_colors:
            w.setColor_(None)

        for i, clr in enumerate(self.svg.get_svg_colors()[:21]):
            #print(" #{} -> {}".format(i, str(clr)))
            self.svg_colors[i].setColor_(clr)
        self.update()

    def _auto_harmony(self):
        if self.auto_harmony.isChecked():
            self._do_harmony()
            self.update()

    def on_set_current_color(self):
        self.base_colors = {}
        for selector in self._get_selectors():
            selector.setColor(self.current_color.getColor())
        self._auto_harmony()

    def on_select_from_palette(self, row, col):
        color = self.palette.palette.getColor(row, col)
        print(_("Selected from palette: ") + str(color))
        self.current_color.setColor(color)
        self.current_color.selected.emit()

    def _get_selectors(self):
        selectors = [self.selector, self.hcy_selector]
        if use_lcms:
            selectors.append(self.lab_selector)
        return selectors

    def on_select_color(self, sequence, prev_color, color):
        selectors = self._get_selectors()
        command = SelectColor(self, selectors, sequence, prev_color, color)
        self.undoStack.push(command)

    def on_select_hcy(self, sequence, prev_color, color):
        selectors = self._get_selectors()
        command = SelectColor(self, selectors, sequence, prev_color, color)
        self.undoStack.push(command)

    def on_select_lab(self, sequence, prev_color, color):
        selectors = self._get_selectors()
        command = SelectColor(self, selectors, sequence, prev_color, color)
        self.undoStack.push(command)

    def _get_selector(self):
        selectors = self._get_selectors()
        return selectors[self.tabs.currentIndex()]

    def on_select_harmony(self, prev_idx, idx):
        manual_enabled = self._get_selector().manual_edit_implemented
        command = SetHarmony(self._get_selectors(), self.harmony_slider, self, self.available_harmonies, prev_idx, idx, manual_enabled)
        self.undoStack.push(command)

    def on_select_shader(self, prev_idx, idx):
        command = SetShader(self, prev_idx, idx)
        self.undoStack.push(command)
    
    def on_select_mixer(self, prev_idx, idx):
        command = SetMixer(self, self.available_mixers, prev_idx, idx)
        self.undoStack.push(command)
    
    def on_select_selector_mixer(self, prev_idx, idx):
        command = SetMixer(self.selector, self.available_selector_mixers, prev_idx, idx)
        self.undoStack.push(command)

    def setMixer(self, mixer, idx):
        self.mixer = mixer
        self.palette.setMixer(mixer)
        self.mixers.select_item(idx)
    
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
        colors = copy( self._get_selector().get_harmonized() )
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
                try:
                    self.model.swatches[j][i].color = clr
                    #self.swatches[i][j].setColor_(clr)
                except IndexError:
                    print i,j
        #self.hcy_selector.set_harmonized(colors)

    def on_shades_from_scratchpad(self):
        command = ShadesFromScratchpad(self)
        self.undoStack.push(command)

    def on_harmony(self):
        command = DoHarmony(self)
        self.undoStack.push(command)

    def on_harmony_parameter(self, prev_value, value):
        command = UpdateHarmony(self, self._get_selectors(), prev_value, value)
        self.undoStack.push(command)

    def on_shades_parameter(self, prev_value, value):
        command = UpdateShades(self, prev_value, value)
        self.undoStack.push(command)

    def on_colorize_harmony(self):
        dst_colors = [w.getColor() for w in self.harmonized if w.getColor() is not None]
        space = self.matching_spaces.get_current_item()
        self.svg.setColors(dst_colors, space)
        self.update()

    def on_colorize_palette(self):
        xs = self.palette.palette.getColors()
        space = self.matching_spaces.get_current_item()
        self.svg.setColors(sum(xs,[]), space)
        self.update()

    def on_reset_template(self):
        self.svg.resetColors()
        self.update()

    def on_open_template(self):
        filename = filedialog.get_image_filename(self, _("Open SVG template"), directory="", filter="*.svg")
        if filename:
            self.svg.loadTemplate(str(filename))
            self.template_path = str(filename)
    
    def on_save_template(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, _("Save SVG"), ".", "*.svg")
        if filename:
            content = self.svg.get_svg()
            f = open(unicode(filename),'w')
            f.write(content)
            f.close()

    def on_show_options(self):
        dialog = OptionsDialog(self.options)
        dialog.exec_()

    def on_help(self):
        webbrowser.open('https://github.com/portnov/color-palette/wiki')

    def on_about(self):
        title = _("About Palette Editor")
        text = _("This is Palette Editor version {0}.\nPlease report issues at {1}.").format(__version__, 'https://github.com/portnov/color-palette/issues')
        QtGui.QMessageBox.about(self, title, text)

    def closeEvent(self, event):
        self._store()
        QtGui.QMainWindow.closeEvent(self, event);

def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--template", nargs=1, metavar="FILENAME.SVG", help=_("Use specified SVG template for preview"))
    parser.add_argument("palette", metavar="FILENAME", nargs='?', help=_("Load specified palette file"))
    return parser.parse_args()
    
if __name__ == "__main__":

    args = parse_cmdline()
    
    app = QtGui.QApplication(sys.argv)
    w = GUI(template_path=args.template)
    w.show()
    w.restore(palette_filename=args.palette)
    sys.exit(app.exec_())

