'''
Given an input image preprocess the image
Apply grayscale, gaussian_filter, median filter
'''
import numpy as np
from PIL import Image
import scipy.misc
import scipy.ndimage.filters
import scipy.signal

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def preprocess(img):

    G_rst = scipy.ndimage.filters.gaussian_filter(rgb2gray(img), 1,order=0, output=None,
                                        mode='reflect', cval=0.0, truncate=4.0)
    # apply median filter
    M_rst = scipy.signal.medfilt(G_rst, kernel_size=5)
    return np.uint8(np.around(M_rst))

if __name__ == '__main__':
    out = preprocess('handwrite.png')
    scipy.misc.imsave('preRest.png', out)
