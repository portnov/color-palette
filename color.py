from math import pi, floor, sqrt
from colorsys import hsv_to_rgb, hls_to_rgb, rgb_to_hsv, rgb_to_hls
import lcms

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

xyz_profile = lcms.cmsCreateXYZProfile()
rgb_profile = lcms.cmsCreate_sRGBProfile()

xyz2rgb = lcms.cmsCreateTransform(xyz_profile, lcms.TYPE_XYZ_DBL,
                                  rgb_profile, lcms.TYPE_RGB_8,
                                  lcms.INTENT_ABSOLUTE_COLORIMETRIC,
                                  0)

def lch_to_rgb(l,c,h):
    h += 0.1054
    if h > 1.0:
        h -= 1.0
    lch = lcms.cmsCIELCh(l*100,c*100, h*360)
    lab = lcms.cmsCIELab(0.0,0.0,0.0)
    xyz = lcms.cmsCIEXYZ(0.0,0.0,0.0)
    lcms.cmsLCh2Lab(lab,lch)
    lcms.cmsLab2XYZ(None, xyz,lab)
    rgb = lcms.COLORB()
    rgb[0] = rgb[1] = rgb[2] = 0
    lcms.cmsDoTransform(xyz2rgb, xyz, rgb, 1)
#     return rgb
    return rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0

vY = 1.0
vR = 0.9
vB = 0.7

hR = 0.
hY = 1./6
hB = 2./3

def simple_mix(x1,v1,a,x2,v2,b):
    if a==b==0:
        return (x1+x2)/2.
    q = float(b)/(a+b)
    h = (1.-q)*x1 + q*x2
#     print 'simple_mix/ q: %.2f' % q
    return h

def simple_mix_invert(x1,v1,p,x2,v2,q):
    return simple_mix(x1,v1,q, x2,v2,p)

def mix3(a,b,c):
    if a==0. and b!=0.:
        s = 1-(b-c)/float(b)
    elif b==0. and a!=0.:
        s = float(c)/a
    elif a==0. and b==0.:
        s = 0.
    else:
        xA = (b-c)/float(b)
        if xA < 0:
            xA = 0.
        xB = float(c)/a
        if xB > 1:
            xB = 1.
#         print 'mix3/xA: %.2f, xB: %.2f' % (xA,xB)
        s = 1 - (xB-xA)
    v = 1-c
    return s,v

def mix_v(a,v1,b,v2):
#     print 'mix_v/a,b:', a,b
    if a==b==0:
        return 1.0
    v = 1-(a*b)/(a+b)
#     print 'mix_v/v:',v
    return v

def mixRYB_hsv(qR,qY,qB):
#     print '///mixRYB: qR: %.2f, qY: %.2f, qB: %.2f' % (qR,qY,qB)
    if qR==qY==qB==0:
        return 0.,0.,1.
    c = min(qR,qY,qB)
    if c==qR:
#         print 'min. red'
        h = mix_YB(qY,qB)
        vM = mix_v(qY,vY,qB,vB)
        sm,vm = mix3(qY,qB, c)
    elif c==qY:
#         print 'min. yellow'
        h = mix_BR(qB,qR)
        vM = mix_v(qB,vB,qR,vR)
        sm,vm = mix3(qB,qR, c)
    else: # c==qB
#         print 'min. blue'
        h = mix_RY(qR,qY)
        vM = mix_v(qR,vR,qY,vY)
        sm,vm = mix3(qR,qY, c)
#     print "h: %.2f, c: %.2f, sm: %.2f, vm: %.2f, vM: %.2f" % (h,c,sm,vm,vM)
    if 1-c >= vM:
#         print 'mixRYB_hsv/ 1-c >= vM'
        s = 1.0
        v = vM
    else:
#         print 'mixRYB_hsv/ 1-c < vM'
        s = sm
        v = vm
    return h,s,v

def mixRYB(qR,qY,qB):
    h,s,v = mixRYB_hsv(qR,qY,qB)
#     print 'mixRYB/hsv:',h,s,v
    return to_rgb(h,s,v)

def mix_RY(qR,qY):
    return simple_mix(hR,vR,qR, hY,vY,qY)

def mix_YB(qY,qB):
    return simple_mix(hY,vY,qY, hB,vB,qB)

def mix_BR(qB,qR):
    return simple_mix(hB,vB,qB, 1.,vR,qR)

def hsv_ryb_rgb(h1,s1,v1, correction = 0.0):
    if h1 < 1./3:
        q = h1*3
        qY = q
#         h2,v2 = mix_RY(q,1-q)
        h2,s2,v2 = mixRYB_hsv(chg(1-q),chg(q),0.)
    elif h1 < 2./3:
        q = (h1-1./3)*3
        qY = 1-q
#         h2,v2 = mix_YB(q,1-q)
        h2,s2,v2 = mixRYB_hsv(0,chg(1-q),chg(q))
    else:
        q = (h1-2./3)*3
        qY = 0
#         h2,v2 = mix_BR(q,1-q)
        h2,s2,v2 = mixRYB_hsv(chg(q),0,chg(1-q))
#     v2 = correct_v(qY,v2)
    l = light_transform(h2, v1*v2, correction)
    r,g,b = to_rgb(h2, s1*s2, l)
#     print 'hsv_ryb_rgb/rgb:',r,g,b
    return r,g,b

def rgb_ryb_hsv(r,g,b):
    h1,s1,v1 = from_rgb(r,g,b)
    if h1 < 1./6:        # Between R and Y
        q = h1*6
        h2,v2 = simple_mix(0.,vR,chg1(1-q), 1./3,vY,chg1(q))
    elif h1 < 2.3:       # Between Y and B
        q = (h1-1./6)*2
        h2,v2 = simple_mix(1./3,vY,chg1(1-q), 2./3,vB, chg1(q))
    else:                # Between B and R
        q = (h1-2./3)*3
        h2,v2 = simple_mix(2./3,vB,chg1(1-q), 1.,vR,chg1(q))
    return h2, s1, v2/v1

def correct_v(qY,v):
    v = v + 0.2*qY
    if v>1:
        v = 1.
    return v

def light_transform(h, l, correction=0.0):
    def change(x):
#         return - 39.6429*x**5 + 115.4617*x**4- 100.8745*x**3 + 19.4957*x**2 + 5.5600*x - 0.5458
        return - 138.4962*x**5 + 351.0104*x**4 - 288.6199*x**3 + 77.1494*x**2 - 1.0438*x - 0.2981
    return l + correction*change(h)

def color_to_rgb(l,c,h, ryb=False, correction=0.0):
    if ryb:
        return hsv_ryb_rgb(h,c,l, correction)
    if correction != 0.0:
        l = light_transform(h, l, correction)
    return to_rgb(h,c,l)

def rgb_to_color(r,g,b, ryb=False):
    if ryb:
        return rgb_ryb_hsv(r,g,b)
    return from_rgb(r,g,b)

