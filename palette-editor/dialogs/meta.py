
# coding: utf-8

from PyQt5 import QtGui, QtCore, QtWidgets

from models.meta import Meta, as_unicode

table_headers = (_("Name"), _("Value"))

class MetaModel(QtCore.QAbstractTableModel):
    def __init__(self, meta):
        QtCore.QAbstractTableModel.__init__(self)
        self.meta = meta

    def rowCount(self, parent=None):
        return len(self.meta)+1
    
    def columnCount(self, parent=None):
        return 2

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return self.meta.key(index.row())
            else:
                return self.meta.value(index.row())
        return None

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if index.column() == 0:
                value = as_unicode(value)
                if not value:
                    self.meta.remove(index.row())
                    return True
                else:
                    self.meta.setKey(index.row(), value)
                    return True
            else:
                key = self.meta.key(index.row())
                self.meta[key] = as_unicode(value)
                return True
        return True

    def addRow(self):
        parent = QtCore.QModelIndex()
        n = len(self.meta)
        self.beginInsertRows(parent, n-1,n-1)
        self.meta.add(_("Name"), u"")
        self.endInsertRows()

    def delRow(self, row):
        parent = QtCore.QModelIndex()
        self.beginRemoveRows(parent, row, row)
        self.meta.remove(row)
        self.endRemoveRows()

    def flags(self, index):
        result = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return result | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return _("Name")
            else:
                return _("Value")
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)


class MetaTable(QtWidgets.QTableView):
    def __init__(self, meta, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self._model = MetaModel(meta)
        self.setModel(self._model)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.resizeColumnsToContents()
        #self.setColumnCount(2)
        #self.setRowCount(3)
        #self.setHorizontalHeaderLabels(table_headers)
        #self.verticalHeader().setVisible(False)

    def addRow(self):
        self._model.addRow()

    def selectedRow(self):
        model = self.selectionModel()
        if model.hasSelection():
            idxs = model.selectedRows()
            return idxs[0].row()
        return None

    def delRow(self):
        row = self.selectedRow()
        if row is not None:
            self._model.delRow(row)
        self.update()

class MetaDialog(QtWidgets.QDialog):
    def __init__(self, meta, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)

        self.meta = meta
        self.table = MetaTable(meta, parent=self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table)

        toolbar = QtWidgets.QToolBar(self)
        toolbar.addAction(QtGui.QIcon(locate_icon("list-add.png")), _("Add"), self.on_add_row)
        toolbar.addAction(QtGui.QIcon(locate_icon("edit-delete.png")), _("Delete"), self.on_del_row)

        layout.addWidget(toolbar)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        ok = QtWidgets.QPushButton(_("&OK"))
        ok.clicked.connect(self.accept)
        cancel = QtWidgets.QPushButton(_("&Cancel"))
        cancel.clicked.connect(self.reject)
        buttons.addWidget(ok)
        buttons.addWidget(cancel)

        layout.addLayout(buttons)

        self.setLayout(layout)
        self.setWindowTitle(_("Edit metainformation"))

    def on_add_row(self):
        self.table.addRow()

    def on_del_row(self):
        self.table.delRow()
        
def edit_meta(owner, parent=None):
    old_meta = owner.meta.copy()
    dialog = MetaDialog(meta=owner.meta, parent=parent)
    if dialog.exec_():
        return dialog.meta
    else:
        owner.meta = old_meta
        return old_meta

