import cv2 as cv
import numpy as np
from preprocess import preprocess



class CharRect(tuple):

    def __init__(self, (x,y,w,h)):

        tuple.__init__(self,x,y,w,h)
        self.x = x
        self.y = y
        self.w = w
        self.h = h

def extends((lx,ly,lw,lh), (rx,ry,rw,rh)):
# Returns true if left rect intersects the right rect, but
# the right rect is not a subset of the left

    return \
    ( (lx <= rx and rx < lx+lw) or (rx <= lx and lx < rx+rw) ) and \
    ( (ly <= ry and ry < ly+lh) or (ry <= ly and ly < ry+rh) ) and \
    not (lx < rx and ly < ry and rx+rw < lx+lw and ry+rh < ly+lh)

def merge((lx,ly,lw,lh), (rx,ry,rw,rh)):
# Returns the combination of the two rects

    x = min(lx,rx)
    y = min(ly,ry)
    w = max(lx+lw,rx+rw) - x
    h = max(ly+rh,ry+rh) - y
    return (x,y,w,h)

def isValid( (x,y,w,h), (im_h, im_w)):
# Returns true if this rect meets the criterion for being a connected component

    return \
    w > 8 and h > 8 and \
    ( (1 <= w/h and w/h < 8) or (1 <= h/w and h/w < 8) ) and \
    h < im_h/4 and w < im_w/4 # and \
    #(h > im_h/500 or w > im_w/500)

def inRange( median, value, rb=8 ):
    
    return 0.5*median < value and value < rb*median

def get_components(img):
# EFF: Returns the bounding rectangles of each approximate letter in the image
# img is a black and white opencv image that has been filtered

    # Binarize the image using comparing 
    # a pixel to the its value in a gaussian kernel
    binary = cv.adaptiveThreshold( img, 255,
        cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 10 )
    # Get the connected components in the binarized image
    _,contours,hierarchy = cv.findContours(binary, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
    # Only get outter rings of a certain length
    rects = []
    for i in xrange(len(contours)):

        # This contour is not a hole, try to add it
        if hierarchy[0][i][3] >= 0:

            rect = cv.boundingRect(contours[i])
            if isValid(rect, img.shape): rects += [rect]

    h_median = np.median( [h for (x,y,w,h) in rects] )
    w_median = np.median( [w for (x,y,w,h) in rects] )

    #rects = [rect for rect in rects
    #        if inRange(h_median, rect[-1]) ]#or inRange(w_median, rect[-2], 3)]

    #final = []
    #for reject in rejected:
    #    for rect in rects:
    #        if extends(reject, rect):
    #            
    #            final += [merge(reject, rect)]
    #            rects.remove(rect)

    return [CharRect(r) for r in rects]


import sys
if __name__ == '__main__':

    orig = cv.imread(sys.argv[1])
    img = preprocess(orig)
    contours = get_components(img)
    for (x,y,w,h) in contours: cv.rectangle(orig, (x,y), (x+w,y+h), (0,0,255))
    cv.imwrite('test.jpg', orig)
