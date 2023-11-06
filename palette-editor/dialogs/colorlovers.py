
# coding: utf-8

from PyQt5 import QtGui, QtCore, QtWidgets

from palette.storage.storage import create_palette
from palette.image import PaletteImage
from color.colors import *

try: 
    from colourlovers import ColourLovers
    colorlovers_available = True
    print("Colorlovers.com API is available")
except ImportError:
    colorlovers_available = False
    print("Colorlovers.com API is not available")

table_headers = (_("ID"), _("Title"), _("Author"))

def convert_palette(clpalette):
    hexs = clpalette.colours
    colors = map(fromHex, hexs)
    return create_palette(colors)

class PalettesTable(QtWidgets.QTableWidget):

    selected = QtCore.pyqtSignal(int)

    def __init__(self, *args):
        QtWidgets.QTableWidget.__init__(self, *args)
        self._palettes = []
        self.setRowCount(1)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(table_headers)
        self.currentCellChanged.connect(self._on_select_cell)
        self.verticalHeader().setVisible(False)

    def set_palettes(self, palettes):
        self._palettes = palettes
        self.clear()
        self.setHorizontalHeaderLabels(table_headers)
        self.setRowCount(len(palettes))
        for i, palette in enumerate(palettes):
            id = QtWidgets.QTableWidgetItem(str(palette.id))
            if palette.title is not None:
                title = QtWidgets.QTableWidgetItem(palette.title)
            else: 
                title = QtWidgets.QTableWidgetItem("")
            author = QtWidgets.QTableWidgetItem(palette.user_name)
            self.setItem(i, 0, id)
            self.setItem(i, 1, title)
            self.setItem(i, 2, author)
        self.resizeColumnsToContents()

    def get_palette(self, row):
        if self._palettes:
            return self._palettes[row]
        else:
            return None

    def _on_select_cell(self, row, col, prevrow, prevcol):
        if self._palettes:
            palette = self._palettes[row]
            print(palette)
            self.selected.emit(row)

class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        
        self.palette = None
        self.to_scratchpad = False

        self._new = QtWidgets.QRadioButton(_("New"))
        self._new.setChecked(True)
        self._top = QtWidgets.QRadioButton(_("Top"))
        self._random = QtWidgets.QRadioButton(_("Random"))

        radiobox = QtWidgets.QVBoxLayout()
        radiobox.addWidget(self._new)
        radiobox.addWidget(self._top)
        radiobox.addWidget(self._random)

        self.hue_option = QtWidgets.QComboBox()
        self.hue_option.addItem(_("Any"))
        self.hue_option.addItem(_("Yellow"), 'yellow')
        self.hue_option.addItem(_("Orange"), 'orange')
        self.hue_option.addItem(_("Red"), 'red')
        self.hue_option.addItem(_("Green"), 'green')
        self.hue_option.addItem(_("Violet"), 'violet')
        self.hue_option.addItem(_("Blue"), 'blue')

        self.keywords = QtWidgets.QLineEdit()
        self.username = QtWidgets.QLineEdit()

        optsbox = QtWidgets.QFormLayout()
        optsbox.addRow(_("Hue:"), self.hue_option)
        optsbox.addRow(_("Keywords:"), self.keywords)
        optsbox.addRow(_("User:"), self.username)

        topbox = QtWidgets.QHBoxLayout()
        topbox.addLayout(radiobox, 2)
        topbox.addLayout(optsbox, 2)

        query = QtWidgets.QPushButton(_("&Query"))
        query.clicked.connect(self._on_query)
        topbox.addWidget(query, 1)

        tablebox = QtWidgets.QHBoxLayout()
        self.table = PalettesTable()
        self.table.setMinimumSize(450, 300)
        self.table.selected.connect(self._on_select_palette)
        tablebox.addWidget(self.table, 3)

        previewbox = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel(_("Preview:"))
        previewbox.addWidget(label,1)
        self.preview = QtWidgets.QLabel()
        previewbox.addWidget(self.preview, 5)
        self.label = QtWidgets.QLabel()
        self.label.setMaximumSize(200, 150)
        self.label.setWordWrap(True)
        previewbox.addWidget(self.label, 1)
        tablebox.addLayout(previewbox, 1)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(topbox)
        layout.addLayout(tablebox)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        ok = QtWidgets.QPushButton(_("&Load"))
        ok.clicked.connect(self.accept)
        scratch = QtWidgets.QPushButton(_("To &scratchpad"))
        scratch.clicked.connect(self._on_load_to_scratchpad)
        cancel = QtWidgets.QPushButton(_("&Cancel"))
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(scratch)
        buttons.addWidget(cancel)

        layout.addLayout(buttons,1)

        self.setLayout(layout)
        self.setWindowTitle(_("Download palette from Colorlovers.com"))

    def _get_query_type(self):
        if self._new.isChecked():
            return 'new'
        if self._top.isChecked():
            return 'top'
        if self._random.isChecked():
            return 'random'

    def _on_load_to_scratchpad(self):
        self.to_scratchpad = True
        self.accept()

    def _on_query(self):
        cl = ColourLovers()
        query_type = self._get_query_type()
        username = self.username.text()
        keywords = self.keywords.text()
        hue_idx = self.hue_option.currentIndex()
        hue = self.hue_option.itemData(hue_idx)
        opts = {}
        if username:
            opts['lover'] = username
        if keywords:
            opts['keywords'] = keywords
        if hue:
            opts['hueOption'] = str(hue.toString())
        print(opts)
        palettes = cl.palettes(query_type, **opts)
        self.table.set_palettes(palettes)

    def _describe_palette(self, palette):
        return _("ID: {}\nTitle: {}\nDescription: {}\nAuthor: {}").format(palette.id, palette.title, palette.description, palette.user_name)

    def _on_select_palette(self, row):
        clpalette = self.table.get_palette(row)
        self.label.setText(self._describe_palette(clpalette))
        palette = convert_palette(clpalette)
        image = PaletteImage(palette).get(160,160)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.preview.setPixmap(pixmap.scaled(self.preview.width(), self.preview.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.palette = palette

def download_palette(parent=None):
    dialog = DownloadDialog(parent=parent)
    if dialog.exec_():
        return dialog.to_scratchpad, dialog.palette
    else:
        return False, None

