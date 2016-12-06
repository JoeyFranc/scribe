import numpy as np
from PIL import Image
import scipy.misc
import scipy.ndimage.filters
import scipy.signal

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

if __name__ == '__main__':

    img = np.asarray(Image.open('trump.jpg').convert('RGB'))
    gray = rgb2gray(img)
    G_rst = scipy.ndimage.filters.gaussian_filter(img, 1.6,order=0, output=None,
                                            mode='reflect', cval=0.0, truncate=4.0)
    M_rst = scipy.signal.medfilt(img, kernel_size=3)

    scipy.misc.imsave('rst0.png', gray)
    scipy.misc.imsave('rst1.png', G_rst)
    scipy.misc.imsave('rst2.png', M_rst)
