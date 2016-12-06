import cv2 as cv
import numpy as np
import math



def fixSkew( img ):
# REQ:  img - A greyscale opencv image object with minimal noise
# EFF:  Rotates, deskews target image with a Hough Transform, then returns result
# MOD:  None

    img = cv.imread('test.jpg', 0)
    #cv.bitwise_not(img, img)
    edges = cv.Canny(img, 50, 200)
    lines = cv.HoughLines(edges, 1, np.pi/180, 200)
    skew_angle = lines[0][0][0]
    center = img.shape[0]/2, img.shape[1]/2
    R = cv.getRotationMatrix2D(center, skew_angle, 1)



return cv.warpAffine(img, R, (new_size[0], new_size[1]))
