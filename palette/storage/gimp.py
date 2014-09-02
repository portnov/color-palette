
from os.path import join, basename
from PyQt4 import QtGui

from l10n import _
from color.colors import *
from color import mixers
from palette.storage.storage import *

marker = '# Colors not marked with #USER are auto-generated'

def save_gpl(name, ncols, clrs, file_w):
    if type(file_w) in [str,unicode]:
        pf = open(file_w, 'w')
        do_close = True
    elif hasattr(file_w,'write'):
        pf = file_w
        do_close = False
    else:
        raise ValueError("Invalid argument type in save_gpl: {}".format(type(file_w)))
    pf.write('GIMP Palette\n')
    pf.write('Name: '+name+'\n')
    if ncols is not None:
        pf.write('Columns: %s\n' % ncols)
    for color in clrs:
        r, g, b = color.getRGB()
        n = 'Untitled'
        s = '%d %d %d %s\n' % (r, g, b, n)
        pf.write(s)
    if do_close:
        pf.close()

class GimpPalette(Storage):

    title = _("Gimp palette")
    filters = ["*.gpl"]
    can_save = True
    can_load = True

    @staticmethod
    def get_options_widget(dialog, filename):

        def on_columns_changed(n):
            dialog.options = n
            dialog.on_current_changed(filename)

        ncols = None
        pf = open(filename,'r')
        l = pf.readline().strip()
        if l != 'GIMP Palette':
            pf.close()
            return None
        for line in pf:
            line = line.strip()
            lst = line.split()
            if lst[0]=='Columns:':
                ncols = int( lst[1] )
                break
        pf.close()

        widget = QtGui.QWidget()
        box = QtGui.QHBoxLayout()
        label = QtGui.QLabel(_("Columns: "))
        spinbox = QtGui.QSpinBox()
        spinbox.setMinimum(2)
        spinbox.setMaximum(100)
        if ncols is None:
            ncols = MAX_COLS
        spinbox.setValue(ncols)
        box.addWidget(label)
        box.addWidget(spinbox)
        spinbox.valueChanged.connect(on_columns_changed)
        widget.setLayout(box)
        return widget

    def save(self, file_w=None):
        if type(file_w) in [str,unicode]:
            pf = open(file_w, 'w')
            do_close = True
        elif hasattr(file_w,'write'):
            pf = file_w
            do_close = False
        else:
            raise ValueError("Invalid argument type in GimpPalette.save: {}".format(type(file_w)))
        pf.write('GIMP Palette\n')
        if not hasattr(self.palette, 'name'):
            if type(file_w) in [str, unicode]:
                self.palette.name = basename(file_w)
            else:
                self.palette.name='Colors'
        pf.write('Name: '+self.palette.name+'\n')
        if hasattr(self.palette, 'ncols') and self.palette.ncols:
            pf.write('Columns: %s\n' % self.palette.ncols)
        pf.write(marker+'\n')
        pf.write('#\n')
        for row in self.palette.slots:
            for slot in row:
                if slot.mode == USER_DEFINED:
                    n = slot.name + ' #USER'
                else:
                    n = slot.name
                r, g, b = slot.color.getRGB()
                s = '%d %d %d %s\n' % (r, g, b, n)
                pf.write(s)
        if do_close:
            pf.close()

    def load(self, mixer, file_r, force_ncols=None):
        self.palette = Palette(mixer)
        self.palette.ncols = None
        if not file_r:
            palette.filename = None
            palette.name = 'Gimp'
            return
        elif hasattr(file_r,'read'):
            pf = file_r
            self.palette.filename = None
            do_close = False
        elif type(file_r) in [str,unicode]:
            pf = open(file_r)
            self.palette.filename = file_r
            do_close = True
        l = pf.readline().strip()
        if l != 'GIMP Palette':
            raise SyntaxError, "Invalid palette file!"
        self.palette.name = pf.readline().strip().split()[1]
        all_user = True
        n_colors = 0
        all_slots = []
        for line in pf:
            line = line.strip()
            if line==marker:
                all_user = False
            if line.startswith('#'):
                continue
            lst = line.split()
            if lst[0]=='Columns:':
                self.palette.ncols = int( lst[1] )
            if len(lst) < 3:
                continue
            rs,gs,bs = lst[:3]
            clr = Color(float(rs), float(gs), float(bs))
            #print(str(clr))
            slot = Slot(clr)
            n_colors += 1
            if all_user or lst[-1]=='#USER':
                slot.mode = USER_DEFINED
                name = ' '.join(lst[3:-1])
            else:
                name = ' '.join(lst[3:])
            slot.name = name
            all_slots.append(slot)
        if do_close:
            pf.close()
        if n_colors < DEFAULT_GROUP_SIZE:
            self.palette.ncols = n_colors
        if not self.palette.ncols:
            if n_colors > MAX_COLS:
                self.palette.ncols = MAX_COLS
            else:
                self.palette.ncols = n_colors
        if force_ncols is not None:
            self.palette.ncols = force_ncols
        self.palette.setSlots(all_slots)
        print("Loaded palette: {}x{}".format( self.palette.nrows, self.palette.ncols ))
        return self.palette

