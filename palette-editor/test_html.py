#!/usr/bin/python

import sys
from PyQt4.QtGui import QApplication
from PyQt4 import QtGui
import gettext

from color.colors import *
from palette.storage.html import *
from widgets.htmlview import *

# html = open("template.html").read()
# inline_colors, css_colors = colors_dicts(html)
# #print inline_colors
# #print css_colors
# soup, inline_css, separate_css = extract_css(html)
# res = change_inline_colors(soup, inline_colors, {'h1_style_color': Color(115,100,3)})
# 
# print res
# 
# res = change_css_colors(inline_css, {'style_inline_p_background_color': Color(200, 150, 20)})
# print res.cssText

gettext.install("colors", localedir="share/locale", unicode=True)

class GUI(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.preview = Preview(self, self)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.preview, 5)
        button = QtGui.QPushButton("Load")
        button.clicked.connect(self.on_load)
        self.layout.addWidget(button)
        self.setLayout(self.layout)
        self.undoStack = QtGui.QUndoStack()

    def get_undo_stack(self):
        return self.undoStack

    def on_load(self):
        self.preview.load_file("template.html")

app = QApplication(sys.argv)
w = GUI()
w.show()
app.exec_()
