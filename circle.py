#!/usr/bin/python

from math import sqrt,pi,cos,sin
import gtk
gdk = gtk.gdk
import cairo
from color import mixRYB

sq36 = sqrt(3.)/6.
sq33 = sqrt(3.)/3.
ANGLE_STEP=1/24.
RAD_STEP = 1/12.

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

    def segment(self,cr,color,rad,phi):
        cr.set_source_rgb(*color)
#         x0,y0 = self.x0, self.y0
#         x0 = rad*cos(phi*2*pi)/2.
#         y0 = rad*sin(phi*2*pi)/2.
        a1,r1 = phi*2*pi,rad
        a2,r2 = (phi+ANGLE_STEP)*2*pi, rad+RAD_STEP
        x1,y1 = r1*cos(a1)/2., r1*sin(a1)/2.
        x2,y2 = r2*cos(a1)/2., r2*sin(a1)/2.
        x3,y3 = r2*cos(a2)/2., r2*sin(a2)/2.
        x4,y4 = r1*cos(a2)/2., r1*sin(a2)/2.
        cr.arc(0,0, r1/2., a2,a1)
#         cr.line_to(x3,y3)
        cr.arc(0,0,r2/2., a1,a2)
#         cr.line_to(x1,y1)
        cr.fill()

    def draw_img(self):
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w,self.h)
        cr = cairo.Context(img)
        cr.translate(self.x0,self.y0)
        cr.scale(self.M,self.M)
        rad = 1.
        while rad > 0.01:
            phi = 0.0
            while phi < 1:
                if phi < 1./3:
                    qB = 0
                    qY = phi*3
                    qR = 1-qY
                elif phi < 2./3:
                    qR = 0
                    qB = (phi-1./3)*3
                    qY = 1-qB
                else:  #
                    qY = 0
                    qR = (phi-2./3)*3
                    qB = 1-qR
                r,g,b = mixRYB(qR,qY,qB)
                if rad > 2./3:
                    s = 1-(rad-2./3)*3
                    r = s*r + (1-s)
                    g = s*g + (1-s)
                    b = s*b + (1-s)
                else:
                    s = rad*1.5
                    r = s*r
                    g = s*g
                    b = s*b
                self.segment(cr, (r,g,b), rad, phi)
#                 cr.set_source_rgb(r,g,b)
#                 x = rad*cos(phi*2*pi)/2.
#                 y = rad*sin(phi*2*pi)/2.
#                 cr.arc(x,y,0.02, 0,2*pi)
#                 cr.fill()
                phi += ANGLE_STEP
            rad -= RAD_STEP
        return img

    def draw(self,w,event):
        if not self.img:
            self.img = self.draw_img()
        cr = self.window.cairo_create()
        cr.set_source_surface(self.img)
        cr.paint()

w = gtk.Window()
w.connect('destroy', lambda w: gtk.main_quit())

circle = Circle()
w.add(circle)
w.show_all()

gtk.main()

