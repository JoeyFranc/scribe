import cv2 as cv
import numpy as np
import math



#def get_max(edges):
## Returns the most voted for line
#
#    
#    lb = 100
#    thresh = 600
#    rb = 1100
#    lines = cv.HoughLines(edges, 1, np.pi/180, thresh)
#    if lines is None: fewest = (0, None)
#    else: fewest = (len(lines), lines[0][0][1])
#    while fewest[0] != 1 and lb != rb:
#
#        # Get more lines
#        lines = cv.HoughLines(edges,1,np.pi/180,thresh)
#
#        # Threshold is too high
#        if lines is None:
#
#            lb = thresh
#            thresh = (lb+rb)/2
#
#        # Threshhold is right or too low
#        else:
#
#            # Check if this is the new optimal set of lines
#            if len(lines) < fewest[0]: fewest = (len(lines), lines[0][0][1])
#            rb = thresh
#            thresh = (lb+rb)/2
#
#    return fewest[1]


def fixSkew( img ):
# REQ:  img - A greyscale opencv image object with minimal noise
# EFF:  Rotates, deskews target image with a Hough Transform, then returns result
# MOD:  None

    # Perform edge detection and find the strongest edge
    edges = cv.Canny(img, 50, 200)
    skew_angle = cv.HoughLines(edges, 1, np.pi/180, 1)[0][0][1]

    # Calculate the pivot, new dimensions, and rotation matrix for a new image
    h,w = img.shape
    cos = np.cos(skew_angle)
    sin = np.sin(skew_angle)
    center = (h-h*sin*cos, h*sin**2)
    ab = np.absolute
    new_size = ( int(ab(w*cos)+ab(h*sin)), int(ab(w*sin)+ab(h*cos)) )
    R = cv.getRotationMatrix2D(center, skew_angle*180/np.pi, 1)

    return cv.warpAffine(img, R, new_size)

import sys
if __name__ == '__main__':

    img = cv.imread(sys.argv[1],0)
    cv.imwrite('rotatedImage.jpg', fixSkew(img))
    cv.waitKey()
