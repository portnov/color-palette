
from os.path import join, basename
from colors import *
import mixers

NONE = 0
USER_DEFINED = 1
VERTICALLY_GENERATED = 2
HORIZONTALLY_GENERATED = 3
DEFAULT_GROUP_SIZE = 7
MAX_COLS = 10

class Slot(object):
    def __init__(self, color=None, name='Untitled'):
        self.name = name
        self._color = color
        self._mode = NONE
        self._user_defined = False
        self._src_slot1 = None
        self._src_row1 = None
        self._src_col1 = None
        self._src_slot2 = None
        self._src_row2 = None
        self._src_col2 = None

    def __repr__(self):
        return "<Slot mode={}>".format(self._mode)

    def getColor(self):
        if self._color is None:
            return Color(1,1,1)
        else:
            return self._color

    def setColor(self, color):
        self._color = color

    color = property(getColor, setColor)
    
    def getMode(self):
        if self._user_defined:
            return USER_DEFINED
        else:
            return self._mode

    def setMode(self, mode):
        self._mode = mode
        if mode == USER_DEFINED:
            self._user_defined = True

    mode = property(getMode, setMode)

    def mark(self, user_defined=None):
        if user_defined is None:
            user_defined = not self._user_defined
        self._user_defined = user_defined

    def setSources(self, slot1, row1, col1, slot2, row2, col2):
        self._src_slot1 = slot1
        self._src_row1 = row1
        self._src_col1 = col1
        self._src_slot2 = slot2
        self._src_row2 = row2
        self._src_col2 = col2

    def getSource1(self):
        return self._src_slot1, self._src_row1, self._src_col1

    def getSource2(self):
        return self._src_slot2, self._src_row2, self._src_col2

class Palette(object):
    def __init__(self, mixer, nrows=1, ncols=7):
        self.mixer = mixer
        self.nrows = nrows
        self.ncols = ncols
        self.slots = [[Slot() for i in range(ncols)] for j in range(nrows)]
        self.need_recalc = True

    def mark_color(self, row, column):
        slot = self.slot[row][column]
        slot.mark()
        self.recalc()

    def del_column(self, col):
        if self.ncols < 2:
            return
        new = []
        for row in self.slots:
            new_row = []
            for c, slot in enumerate(row):
                if c != col:
                    new_row.append(slot)
            new.append(new_row)
        self.slots = new
        self.ncols -= 1
        self.recalc()

    def add_column(self, col):
        new = []
        for row in self.slots:
            new_row = []
            for c, slot in enumerate(row):
                if c == col:
                    new_row.append(Slot())
                new_row.append(slot)
            new.append(new_row)
        self.slots = new
        self.ncols += 1
        self.recalc()

    def del_row(self, row):
        if self.nrows < 2:
            return
        new = []
        for r,row_ in enumerate(self.slots):
            if r != row:
                new.append(row_)
        self.slots = new
        self.nrows -= 1
        self.recalc()

    def add_row(self, row):
        new = []
        for r,row_ in enumerate(self.slots):
            if r == row:
                new_row = [Slot() for k in range(self.ncols)]
                new.append(new_row)
            new.append(row_)
        self.slots = new
        self.nrows += 1
        self.recalc()

    def paint(self, row, column, color):
        self.slots[row][column].color = color
        self.slots[row][column].mark(True)
        #self.recalc()

    def erase(self, row, column):
        self.paint(row, column, Color(0,0,0))

    def getColor(self, row, column):
        if self.need_recalc:
            self.recalc()
        return self.slots[row][column].color

    def getColors(self):
        if self.need_recalc:
            self.recalc()
        return [[slot.color for slot in row] for row in self.slots]

    def setSlots(self, all_slots):
        self.slots = []
        row = []
        for i, slot in enumerate(all_slots):
            if i % self.ncols == 0:
                if len(row) != 0:
                    self.slots.append(row)
                row = []
            row.append(slot)
        self.slots.append(row)
        self.nrows = len(self.slots)
        self.recalc()
#         print(self.slots)
    
    def user_chosen_slot_down(self, i,j):
        """Returns tuple:
          * Is slot found
          * Row of found slot
          * Column of found slot"""

        #print("Searching down ({},{})".format(i,j))
        for i1 in range(i, self.nrows):
            slot = self.slots[i1][j]
            #print("Down: check ({},{}): {}".format(i1,j,slot))
            if slot.mode == USER_DEFINED:
                #print("Found down ({},{}): ({},{})".format(i,j, i1,j))
                return True,i1,j
        return False, self.nrows-1,j

    def user_chosen_slot_up(self, i,j):
        """Returns tuple:
          * Is slot found
          * Row of found slot
          * Column of found slot"""

        for i1 in range(i-1, -1, -1):
            if self.slots[i1][j].mode == USER_DEFINED:
                #print("Found up ({},{}): ({},{})".format(i,j, i1,j))
                return True,i1,j
        return False, 0, j

    def fixed_slot_right(self, i,j):
        """Returns tuple:
          * Mode of found slot
          * Row of found slot
          * Column of found slot"""

        for j1 in range(j, self.ncols):
            if self.slots[i][j1].mode in [USER_DEFINED, VERTICALLY_GENERATED]:
                return self.slots[i][j1].mode, i,j1
        return NONE, i,self.ncols-1

    def fixed_slot_left(self, i,j):
        """Returns tuple:
          * Mode of found slot
          * Row of found slot
          * Column of found slot"""

        for j1 in range(j-1, -1, -1):
            if self.slots[i][j1].mode in [USER_DEFINED, VERTICALLY_GENERATED]:
                return self.slots[i][j1].mode, i,j1
        return NONE, i,0

    def recalc(self):
        self._calc_modes()
        self._calc_modes()
        self._calc_modes()
        self._calc_colors()
        self.need_recalc_colors = False

    def _calc_modes(self):
        for i,row in enumerate(self.slots):
            for j,slot in enumerate(row):
                if slot.mode == USER_DEFINED:
                    continue
                # Should slot be vertically generated?
                v1,iv1,jv1 = self.user_chosen_slot_down(i,j)
                v2,iv2,jv2 = self.user_chosen_slot_up(i,j)
                h1,ih1,jh1 = self.fixed_slot_left(i,j)
                h2,ih2,jh2 = self.fixed_slot_right(i,j)
                if v1 and v2:   # if there are user chosen slots above and below current
                    slot.mode = VERTICALLY_GENERATED
                    s1 = self.slots[iv1][jv1]
                    s2 = self.slots[iv2][jv2]
                    slot.setSources(s1, iv1, jv1, s2, iv2, jv2)
                elif ((v1 and j-jv1 > 1) or (v2 and jv2-j > 1)) and ((h1!=USER_DEFINED) or (h2!=USER_DEFINED)):
                    slot.mode = VERTICALLY_GENERATED 
                    s1 = self.slots[iv1][jv1]
                    s2 = self.slots[iv2][jv2]
                    slot.setSources(s1, iv1, jv1, s2, iv2, jv2)
                elif h1 and h2:
                    # if there are fixed slots at left and at right of current
                    slot.mode = HORIZONTALLY_GENERATED 
                    s1 = self.slots[ih1][jh1]
                    s2 = self.slots[ih2][jh2]
                    slot.setSources(s1, ih1, jh1, s2, ih2, jh2)
                elif (h1 or h2) and not (v1 or v2):
                    slot.mode = HORIZONTALLY_GENERATED
                    s1 = self.slots[ih1][jh1]
                    s2 = self.slots[ih2][jh2]
                    slot.setSources(s1, ih1, jh1, s2, ih2, jh2)
                else:
                    slot.mode = HORIZONTALLY_GENERATED
                    s1 = self.slots[ih1][jh1]
                    s2 = self.slots[ih2][jh2]
                    slot.setSources(s1, ih1, jh1, s2, ih2, jh2)

    def color_transition(self, from_color, to_color, steps, idx):
        if self.mixer is None:
            return Color(1,1,1)
        q = float(idx+1) / float(steps+1)
        return self.mixer.mix(from_color, to_color, q)

    def _calc_colors(self):
        for i,row in enumerate(self.slots):
            for j,slot in enumerate(row):
                if slot.mode == USER_DEFINED:
                    continue

                if slot.mode == VERTICALLY_GENERATED:
                    slot_down, iv1, jv1 = slot.getSource1()
                    slot_up, iv2, jv2 = slot.getSource2()
                    clr_down = slot_down.color
                    clr_up = slot_up.color
                    length = iv1-iv2 - 1
                    idx = i-iv2 - 1
                    try:
                        #print("Mixing ({},{}) with ({},{}) to get ({},{})".format(iv1,jv1, iv2,jv2, i,j))
                        clr = self.color_transition(clr_up,clr_down,length, idx)
                    except IndexError:
                        clr = Color(1,1,1)
                    slot.color = clr

                elif slot.mode == HORIZONTALLY_GENERATED:
                    slot_left, ih1, jh1 = slot.getSource1()
                    slot_right, ih2, jh2 = slot.getSource2()
                    clr_left = slot_left.color
                    clr_right = slot_right.color
                    length = jh2-jh1 - 1
                    idx = j-jh1 - 1
                    try:
                        #print("Mixing ({},{}) with ({},{}) to get ({},{})".format(ih1,jh1, ih2,jh2, i,j))
                        clr = self.color_transition(clr_left,clr_right,length, idx)
                    except IndexError:
                        clr = Color(1,1,1)
                    slot.color = clr

class Storage(object):
    def __init__(self, palette=None):
        self.palette = palette

    def load(self, mixer, file_r):
        raise NotImplemented

    def save(self, file_w):
        raise NotImplemented

marker = '# Colors not marked with #USER are auto-generated'

class GimpPalette(Storage):

    def save(self, file_w=None):
        if type(file_w) in [str,unicode]:
            pf = open(file_w, 'w')
            do_close = True
        elif hasattr(file_w,'write'):
            pf = file_w
            do_close = False
        pf.write('GIMP Palette\n')
        if not hasattr(self.palette, 'name'):
            if type(file_w) in [str, unicode]:
                self.palette.name = basename(file_w)
            else:
                self.palette.name='MyPaint'
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

    def load(self,mixer,file_r):
        self.palette = Palette(mixer)
        self.palette.ncols = None
        if not file_r:
            palette.filename = None
            palette.name = 'MyPaint'
            palette['MyPaint'] = []
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
        self.palette.setSlots(all_slots)
        return self.palette

