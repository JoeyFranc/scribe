import cv2 as cv
import numpy as np
import math



def computeSkew( img ):
# REQ:  img - A greyscale opencv image object with minimal noise
# EFF:  Rotates, deskews target image with a Hough Transform, then displays result
#       Returns void
# MOD:  None
    HoughL
    

img = cv.imread('test.jpg', 0)
#cv.bitwise_not(img, img)
edges = cv.Canny(img, 50, 200)

lines = cv.HoughLines(edges, 1, np.pi/180, 200)

skew_angle = lines[0][0][0]
#skew_angle = math.atan(sum(slopes)/len(slopes))
center = img.shape[0]/2, img.shape[1]/2
R = cv.getRotationMatrix2D(center, skew_angle, 1)


new_size = [int(1.5*x) for x in img.shape]
cv.imwrite('houghlines3.jpg', cv.warpAffine(img, R, (new_size[0], new_size[1])) )

