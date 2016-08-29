
from PyQt4 import QtGui, QtCore

from color.colors import *
from widgets.widgets import *
from dialogs.meta import edit_meta
from palette import *
from image import PaletteImage
from commands import *
from models.models import Clipboard

class PaletteWidget(QtGui.QLabel):
    clicked = QtCore.pyqtSignal(int,int) # (x,y)
    selected = QtCore.pyqtSignal(int,int) # (row, column)
    file_dropped = QtCore.pyqtSignal(unicode)

    def __init__(self, parent, palette, options, padding=2.0, background=None, undoStack=None, indicate_modes=False, *args):
        QtGui.QLabel.__init__(self, parent, *args)
        self.palette = palette
        self.options = options
        self.palette_image = PaletteImage(palette, padding=padding, background=background, indicate_modes=indicate_modes)
        self.indicate_modes = indicate_modes

        if undoStack is None:
            self.undoStack = QtGui.QUndoStack(self)
        else:
            self.undoStack = undoStack

        self.selected_slot = None

        self._drag_start_pos = None

        self.selection_enabled = True
        self.editing_enabled = True
        self.drop_file_enabled = True

        self._delete_rect = None
        self._insert_line = None
        self._mouse_pressed = False

        self.buttons_size = 24
        self.setMinimumSize(100,50)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self.buttons_color = QtGui.QColor(240,240,240, 127)

    def setMixer(self, mixer):
        self.palette.setMixer(mixer)
        self.update()

    def get_selected_slot(self):
        if self.selected_slot is None:
            return None
        else:
            row,col = self.selected_slot
            return self.palette.slots[row][col]

    def recalc_size(self):
        r,c = self.palette.nrows, self.palette.ncols
        self.setMinimumSize(c*30, r*30)

    def redraw(self):
        self.palette_image.palette = self.palette
        self.palette_image.invalidate()
        self.recalc_size()
        self.repaint()

    def dragEnterEvent(self, event):
        if event.mimeData().hasColor() and self.editing_enabled:
            event.acceptProposedAction()
        if event.mimeData().hasUrls() and self.drop_file_enabled:
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasColor():
            qcolor = QtGui.QColor(event.mimeData().colorData())
            r,g,b,_ = qcolor.getRgb()
            color = Color(r,g,b)
            event.acceptProposedAction()
            if event.mimeData().hasFormat("application/x-metainfo"):
                data = event.mimeData().data("application/x-metainfo")
                color.meta.set_from_xml(str(data))

            row,col = self._get_slot_rc_at(event.pos().x(), event.pos().y())
            command = SetColor(self, row, col, color)
            self.undoStack.push(command)
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            path = unicode( urls[0].path() )
            self.file_dropped.emit(path)

    def sizeHint(self):
        r,c = self.palette.nrows, self.palette.ncols
        return QtCore.QSize(c*50, r*50)

    def _get_button_radius(self):
        return self.buttons_size/2.0 - 3

    def _get_button_rect(self, center):
        xc, yc = center
        r = self._get_button_radius()
        return QtCore.QRectF(xc-r, yc-r, 2*r, 2*r)

    def _get_image_size(self):
        w, h = self.size().width(),  self.size().height()
        return (w-self.buttons_size, h-self.buttons_size)

    def _get_slot_size(self):
        image_w, image_h = self._get_image_size()
        rows, cols = self.palette.nrows, self.palette.ncols
        rw = float(image_w)/float(cols)
        rh = float(image_h)/float(rows)
        return (rw, rh)

    def _get_delete_col_button_centers(self):
        image_w, image_h = self._get_image_size()
        rows, cols = self.palette.nrows, self.palette.ncols
        rw, rh = self._get_slot_size()
        r = self._get_button_radius()
        yc = image_h + r
        return [(i*rw + rw/2.0, yc) for i in range(cols)]

    def _get_delete_row_button_centers(self):
        image_w, image_h = self._get_image_size()
        rows, cols = self.palette.nrows, self.palette.ncols
        rw, rh = self._get_slot_size()
        r = self._get_button_radius()
        xc = image_w + r
        return [(xc, i*rh + rh/2.0) for i in range(rows)]

    def _get_insert_col_button_centers(self):
        image_w, image_h = self._get_image_size()
        rows, cols = self.palette.nrows, self.palette.ncols
        rw, rh = self._get_slot_size()
        r = self._get_button_radius()
        yc = image_h + r
        return [(i*rw, yc) for i in range(cols)]

    def _get_insert_row_button_centers(self):
        image_w, image_h = self._get_image_size()
        rows, cols = self.palette.nrows, self.palette.ncols
        rw, rh = self._get_slot_size()
        r = self._get_button_radius()
        xc = image_w + r
        return [(xc, i*rh) for i in range(rows)]

    def _draw_delete_button(self, qp, rect):
        qp.setPen(self.buttons_color)
        qp.setBrush(self.buttons_color)
        qp.drawEllipse(rect)
        qp.setBrush(Color(255,0,0))
        center = rect.center()
        x0,y0 = center.x(), center.y()
        x,y = x0-7, y0-2
        w,h = 14, 4
        qp.drawRect(x,y, w, h)

    def _draw_insert_button(self, qp, rect):
        qp.setPen(self.buttons_color)
        qp.setBrush(self.buttons_color)
        qp.drawEllipse(rect)
        qp.setBrush(Color(0,255,0))
        center = rect.center()
        x0,y0 = center.x(), center.y()
        x,y = x0-7, y0-2
        w,h = 14, 4
        qp.drawRect(x,y, w, h)
        x,y = x0-2, y0-7
        w,h = 4, 14
        qp.drawRect(x,y, w, h)

    def _get_col_rect(self, coln):
        image_w, image_h = self._get_image_size()
        rw, rh = self._get_slot_size()
        return QtCore.QRectF(coln*rw, 0, rw, image_h)

    def _get_row_rect(self, rown):
        image_w, image_h = self._get_image_size()
        rw, rh = self._get_slot_size()
        return QtCore.QRectF(0, rh*rown, image_w, rh)

    def _get_insert_row_line(self, rown):
        image_w, image_h = self._get_image_size()
        rw, rh = self._get_slot_size()
        return (0, rh*rown, image_w, rh*rown)

    def _get_insert_col_line(self, coln):
        image_w, image_h = self._get_image_size()
        rw, rh = self._get_slot_size()
        return (coln*rw, 0, coln*rw, image_h)

    def _draw_delete_rect(self, qp, rect):
        qp.setBrush(QtGui.QColor(0,0,0,0))
        qp.setPen(Color(255,0,0))
        qp.drawRect(rect)

    def _draw_insert_line(self, qp, line):
        x1,y1,x2,y2 = line
        qp.setPen(QtGui.QPen(QtGui.QBrush(Color(0,255,0)), 3.0))
        qp.drawLine(x1,y1,x2,y2)

    def _get_delete_col_button_at_xy(self, x, y):
        r = self._get_button_radius()
        for coln, center in enumerate( self._get_delete_col_button_centers() ):
            xc, yc = center
            if (x-xc)**2 + (y-yc)**2 < r**2:
                return coln
        return None

    def _get_delete_row_button_at_xy(self, x, y):
        r = self._get_button_radius()
        for rown, center in enumerate( self._get_delete_row_button_centers() ):
            xc, yc = center
            if (x-xc)**2 + (y-yc)**2 < r**2:
                return rown
        return None

    def _get_insert_col_button_at_xy(self, x, y):
        r = self._get_button_radius()
        for coln, center in enumerate( self._get_insert_col_button_centers() ):
            xc, yc = center
            if (x-xc)**2 + (y-yc)**2 < r**2:
                return coln
        return None

    def _get_insert_row_button_at_xy(self, x, y):
        r = self._get_button_radius()
        for rown, center in enumerate( self._get_insert_row_button_centers() ):
            xc, yc = center
            if (x-xc)**2 + (y-yc)**2 < r**2:
                return rown
        return None

    def get_image(self, width=None, height=None):
        if width is None:
            width = self.palette.ncols * 48
        if height is None:
            height = self.palette.nrows * 48
        image = self.palette_image.get(width, height)
        return image

    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            self._on_tooltip(event)
            return True
        else:
            return super(PaletteWidget, self).event(event)

    def _on_tooltip(self, event):
        x,y = event.pos().x(), event.pos().y()
        row,col = self._get_slot_rc_at(x,y)
        try:
            slot = self.palette.slots[row][col]
            color = slot.getColor()
            if color is not None:
                QtGui.QToolTip.showText(event.globalPos(), color.verbose())
        except IndexError:
            pass

    def paintEvent(self, event):
        w, h = self.size().width(),  self.size().height()
        image_w, image_h = self._get_image_size()
        image = self.palette_image.get(image_w, image_h)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, image)
        rw,rh = self._get_slot_size()

        if self.editing_enabled:
            for rect in map(self._get_button_rect, self._get_delete_col_button_centers() ):
                self._draw_delete_button(qp, rect)
            for rect in map(self._get_button_rect, self._get_delete_row_button_centers() ):
                self._draw_delete_button(qp, rect)
            for rect in map(self._get_button_rect, self._get_insert_col_button_centers() ):
                self._draw_insert_button(qp, rect)
            for rect in map(self._get_button_rect, self._get_insert_row_button_centers() ):
                self._draw_insert_button(qp, rect)

            if self._delete_rect is not None:
                self._draw_delete_rect(qp, self._delete_rect)

            if self._insert_line is not None:
                self._draw_insert_line(qp, self._insert_line)

        qp.setBrush(QtGui.QColor(0,0,0,0))

        if self.selected_slot is not None:
            row,col = self.selected_slot
            slot = self.palette.slots[row][col]
            y = row * rh
            x = col * rw
            qp.setPen(QtGui.QPen(QtGui.QBrush(slot.color.getVisibleColor()), 2.0))
            qp.drawRect(x,y,rw,rh)

        for row, col, slot in self.palette.getUserDefinedSlots():
            y = row * rh
            x = col * rw
            qp.setPen(slot.color.invert())
            qp.setBrush(slot.color.invert())
            qp.drawEllipse(x,y,8,8)

        qp.end()

    def wheelEvent(self, event):
        if not self.editing_enabled:
            event.ignore()
            return
        row,col = self._get_slot_rc_at(event.x(), event.y())
        slot = self.palette.slots[row][col]
        #print("{} at ({}, {})".format(str(slot), row, col))
        if slot.mode != USER_DEFINED:
            event.ignore()
            return

        event.accept()
        clr = slot.getColor()
        steps = event.delta()/120.0
        if event.modifiers() & QtCore.Qt.ControlModifier:
            clr = colors.increment_hue(clr, 0.01*steps)
        elif event.modifiers() & QtCore.Qt.ShiftModifier:
            clr = colors.lighter(clr, 0.1*steps)
        else:
            clr = colors.saturate(clr, 0.1*steps)
        command = SetColor(self, row, col, clr)
        self.undoStack.push(command)

    def mousePressEvent(self, event):
        #print("Mouse pressed")
        self.setFocus(QtCore.Qt.OtherFocusReason)
        self._mouse_pressed = True
        self._drag_start_pos = event.pos()
        event.accept()

    def mouseMoveEvent(self, event):

        x,y = event.x(), event.y()

        if self.editing_enabled:
            delete_col = self._get_delete_col_button_at_xy(x,y)
            if delete_col is not None:
                self._delete_rect = self._get_col_rect(delete_col)
                self._insert_line = None
                self.repaint()
                return

            delete_row = self._get_delete_row_button_at_xy(x,y)
            if delete_row is not None:
                self._delete_rect = self._get_row_rect(delete_row)
                self._insert_line = None
                self.repaint()
                return

            insert_col = self._get_insert_col_button_at_xy(x,y)
            if insert_col is not None:
                self._delete_rect = None
                self._insert_line = self._get_insert_col_line(insert_col)
                self.repaint()
                return

            insert_row = self._get_insert_row_button_at_xy(x,y)
            if insert_row is not None:
                self._delete_rect = None
                self._insert_line = self._get_insert_row_line(insert_row)
                self.repaint()
                return

        self._delete_rect = None
        self._insert_line = None

        if not self._mouse_pressed:
            return
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QtGui.QApplication.startDragDistance():
            return

        row,col = self._get_slot_rc_at(x,y)
        color = self.palette.getColor(row,col)
        drag = create_qdrag_color(self, color)
        drag.exec_()

    def mouseReleaseEvent(self, event):
        #print("Mouse released")
        self._mouse_pressed = False
        x,y = event.x(), event.y()
        if event.button() == self.options.select_button and self.editing_enabled:
            delete_col = self._get_delete_col_button_at_xy(x,y)
            if delete_col is not None:
                print("Deleting column #{}".format(delete_col))
                self._delete_rect = None
                command = EditLayout(self, DELETE, COLUMN, delete_col)
                self.undoStack.push(command)
                return

            delete_row = self._get_delete_row_button_at_xy(x,y)
            if delete_row is not None:
                print("Deleting row #{}".format(delete_row))
                self._delete_rect = None
                command = EditLayout(self, DELETE, ROW, delete_row)
                self.undoStack.push(command)
                return

            insert_col = self._get_insert_col_button_at_xy(x,y)
            if insert_col is not None:
                print("Inserting column #{}".format(insert_col))
                self._insert_line = None
                command = EditLayout(self, INSERT, COLUMN, insert_col)
                self.undoStack.push(command)
                return

            insert_row = self._get_insert_row_button_at_xy(x,y)
            if insert_row is not None:
                print("Inserting row #{}".format(insert_row))
                self._insert_line = None
                command = EditLayout(self, INSERT, ROW, insert_row)
                self.undoStack.push(command)
                return

        if event.button() == self.options.select_button and self.selection_enabled:
            self._select(x,y)
        elif event.button() == self.options.mark_button and self.editing_enabled:
            self._mark(x,y)
        elif event.button() == self.options.menu_button:
            menu = self._get_context_menu((x,y), self.editing_enabled)
            menu.exec_(event.globalPos())
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start_pos = event.pos()
        event.accept()

    def _get_context_menu(self, pos, editing_enabled):

        def _get_color():
            color = self._get_color_at(*pos)
            print("Palette: copy color {}".format(color))
            return color

        def _set_color(color):
            row,col = self._get_slot_rc_at(*pos)
            command = SetColor(self, row, col, color)
            self.undoStack.push(command)

        def _edit_metainfo():
            color = self._get_color_at(*pos)
            meta = edit_meta(color, self)
            print meta

        menu = QtGui.QMenu(self)
        if editing_enabled:
            mark = menu.addAction(_("Toggle mark"))
            mark.triggered.connect(lambda: self._mark(*pos))

        edit = menu.addAction(_("Edit color metainformation"))
        edit.triggered.connect(_edit_metainfo)

        self.clipboard = Clipboard(_get_color, _set_color)
        self.clipboard.add_cliboard_actions(menu, editing_enabled)
        return menu

    def _mark(self, x,y):
        row,col = self._get_slot_rc_at(x,y)
        command = MarkCommand(self, row, col)
        self.undoStack.push(command)

    def _get_slot_rc_at(self, x,y):
        w, h = self._get_image_size()
        rw = float(w)/float(self.palette.ncols)
        rh = float(h)/float(self.palette.nrows)
        row, col = int(y//rh), int(x//rw)
        #print((row,col))
        return (row, col)

    def _get_slot_at(self, x,y):
        row,col = self._get_slot_rc_at(x,y)
        slot = self.palette.slots[row][col]
        return slot

    def _get_color_at(self, x,y):
        slot = self._get_slot_at(x,y)
        color = slot.getColor()
        return color

    def _select(self, x, y):
        self.clicked.emit(x,y)
        self.selected_slot = self._get_slot_rc_at(x,y)
        self.selected.emit(*self.selected_slot)
        self.repaint()
        

