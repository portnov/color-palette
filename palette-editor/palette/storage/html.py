
from os.path import exists
import sys

try:
    import cssutils
    from xml.dom import SyntaxErr
    #from tinycss import make_parser, color3
    css_support = True
except ImportError:
    css_support = False

try:
    from BeautifulSoup import BeautifulSoup as Soup, Tag
    html_support = True
except ImportError:
    html_support = False

from color.colors import *

def parse_color(s):
    try:
        c = cssutils.css.ColorValue(s)
        return c
    except SyntaxErr,e:
        print s, e
        return None

def convert_color(css_color):
    r,g,b = css_color.red, css_color.green, css_color.blue
    color = Color()
    color.setRGB((r,g,b))
    return color

def colors_dicts(html):
    """Parse HTML file and extract all mentioned colors from it.
    Returns tuple of two dictionaries:
        * Inline colors, such as in <body bgcolor=...>
        * Colors from inline <style> tag or from attached CSS file.
    """

    inline_colors = {}
    css_colors = {}

    def add_color(key, css_color, css=False, add_hex=False):
        color = convert_color(css_color)
        for k,v in css_colors.iteritems():
            if v.getRGB() == color.getRGB():
                return
        for k,v in inline_colors.iteritems():
            if v.getRGB() == color.getRGB():
                return
        if add_hex:
            key = key + "_" + color.hex()[1:]
        if css:
            css_colors[key] = color
        else:
            inline_colors[key] = color

    def tidy(s):
        for x in ".-()>* ":
            s = s.replace(x, "_")
        return s
    
    #html = open(filename).read()
    soup = Soup(html)
    for tag, name, attrs in [(tag, tag.name, tag.attrs) for tag in soup.findChildren()]:
        #print name
        if name == "style":
            css = None
            if not attrs:
                # Inline CSS
                css_text = tag.text
                css = cssutils.parseString(css_text)
            elif "href" in tag:
                # CSS in separate file
                css_filename = tag["href"]
                if exists(css_filename):
                    css = cssutils.parseFile(css_filename)

            if css:
                for rule in css:
                    if rule.type == rule.STYLE_RULE:
                        for property in rule.style:
                            for val in property.propertyValue:
                                if not isinstance(val, cssutils.css.ColorValue):
                                    continue

                                selector = rule.selectorText
                                cname = "_".join(["style", "inline", selector, property.name.replace("-","_")])
                                add_color(cname, val, css=True)
            continue

        for key, value in attrs:
            if key in [u"color", u"bgcolor", u"fgcolor"]:
                cname = "_".join([name, key])
                css_color = parse_color(value)
                if not isinstance(css_color, cssutils.css.ColorValue):
                    continue
                add_color(cname, css_color, False, True)

            if key == u"style":
                style = cssutils.parseStyle(value)
                for property in style.getProperties():
                    for val in property.propertyValue:
                        if not isinstance(val, cssutils.css.ColorValue):
                            continue
                        cname = "_".join([name, "style", property.name.replace("-","_")])
                        add_color(cname, val, False, True)

    return (inline_colors, css_colors)

def extract_css(html):
    soup = Soup(html)

    inline_css = None
    separate_css = None

    found = False
    for tag in soup.findAll(u"style"):
        name = tag.name
        attrs = tag.attrs
        if not attrs:
            # Inline CSS
            css_text = tag.text
            inline_css = cssutils.parseString(css_text)
            found = True
        elif "href" in tag:
            # CSS in separate file
            css_filename = tag["href"]
            if exists(css_filename):
                separate_css = cssutils.parseFile(css_filename)
                found = True
        if found:
            tag.extract()
            break

    return (soup, inline_css, separate_css)

def add_inline_css(soup, css):
    style = Tag(soup, "style")
    style.string = css.cssText
    if soup.html.head is None:
        head = Tag(soup, "head")
        soup.html.insert(0, head)
    soup.html.head.append(style)
    return soup

def change_css_colors(css, old_colors, new_colors):

    rev = dict([(v.hex(),k) for k,v in old_colors.iteritems()])

    for rule in css:
        if rule.type == rule.STYLE_RULE:
            for property in rule.style:
                for val in property.propertyValue:
                    if not isinstance(val, cssutils.css.ColorValue):
                        continue

                    #selector = rule.selectorText
                    #cname = "_".join(["style", "inline", selector, property.name.replace("-","_")])
                    old_color = convert_color(val).hex()
                    cname = rev[old_color]
                    if cname in new_colors:
                        new_color = new_colors[cname]
                        new_prop = cssutils.css.Property(name=property.name, value=new_color.hex())
                        rule.style.setProperty(new_prop)
                        old_colors[cname] = new_colors
    return css

def change_inline_colors(soup, old_colors, new_colors):

    rev = dict([(v.hex(),k) for k,v in old_colors.iteritems()])

    #soup = Soup(html)
    for tag, name, attrs in [(tag, tag.name, tag.attrs) for tag in soup.findChildren()]:
        for key, value in attrs:
            if key in [u"color", u"bgcolor", u"fgcolor"]:
                #cname = "_".join([name, key, value[1:]])
                css_color = parse_color(value)
                if not isinstance(css_color, cssutils.css.ColorValue):
                    continue
                old_color = convert_color(css_color).hex()
                cname = rev[old_color]
                if cname in new_colors:
                    new_color = new_colors[cname]
                    tag[key] = new_color.hex()
                    old_colors[cname] = new_color

            if key == u"style":
                style = cssutils.parseStyle(value)
                for property in style.getProperties():
                    for i, val in enumerate(property.propertyValue):
                        if not isinstance(val, cssutils.css.ColorValue):
                            continue
                        old_color = convert_color(val).hex()
                        cname = rev[old_color]
                        #cname = "_".join([name, "style", property.name.replace("-","_"), old_color.hex()[1:]])
                        #print cname
                        if cname in new_colors:
                            #print cname
                            new_color = new_colors[cname]
                            new_prop = cssutils.css.Property(name=property.name, value=new_color.hex())
                            style.setProperty(new_prop)
                            old_colors[cname] = new_color
                tag[key] = style.cssText

    return soup

def merge_css(css1, css2):
    if css1 is None and css2 is None:
        return None
    if css1 is None:
        return css2
    if css2 is None:
        return css1
    return cssutils.parseString(css1.cssText + "\n" + css2.cssText)

