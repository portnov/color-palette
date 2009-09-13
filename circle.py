#!/usr/bin/python

from math import sqrt,pi
import gtk
gdk = gtk.gdk
import cairo
from color import mixRYB

sq36 = sqrt(3.)/6.
sq33 = sqrt(3.)/3.
STEP=6
R=0.7*STEP

def rho(x1,y1,x2,y2):
    return sqrt((x2-x1)**2 + (y2-y1)**2)

class Circle(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.set_events(gdk.BUTTON_PRESS_MASK |
                        gdk.BUTTON_RELEASE_MASK |
                        gdk.POINTER_MOTION_MASK |
                        gdk.ENTER_NOTIFY |
                        gdk.LEAVE_NOTIFY |
                        gdk.DROP_FINISHED |
                        gdk.DROP_START |
                        gdk.DRAG_STATUS)
        self.connect('configure-event', self.on_configure)
        self.connect('expose-event', self.draw)

    def on_configure(self,w,size):
        w = self.w = size.width
        h = self.h = size.height
        M = self.M = 0.8*min(w,h)
        self.x0 = w/2.
        self.y0 = h/2.
        self.x1 = self.x0-M/2
        self.y1 = self.y0+M*sq36
        self.x2 = self.x0+M/2
        self.y2 = self.y1
        self.x3 = self.x0
        self.y3 = self.y0 - M*sq33
        self.img = None

    def draw(self,w,event):
        if not self.img:
            self.img = img = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w,self.h)
            cr = cairo.Context(img)
            x = 0.0
            while x < self.w:
                y = 0.0
                while y < self.h:
                    dR = rho(self.x1,self.y1,x,y)/self.M
                    dY = rho(self.x2,self.y2,x,y)/self.M
                    dB = rho(self.x3,self.y3,x,y)/self.M
                    s = dR+dY+dB
#                     print dR,dY,dB
                    if dR>1 or dY>1 or dB>1:
                        y += STEP
                        continue
                    clr = mixRYB(1-dR/s, 1-dY/s, 1-dB/s)
                    cr.set_source_rgb(*clr)
                    cr.arc(x,y,R,0,2*pi)
                    cr.fill()
                    y += STEP
#                     print x,y
                x += STEP
        cr = self.window.cairo_create()
        cr.set_source_surface(self.img)
        cr.paint()

w = gtk.Window()
w.connect('destroy', lambda w: gtk.main_quit())

circle = Circle()
w.add(circle)
w.show_all()

gtk.main()

