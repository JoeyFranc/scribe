import cv2 as cv
from preprocess import preprocess



def isValid( (x,y,w,h), (im_h, im_w)):
# Returns true if this rect meets the criterion for being a connected component

    return \
    w > 5 and h > 5 and \
    ( (1 <= w/h and w/h < 8) or (1 <= h/w and h/w < 8) ) and \
    h < im_h/4 and w < im_w/4 and \
    (h > im_h/500 or w > im_w/500)

def get_components(img):
# EFF: Returns the bounding rectangles of each approximate letter in the image
# img is a black and white opencv image that has been filtered

    # Binarize the image using comparing 
    # a pixel to the its value in a gaussian kernel
    binary = cv.adaptiveThreshold( img,255,
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

    return rects


import sys
if __name__ == '__main__':

    orig = cv.imread(sys.argv[1])
    img = preprocess(sys.argv[1])
    contours = get_components(img)
    for (x,y,w,h) in contours: cv.rectangle(orig, (x,y), (x+w,y+h), (0,0,255))
    cv.imwrite('test.jpg', orig)
