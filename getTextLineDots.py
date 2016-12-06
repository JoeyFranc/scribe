import cv2

'''
Find bottom points of each line of text that could do robust linear regression on
Dots are shown in green circles (r = 1 pixel)
'''

def getTextLineBox(gray):

    _,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV) # threshold
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    dilated = cv2.dilate(thresh,kernel,iterations = 2) # need calibration on this for different format
    cv2.imwrite("out.jpg", dilated)
    out, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # get contours
    pts = []
    # for each contour found, draw a rectangle around it on original image
    for contour in contours:
        # get rectangle bounding contour
        [x,y,w,h] = cv2.boundingRect(contour)   # can return this box here

        # branch and bound


        # # discard areas that are too small
        if h<8 or w<8:
            continue

        for i in range(x, x+w, 1):
            #cv2.circle(image, (x+i,y+h), 1, (0,255,0))  # illustrate
            pts.append((x+i,y+h))

    return pts
