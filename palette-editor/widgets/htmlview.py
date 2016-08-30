
from copy import deepcopy as copy
from PyQt4.QtCore import QUrl, QString
from PyQt4.QtWebKit import QWebView
from PyQt4 import QtGui, QtCore

from palette.storage.html import *
from widgets import ColorWidget
from models.models import *

class HtmlView(QWebView):
    def __init__(self, parent=None):
        QWebView.__init__(self, parent)

    def load_file(self, filename):
        html = open(filename).read()
        #self.html = Soup(html)
        self.inline_colors, self.css_colors = colors_dicts(html)
        self.old_inline_colors = copy(self.inline_colors)
        self.old_css_colors = copy(self.css_colors)
        self.html, self.inline_css, self.separate_css = extract_css(html)
        self.css = merge_css(self.inline_css, self.separate_css)
        html_text = str( add_inline_css(self.html, self.css) )
        self.setHtml(QString(html_text))

    def set_inline_color(self, key, color):
        html = change_inline_colors(self.html, self.old_inline_colors, {key: color})
        html_text = str(html)
        print html_text
        self.setHtml(QString(html_text))

    def set_css_color(self, key, color):
        css = change_css_colors(self.css, self.old_css_colors, {key: color})
        html = add_inline_css(self.html, css)
        html_text = str(html)
        print html_text
        self.setHtml(QString(html_text))

class Preview(QtGui.QWidget):
    def __init__(self, model, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.model = model
        self.htmlview = HtmlView(self)
        self.layout = QtGui.QVBoxLayout()
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.layout.addWidget(splitter)
        bottom = QtGui.QWidget(self)
        self.hbox = QtGui.QHBoxLayout()
        bottom.setLayout(self.hbox)
        splitter.addWidget(self.htmlview)
        splitter.addWidget(bottom)
        self.inline_colors_scroll = None
        self.css_colors_scroll = None
        self.setLayout(self.layout)

    def _create_scrolls(self):
        if self.inline_colors_scroll is not None:
            self.hbox.removeWidget(self.inline_colors_scroll)
        if self.css_colors_scroll is not None:
            self.hbox.removeWidget(self.css_colors_scroll)

        self.inline_colors_scroll = scroll = QtGui.QScrollArea(self)
        self.inline_colors_form = QtGui.QVBoxLayout()
        self.inline_colors_form.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        w = QtGui.QWidget(self)
        w.setLayout(self.inline_colors_form)
        scroll.setWidget(w)
        self.hbox.addWidget(scroll)

        self.css_colors_scroll = scroll = QtGui.QScrollArea(self)
        self.css_colors_form = QtGui.QVBoxLayout()
        self.css_colors_form.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        w = QtGui.QWidget(self)
        w.setLayout(self.css_colors_form)
        scroll.setWidget(w)
        self.hbox.addWidget(scroll)

    def load_file(self, filename):
        self.htmlview.load_file(filename)
        self._create_scrolls()

        for key,color in self.htmlview.inline_colors.iteritems():
            model = HtmlColor(self.model, key, color)
            w = ColorWidget(self, model)
            w.setMinimumSize(60,20)
            #w.setColor_(color)
            model.selected.connect(self.on_select_inline(w, key))
            self.inline_colors_form.addWidget(w)

        for key,color in self.htmlview.css_colors.iteritems():
            model = HtmlColor(self.model, key, color)
            w = ColorWidget(self, model)
            w.setMinimumSize(60,20)
            #w.setColor_(color)
            model.selected.connect(self.on_select_css(w, key))
            self.css_colors_form.addWidget(w)

    def on_select_inline(self, w, key):
        print "ping"
        def handler(color):
            #color = w.getColor()
            self.htmlview.set_inline_color(key, color)
        return handler

    def on_select_css(self, w, key):
        print "ping"
        def handler(color):
            #color = w.getColor()
            self.htmlview.set_css_color(key, color)
        return handler

class HtmlColor(ColorModel):

    selected = QtCore.pyqtSignal(Color)

    def __init__(self, parent, name, color=None):
        ColorModel.__init__(self, parent, color)
        self.name = name

    def setColor(self, color):
        self.color = color
        self.selected.emit(color)

    def get_tooltip(self):
        if self.color is None:
            return None
        return self.name + "\n" + self.color.verbose()

