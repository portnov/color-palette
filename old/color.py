from math import pi, floor, sqrt
from colorsys import hsv_to_rgb, hls_to_rgb, rgb_to_hsv, rgb_to_hls
#import lcms

HLS=False

if HLS:
    def to_rgb(h,s,l):
        return hls_to_rgb(h,l,s)
#         return lch_to_rgb(l,s,h)
    def from_rgb(r,g,b):
        h,l,s = rgb_to_hls(r,g,b)
        return h,s,l
    FULL_LIGHT = 0.5
else:
    def to_rgb(h,s,l):
        return hsv_to_rgb(h,s,l)
    def from_rgb(r,g,b):
        return rgb_to_hsv(r,g,b)
    FULL_LIGHT = 1.0

def chg(x):
    return (x*x + x)/2.

def chg1(y):
    return (sqrt(8*y+1)-1)/2. 

R=[c/255. for c in (254,39,18)]
Y=[c/255. for c in (254,255,51)]
B=[c/255. for c in (2,81,254)]

def mixRYB(qR,qY,qB):
    r =  (qR*R[0] + qY*Y[0] + qB*B[0])
    g =  (qR*R[1] + qY*Y[1] + qB*B[1])
    b =  (qR*R[2] + qY*Y[2] + qB*B[2])
    if r > 1:
        r = 1.
    if g > 1:
        g = 1.
    if b > 1:
        b = 1.
    return r,g,b

vY = 1.0
vR = 0.9
vB = 0.7

hR = 0.
hY = 1./6
hB = 2./3

def simple_mix(x1,a,x2,b):
    if a==b==0:
        return (x1+x2)/2.
    q = float(b)/(a+b)
    h = (1.-q)*x1 + q*x2
#     print 'simple_mix/ q: %.2f' % q
    return h

def mixRGB(rgb1, rgb2, q):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    r = (1.-q)*r1 + q*r2
    g = (1.-q)*g1 + q*g2
    b = (1.-q)*b1 + q*b2
    return (r, g, b)

def mixRYB_hsv(qR,qY,qB):
    return from_rgb(*mixRYB(qR,qY,qB))

def hsv_ryb_rgb(h1,s1,v1):
    if h1 < 1./3:
        q = h1*3
        h2,s2,v2 = mixRYB_hsv(chg(1-q),chg(q),0.)
    elif h1 < 2./3:
        q = (h1-1./3)*3
        h2,s2,v2 = mixRYB_hsv(0,chg(1-q),chg(q))
    else:
        q = (h1-2./3)*3
        h2,s2,v2 = mixRYB_hsv(chg(q),0,chg(1-q))
    r,g,b = to_rgb(h2, s1*s2, v1*v2)
    return r,g,b

def rgb_ryb_hsv(r,g,b):
    h1,s1,v1 = from_rgb(r,g,b)
    if h1 < 1./6:        # Between R and Y
        q = h1*6
        h2 = simple_mix(0.,chg1(1-q), 1./3,chg1(q))
    elif h1 < 2.3:       # Between Y and B
        q = (h1-1./6)*2
        h2 = simple_mix(1./3,chg1(1-q), 2./3, chg1(q))
    else:                # Between B and R
        q = (h1-2./3)*3
        h2 = simple_mix(2./3,chg1(1-q), 1.,chg1(q))
    return h2, s1, v1

def color_to_rgb(l,c,h, ryb=False):
    if ryb:
        return hsv_ryb_rgb(h,c,l)
    return to_rgb(h,c,l)

def rgb_to_color(r,g,b, ryb=False):
    if ryb:
        return rgb_ryb_hsv(r,g,b)
    return from_rgb(r,g,b)

