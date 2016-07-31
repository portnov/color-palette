
try:
    import Image
    import ImageStat
except ImportError:
    try:
        from PIL import Image
        from PIL import ImageStat
    except ImportError as e:
        print("Neither PIL or Pillow are available")
        raise e

from color.colors import *

def average(img):
    stat = ImageStat.Stat(img)
    avg = stat.mean
    if len(avg) == 3:
        r,g,b = avg
    elif len(avg) == 4:
        r,g,b,a = avg
    else:
        raise NotImplementedError("Support of this image format was not implemented yet")
    return Color(r,g,b)

def parse_color_table(filename, options):
    img = Image.open(filename)
    # Size of image
    W, H = img.size
    # Size of single cell
    w = (W - 2*options.border_x - (options.size_x - 1)*options.gap_x) // options.size_x
    h = (H - 2*options.border_y - (options.size_y - 1)*options.gap_y) // options.size_y

    w_gx = w + options.gap_x
    h_gy = h + options.gap_y

    colors = []

    for i in range(0, options.size_y):
        row = []
        for j in range(0, options.size_x):
            x0 = options.border_x + w_gx * j
            y0 = options.border_y + h_gy * i
            x1 = x0 + w
            y1 = y0 + h
            cell = img.crop((x0, y0, x1, y1))
            row.append(average(cell))
        colors.append(row)

    return colors


