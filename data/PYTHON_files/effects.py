from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt

from PyQt5.QtGui import QPixmap
import numpy as np

# Convert PIL Image to QPixmap
def convert_to_qt(image):
    return QPixmap.fromImage(ImageQt(image).copy())


#--------------------------------------------------------
filters = {
    "Blur": ImageFilter.BLUR,
    "Contour": ImageFilter.CONTOUR,
    "Detail": ImageFilter.DETAIL,
    "Edge Enchance": ImageFilter.EDGE_ENHANCE,
    "Edge Enchance More": ImageFilter.EDGE_ENHANCE_MORE,
    "Emboss": ImageFilter.EMBOSS,
    "Find Edges": ImageFilter.FIND_EDGES,
    "Sharpen": ImageFilter.SHARPEN,
    "Smooth": ImageFilter.SMOOTH,
    "Smooth More": ImageFilter.SMOOTH_MORE,
}


def preset_filters(im, filter0):
    im = im.filter(filter0)
    return im


#--------------------------------------------------------
def box_blur(im, radius=5):
    im = im.filter(ImageFilter.BoxBlur(radius))
    return im


def gaussian_blur(im, radius=5):
    im = im.filter(ImageFilter.GaussianBlur(radius))
    return im


def unsharp_mask(im, radius=2, percent=300, threshold=3):
    filter1 = ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold)
    im = im.filter(filter1)
    return im

#--------------------------------------------------------


def channels(im, rgb):
    rgb = tuple(map(lambda x: x / 50, rgb))
    im = im.convert("RGB")

    Matrix = (
        rgb[0],   0,  0, 0, 
        0,   rgb[1],  0, 0, 
        0,     0,  rgb[2], 0
    ) 

    im = im.convert("RGB", Matrix) 
    return im


def transparensy(im, alpha):
    im_rgb = im
    im_rgba = im_rgb.copy()
    im_rgba.putalpha(alpha)
    return im_rgba


#--------------------------------------------------------

def stereo_effect(im, delta):
    # creates a stereo effect
    delta //= 2
    pixels_im = im.load()
    new_im = im.copy()
    pixels_new_im = new_im.load()
    x, y = im.size
    for i in range(x):
        for j in range(y):
            colors = list(pixels_im[i, j])
            colors[0] = pixels_im[i - delta, j][0]
            pixels_new_im[i, j] = tuple(colors)
    return new_im


def lightest_pixel(pixels, i, j, x, y, area):
    # changes the color of a pixel to the color of the lightest pixel in the near area
    r = g = b = 0
    for row in range(i - area, i + area):
        for col in range(j - area, j + area):
            if 0 <= row < x and 0 <= col < y:
                if sum(pixels[row, col]) > r + g + b:
                    r, g, b = pixels[row, col]
    return r, g, b


def lightest_pixel_effect(im, area=5):
    im = im.convert("RGB")
    pixels_im = im.load()
    new_im = im.copy()
    pixels_new_im = new_im.load()
    x, y = im.size
    for i in range(x):
        for j in range(y):
            pixels_new_im[i, j] = lightest_pixel(pixels_im, i, j, x, y, area)
    return new_im


def black_and_white_effect(im):
    im = im.convert("L")
    im = im.convert("RGB")
    return im


def negative_effect(im):
    img_data = np.array(im)
    img_reversed_data = 255 - img_data
    img_reversed = Image.fromarray(img_reversed_data)
    return img_reversed


def two_colors(im):
    new_im = im.copy()
    pixels_new_im = new_im.load()
    x, y = im.size
    for i in range(x):
        for j in range(y):
            r, g, b = pixels_new_im[i, j]
            pixels_new_im[i, j] = r, g, b
    return new_im