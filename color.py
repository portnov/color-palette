from math import pi, floor
from colorsys import hsv_to_rgb, hls_to_rgb, rgb_to_hsv
import lcms

HLS=True

if HLS:
    def to_rgb(h,s,l):
        return hls_to_rgb(h,l,s)
#         return lch_to_rgb(l,s,h)
    FULL_LIGHT = 1.0
else:
    def to_rgb(h,s,l):
        return hsv_to_rgb(h,s,l)
    FULL_LIGHT = 1.0

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

def hue_transform(h):
#     h += 1./24
#     if h > 1.0:
#         h -= 1.0
    if h < 1./3:
        r = -0.9821*(h**3)+0.5647*h+0.0148
    elif h < 0.5:
        r = 18.4804*(h**3)-19.4626*(h**2)+7.0523*h-0.7060
    elif h < 2./3:
        r = -24.9604*(h**3)+45.6987*(h**2)-25.5284*h+4.7241
    else:
        r = 4.2221*(h**3)-12.6664*(h**2)+13.3817*h-3.9226
    if r > 1.0:
        r -= 1.0
    return r

def simple_mix(x1,a,x2,b):
    q = b/(a+b)
    return (1-q)*x1 + q*x2, a*q

def simple_mix_invert(x1,p,x2,q):
    if p==0.0 and q==0.0:
        return (x1+x2)/2.0, 1.0
    elif p==0.0:
        return x1, 1.0
    elif q==0.0:
        return x2, 1.0
    else:
        return simple_mix(x1,1./p, x2,1./q)

def mix_RY(qR,qY):
    h,v = simple_mix_invert(0,qR, 1./6, qY)
    return h,v

def mix_YB(qY,qB):
    h,v = simple_mix_invert(1./6,qY, 2./3,qB)
    return h,v

def mix_BR(qB,qR):
    h,v = simple_mix_invert(2./3,qB, 1.,qR)
    return h,v

def hsv_ryb_rgb(h1,s1,v1, correction = 0.0):
    if h1 < 1./3:
        q = h1*3
        h2,v2 = mix_RY(q,1-q)
    elif h1 < 2./3:
        q = (h1-1./3)*3
        h2,v2 = mix_YB(q,1-q)
    else:
        q = (h1-2./3)*3
        h2,v2 = mix_BR(q,1-q)
    l = light_transform(h2, v1*v2, correction)
    return hsv_to_rgb(h2, s1, l)

def rgb_ryb_hsv(r,g,b):
    h1,s1,v1 = rgb_to_hsv(r,g,b)
    if h1 < 1./6:
        q = h1*6
        h2,v2 = simple_mix_invert(0.,q, 1./3, 1-q)
    elif h1 < 2.3:
        q = (h-1./6)*2
        h2,v2 = simple_mix_invert(1./3,q, 2./3, 1-q)
    else:
        q = (h-2./3)*3
        h2,v2 = simple_mix_invert(2./3,q, 1.,1-q)
    return h2, s1, v2/v1

# def hsv_ryb_rgb(h,s,v, correction=0.0):
#     red = (0.8902, 0.1373, 0.0627)
#     yellow = (0.9961, 0.9961, 0.2)
#     blue = (0.0039, 0.2157, 0.7804)
#     green = (0.,0.8,0.2941)
#     if h < 1./3:
#         base = rgb_blend(red,yellow, h*3)
#     elif h < 0.5:
#         base = rgb_blend(yellow,green, (h-1./3)*6)
#     elif h < 2./3:
#         base = rgb_blend(green, blue, (h-0.5)*6)
#     else:
#         base = rgb_blend(blue,red, (h-2./3)*3)
#     h_,s_,v_ = rgb_to_hsv(*base)
#     l = light_transform(h_,v*v_, correction)
#     return hsv_to_rgb(h_,s*s_,l)

# def rgb_blend(clr1,clr2, alpha):
#     r1,g1,b1 = clr1
#     r2,g2,b2 = clr2
#     r = (1-alpha)*r1 + alpha*r2
#     g = (1-alpha)*g1 + alpha*g2
#     b = (1-alpha)*b1 + alpha*b2
#     return r,g,b
 
def light_transform(h, l, correction=0.0):
    def change(x):
#         return - 39.6429*x**5 + 115.4617*x**4- 100.8745*x**3 + 19.4957*x**2 + 5.5600*x - 0.5458
        return - 138.4962*x**5 + 351.0104*x**4 - 288.6199*x**3 + 77.1494*x**2 - 1.0438*x - 0.2981
    return l + correction*change(h)

def color_to_rgb(l,c,h, ryb=False, correction=0.0):
    if ryb:
        return hsv_ryb_rgb(h,c,l, correction)
#         h = hue_transform(h)
    if correction != 0.0:
        l = light_transform(h, l, correction)
    return to_rgb(h,c,l)

def rgb_to_color(r,g,b, ryb=False):
    if ryb:
        return rgb_ryb_hsv(r,g,b)
    return rgb_to_hsv(r,g,b)

