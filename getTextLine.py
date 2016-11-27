import cv2

'''
Given an image, it can identify the boxes of textlines contained
Need calibrations on iterations for different inputs
Works best for bulletlists and other highly separated texts
'''

def getTextLineBox(infileName):
    image = cv2.imread(infileName)
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) # grayscale
    _,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV) # threshold
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
	# preprocess
    dilated = cv2.dilate(thresh,kernel,iterations = 14) # need calibration on this for different format
    out, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # get contours

    # for each contour found, draw a rectangle around it on original image
    for contour in contours:
        # get rectangle bounding contour
        [x,y,w,h] = cv2.boundingRect(contour)   # can return this box here
        print w,h

        # branch and bound

        # discard areas that are too large
        if h>400 and w>400:
            continue
        #
        # discard areas that are too small
        if h<40 or w<40:
            continue

        # draw rectangle around contour on original image
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,255),2)

    # write original image with added contours to disk
    cv2.imwrite("contoured.jpg", image)

getTextLineBox("testBullets.png")
