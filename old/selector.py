#!/usr/bin/python

import gtk
gdk = gtk.gdk
import cairo
from colorsys import rgb_to_hsv, hsv_to_rgb
from math import pi, sin, cos, sqrt, atan2, floor
import struct
from array import array
from color import color_to_rgb, rgb_to_color, FULL_LIGHT

CSTEP=0.007
PADDING=4

class GColorSelector(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.color = (1,0,0)
        self.hsv = (0,1,1)
        self.connect('expose-event', self.draw)
        self.set_events(gdk.BUTTON_PRESS_MASK |
                        gdk.BUTTON_RELEASE_MASK |
                        gdk.POINTER_MOTION_MASK |
                        gdk.ENTER_NOTIFY |
                        gdk.LEAVE_NOTIFY |
                        gdk.DROP_FINISHED |
                        gdk.DROP_START |
                        gdk.DRAG_STATUS)
        self.connect('button-press-event', self.on_button_press)
        self.connect('button-release-event', self.on_button_release)
        self.connect('configure-event', self.on_configure)
        self.connect('motion-notify-event', self.motion)
        self.connect('drag_data_get', self.drag_get)
        self.button_pressed = False
        self.do_select = True

    def test_drag(self, x,y, d):
        return d<20

    def move(self,x,y):
        pass

    def motion(self,w, event):
        if not self.button_pressed:
            return
        d = sqrt((event.x-self.press_x)**2 + (event.y-self.press_y)**2)
        if self.test_drag(event.x,event.y,d):
            print 'dragging'
            self.do_select = False
            self.drag_begin([("application/x-color",0,80)], gdk.ACTION_COPY, 1, event)
        else:
            self.move(event.x,event.y)

    def drag_get(self, widget, context, selection, targetType, eventTime):
        r,g,b = self.color
        r = min(int(r*65536), 65535)
        g = min(int(g*65536), 65535)
        b = min(int(b*65536), 65535)
        clrs = struct.pack('HHHH',r,g,b,0)
        selection.set(selection.target, 8, clrs)

    def on_configure(self,w, size):
        self.w = size.width
        self.h = size.height
        self.configure_calc()

    def configure_calc(self):
        pass

    def on_select(self,color):
        pass

    def select_color_at(self, x,y):
        pass

    def set_color(self, color):
        self.color = color
        self.hsv = rgb_to_color(*color)
        self.queue_draw()

    def get_color(self):
        return self.color

    def on_button_press(self,w, event):
        self.button_pressed = True
        self.do_select = True
        self.press_x = event.x
        self.press_y = event.y

    def on_button_release(self,w, event):
        if self.button_pressed and self.do_select:
            self.select_color_at(event.x,event.y)
            self.on_select(self.color)
        self.button_pressed = False

    def draw(self,w,event):
        cr = self.window.cairo_create()
        cr.set_source_rgb(*self.color)
        cr.rectangle(PADDING,PADDING, self.w-2*PADDING, self.h-2*PADDING)
        cr.fill()

class RectSlot(GColorSelector):
    def __init__(self,color=(1,1,1),size=48):
        GColorSelector.__init__(self)
        self.color = color
        self.set_size_request(size,size)

class RecentColors(gtk.HBox):
    def __init__(self, N=5):
        gtk.HBox.__init__(self)
        self.set_border_width(4)
        self.N = N
        self.slots = []
        self.colors = []
        for i in range(N):
            slot = RectSlot()
            slot.on_select = self.slot_selected
            self.pack_start(slot, expand=True)
            self.slots.append(slot)
            self.colors.append(slot.color)
        self.show_all()

    def slot_selected(self,color):
        self.on_select(color)

    def on_select(self,color):
        pass

    def set_color(self, color):
        if color in self.colors:
            self.colors.remove(color)
        self.colors.insert(0, color)
        if len(self.colors) > self.N:
            self.colors = self.colors[:-1]
        for color,slot in zip(self.colors, self.slots):
            slot.set_color(color)

CIRCLE_N = 12.0

class CircleSelector(GColorSelector):
    def __init__(self, color=(1,0,0)):
        GColorSelector.__init__(self)
        self.color = color
        self.hsv = rgb_to_color(*color)
        self.previous = color
        self.ryb = False

    def redraw(self):
        self.circle_img = None
        self.queue_draw()
#         self.set_color(self.color, redraw=True)

    def calc_line(self, angle):
        x1 = self.x0 + self.r2*cos(-angle)
        y1 = self.y0 + self.r2*sin(-angle)
        x2 = self.x0 + self.r3*cos(-angle)
        y2 = self.y0 + self.r3*sin(-angle)
        return x1,y1,x2,y2

    def configure_calc(self):
        self.x0 = self.w/2.0
        self.y0 = self.h/2.0
        self.M = M = min(self.w,self.h)-2
        self.r1 = M/10.0
        self.rd = 0.27*M
        self.r2 = 0.4*M
        self.r3 = M/2.0
        self.m = self.rd/sqrt(2.0)
        self.circle_img = None

    def set_color(self, color, redraw=True):
        self.previous = self.color
        r,g,b = self.color = color
        h,s,v = rgb_to_color(r,g,b, ryb=self.ryb)
        if s > 1:
            s = 1.
        if v > 1:
            v = 1.
        self.hsv = h,s,v
        if redraw:
            self.queue_draw()

    def test_drag(self,x,y,dist):
        d = sqrt((x-self.x0)**2 + (y-self.y0)**2)
        return not (d < self.r3)

    def move(self,x,y):
        self.select_color_at(x,y)

    def select_color_at(self, x,y):
        dx = x-self.x0
        dy = y-self.y0
        d = sqrt(dx*dx+dy*dy)
        if self.r2 < d < self.r3:
            h,s,v = self.hsv
            h = 0.5 + 0.5*atan2(dy, -dx)/pi
            self.previous = self.color
            self.color = color_to_rgb(v,s,h, ryb=self.ryb)
            self.hsv = (h,s,v)
            self.queue_draw()
            self.on_select(self.color)
        elif self.rd < d < self.r2:
            print 'selecting sample'
            a = pi+atan2(dy, -dx)
            for i,a1 in enumerate(self.angles):
                if a1-2*pi/CIRCLE_N < a < a1:
                    clr = self.simple_colors[i]
                    r,g,b = self.color = clr
                    self.hsv = rgb_to_color(r,g,b,ryb=self.ryb)
                    self.queue_draw()
                    self.on_select(self.color)
                    break
        else:
            h,s,v = self.hsv
            s = (x-self.x0+self.m)/(2*self.m)
            v = (y-self.y0+self.m)/(2*self.m)
            self.hsv = h,s,1-v
            self.color = color_to_rgb(1-v,s,h, ryb=self.ryb)
            self.queue_draw()
            self.on_select(self.color)

    def draw_square(self,width,height,radius):
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, width,height)
        cr = cairo.Context(img)
        h,s,v = self.hsv
        ds = 2*radius*0.003
        v = 0.0
        y1 = - radius
        while v < 1.0:
            s = 0.0
            y = self.y0 + y1
            x1 = self.x0 - sqrt(radius**2 - y1**2)
            x2 = self.x0 + sqrt(radius**2 - y1**2)
            g = cairo.LinearGradient(x1,y,x2,y)
            g.add_color_stop_rgb(0.0, *color_to_rgb(1.0-v, 0.0, h, ryb=self.ryb))
            g.add_color_stop_rgb(1.0, *color_to_rgb(1.0-v, 1.0, h, ryb=self.ryb))
            cr.set_source(g)
            cr.rectangle(x1,y, (x2-x1), ds)
            cr.fill_preserve()
            cr.stroke()
            v += 0.003
            y1 += ds
        h,s,v = self.hsv
        y = self.y0-radius + (1-v)*2*radius
        v1 = y - self.y0
        d = sqrt(radius**2 - v1**2)
        x = self.x0-d + s*2*d
        cr.set_source_rgb(*color_to_rgb(1-v,1-s,1-h))
        cr.arc(x,y, 3.0, 0.0, 2*pi)
        cr.stroke()
        return img

    def draw_inside_circle(self,width,height):
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, width,height)
        cr = cairo.Context(img)
        h,s,v = self.hsv
        a = h*2*pi
        self.angles = []
        self.simple_colors = []
        cr.set_line_width(6.0)
        for i in range(int(CIRCLE_N)):
            c1 = c = h + i/CIRCLE_N
            if c1 > 1:
                c1 -= 1
            cr.new_path()
            clr = color_to_rgb(v,s,c1, ryb=self.ryb)
            clr0 = color_to_rgb(v,s,c1, ryb=self.ryb)
            cr.set_source_rgb(*clr)
            self.simple_colors.append(clr0)
            an = -c1*2*pi
            self.angles.append(-an+pi/CIRCLE_N)
            a1 = an-pi/CIRCLE_N
            a2 = an+pi/CIRCLE_N
            cr.move_to(self.x0,self.y0)
            cr.arc(self.x0, self.y0, self.r2, a1, a2)
            cr.fill_preserve()
            cr.set_source_rgb(0.5,0.5,0.5)
            cr.stroke()
        x1 = self.x0 + self.r2*cos(-a)
        y1 = self.y0 + self.r2*sin(-a)
        x2 = self.x0 + self.r3*cos(-a)
        y2 = self.y0 + self.r3*sin(-a)
        self.last_line = x1,y1, x2,y2, h
        cr.set_line_width(4.0)
        cr.set_source_rgb(0,0,0)
        cr.move_to(x1,y1)
        cr.line_to(x2,y2)
        cr.stroke()
        cr.set_source_rgb(0.5,0.5,0.5)
        cr.arc(self.x0, self.y0, self.rd, 0, 2*pi)
        cr.fill()
        return img

    def draw_circle(self, w, h):
        if self.circle_img:
            return self.circle_img
#         print 'start draw_circle'
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w,h)
        cr = cairo.Context(img)
        cr.set_line_width(4.0)
        a1 = 0.0
        while a1 < 2*pi:
            clr = color_to_rgb(FULL_LIGHT, 1.0, a1/(2*pi), ryb=self.ryb)
            x1,y1,x2,y2 = self.calc_line(a1)
            a1 += CSTEP
            cr.set_source_rgb(*clr)
            cr.move_to(x1,y1)
            cr.line_to(x2,y2)
            cr.stroke()
        self.circle_img = img
        return img

    def draw(self,w,event):
        cr = self.window.cairo_create()
        cr.set_source_surface(self.draw_circle(self.w,self.h))
        cr.paint()
        cr.set_line_width(6.0)
        cr.set_source_rgb(0.5,0.5,0.5)
        cr.arc(self.x0,self.y0, self.r2, 0, 2*pi)
        cr.stroke()
        cr.arc(self.x0,self.y0, self.r3, 0, 2*pi)
        cr.stroke()
        cr.set_source_surface(self.draw_inside_circle(self.w,self.h))
        cr.paint()
        cr.set_source_surface(self.draw_square(self.w,self.h, self.rd*0.95))
        cr.paint()
        sq2 = sqrt(2.0)
        M = self.M/2.0
        r = (sq2-1)*M/(2*sq2)
        x0 = self.x0+M-r
        y0 = self.y0+M-r
        cr.set_source_rgb(*self.color)
        cr.arc(x0, y0, 0.9*r, -pi/2, pi/2)
        cr.fill()
        cr.set_source_rgb(*self.previous)
        cr.arc(x0, y0, 0.9*r, pi/2, 3*pi/2)
        cr.fill()
        cr.arc(x0, y0, 0.9*r, 0, 2*pi)
        cr.set_source_rgb(0.5,0.5,0.5)
        cr.stroke()

class VSelector(GColorSelector):
    def __init__(self, color=(1,0,0), width=40):
        GColorSelector.__init__(self)
        self.color = color
        self.hsv = rgb_to_hsv(*color)
        self.set_size_request(width,width*2)

    def select_color_at(self, x,y):
        h,s,v = self.hsv
        v = 1-y/self.h
        self.hsv = h,s,v
        self.color = hsv_to_rgb(h,s,v)
        self.queue_draw()
        self.on_select(self.color)

    def draw(self,w, event):
        cr = self.window.cairo_create()
        cr.set_line_width(4.0)
        h,s,v = self.hsv
        t = 0.0
        while t < 1.0:
            x1 = 5
            x2 = self.w-10
            y1 = y2 = t*self.h
            cr.set_source_rgb(*hsv_to_rgb(h,s,1-t))
            cr.move_to(x1,y1)
            cr.line_to(x2,y2)
            cr.stroke()
            t += CSTEP
        x1 = 5
        x2 = self.w-10
        y1 = y2 = (1-v)*self.h
        cr.set_source_rgb(0,0,0)
        cr.move_to(x1,y1)
        cr.line_to(x2,y2)
        cr.stroke()

class SSelector(VSelector):
    def select_color_at(self, x,y):
        h,s,v = self.hsv
        s = 1-y/self.h
        self.hsv = h,s,v
        self.color = hsv_to_rgb(h,s,v)
        self.queue_draw()
        self.on_select(self.color)

    def draw(self,w, event):
        cr = self.window.cairo_create()
        cr.set_line_width(4.0)
        h,s,v = self.hsv
        t = 0.0
        while t < 1.0:
            x1 = 5
            x2 = self.w-10
            y1 = y2 = t*self.h
            cr.set_source_rgb(*hsv_to_rgb(h,1-t,v))
            cr.move_to(x1,y1)
            cr.line_to(x2,y2)
            cr.stroke()
            t += CSTEP
        x1 = 5
        x2 = self.w-10
        y1 = y2 = (1-s)*self.h
        cr.set_source_rgb(0,0,0)
        cr.move_to(x1,y1)
        cr.line_to(x2,y2)
        cr.stroke()

class RGBSelector(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.color = (1,0,0)
        adj1 = gtk.Adjustment(lower=0,upper=255,step_incr=1,page_incr=10)
        adj2 = gtk.Adjustment(lower=0,upper=255,step_incr=1,page_incr=10)
        adj3 = gtk.Adjustment(lower=0,upper=255,step_incr=1,page_incr=10)
        self.r_e = gtk.SpinButton(adj1)
        self.g_e = gtk.SpinButton(adj2)
        self.b_e = gtk.SpinButton(adj3)
        self.r_e.connect('focus-out-event', self.calc_color)
        self.g_e.connect('focus-out-event', self.calc_color)
        self.b_e.connect('focus-out-event', self.calc_color)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('R'), expand=False)
        hbox.pack_start(self.r_e, expand=True)
        self.pack_start(hbox)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('G'), expand=False)
        hbox.pack_start(self.g_e, expand=True)
        self.pack_start(hbox)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('B'), expand=False)
        hbox.pack_start(self.b_e, expand=True)
        self.pack_start(hbox)

    def on_select(self,color):
        pass

    def calc_color(self, spin, event):
        r = self.r_e.get_value()
        g = self.g_e.get_value()
        b = self.b_e.get_value()
        self.color = (r/255.0, g/255.0, b/255.0)
        self.on_select(self.color)

    def set_color(self, color):
        self.color = color
        r,g,b = color
        self.r_e.set_value(r*255)
        self.g_e.set_value(g*255)
        self.b_e.set_value(b*255)

class HSVSelector(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.color = (1,0,0)
        self.hsv = (0,1,1)
        adj1 = gtk.Adjustment(lower=0,upper=359,step_incr=1,page_incr=10)
        adj2 = gtk.Adjustment(lower=0,upper=100,step_incr=1,page_incr=10)
        adj3 = gtk.Adjustment(lower=0,upper=100,step_incr=1,page_incr=10)
        self.h_e = gtk.SpinButton(adj1)
        self.s_e = gtk.SpinButton(adj2)
        self.v_e = gtk.SpinButton(adj3)
        self.h_e.connect('focus-out-event', self.calc_color)
        self.s_e.connect('focus-out-event', self.calc_color)
        self.v_e.connect('focus-out-event', self.calc_color)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('H'), expand=False)
        hbox.pack_start(self.h_e, expand=True)
        self.pack_start(hbox)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('S'), expand=False)
        hbox.pack_start(self.s_e, expand=True)
        self.pack_start(hbox)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label('V'), expand=False)
        hbox.pack_start(self.v_e, expand=True)
        self.pack_start(hbox)

    def on_select(self,color):
        pass

    def calc_color(self, spin, event):
        h = self.h_e.get_value()
        s = self.s_e.get_value()
        v = self.v_e.get_value()
        self.hsv = h/359.0, s/100.0, v/100.0
        self.color = hsv_to_rgb(*self.hsv)
        self.on_select(self.color)

    def set_color(self, color):
        self.color = color
        self.hsv = rgb_to_hsv(*color)
        h,s,v = self.hsv
        self.h_e.set_value(h*359)
        self.s_e.set_value(s*100)
        self.v_e.set_value(v*100)

class Selector(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        hbox = gtk.HBox()
        self.pack_start(hbox, expand=True)
        vbox = gtk.VBox()
        hbox.pack_start(vbox,expand=True)
        self.recent = RecentColors()
        self.circle = CircleSelector()
        corr_checkbox = gtk.CheckButton('RYB')
        corr_checkbox.connect('toggled', self.on_ryb_toggled)
        model = gtk.HBox()
        model.pack_start(corr_checkbox, expand=False)
        vbox.pack_start(model, expand=False)
        vbox.pack_start(self.circle, expand=True)
        self.rgb_selector = RGBSelector()
        self.hsv_selector = HSVSelector()
        self.rgb_selector.on_select = self.rgb_selected
        self.hsv_selector.on_select = self.hsv_selected
        hbox2 = gtk.HBox()
        hbox2.set_spacing(6)
        hbox2.pack_start(self.rgb_selector)
        hbox2.pack_start(self.hsv_selector)
        expander = gtk.Expander('Colors history')
        expander.set_spacing(6)
        expander.add(self.recent)
        self.pack_start(expander, expand=False)
        expander = gtk.Expander('Details')
        expander.set_spacing(6)
        expander.add(hbox2)
        self.pack_start(expander, expand=False)
        self.circle.on_select = self.hue_selected
        self.recent.on_select = self.recent_selected
        self.widgets = [self.recent, self.circle, self.rgb_selector, self.hsv_selector]

        self.connect('drag_data_received',self.drag_data)
        self.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                 [("application/x-color",0,80)],
                 gtk.gdk.ACTION_COPY)
#         self.drag_source_set(gdk.BUTTON1_MASK, [("application/x-color",0,80)], gdk.ACTION_COPY)

    def on_ryb_toggled(self, checkbox):
        self.circle.ryb = checkbox.get_active()
        self.circle.redraw()

    def set_color(self,color,exclude=None):
        for w in self.widgets:
            if w is not exclude:
                w.set_color(color)
        self.on_select(color)

    def drag_data(self, widget, context, x,y, selection, targetType, time):
        r,g,b,a = struct.unpack('HHHH', selection.data)
        clr = (r/65536.0, g/65536.0, b/65536.0)
        self.set_color(clr)

    def rgb_selected(self, color):
        self.set_color(color, exclude=self.rgb_selector)

    def hsv_selected(self, color):
        self.set_color(color, exclude=self.hsv_selector)

    def hue_selected(self, color):
        self.set_color(color, exclude=self.circle)

    def recent_selected(self, color):
        self.set_color(color)

    def on_select(self,color):
        self.color = color
        #print 'Selected:', color

class Window(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title('Color selector')
        self.connect('destroy', lambda w: gtk.main_quit())
        self.selector = Selector()
        self.add(self.selector)
        self.show_all()

w = Window()
gtk.main()

