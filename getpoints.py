import cv2 as cv
import numpy as np
import sys
import tbformat
import textblock as tb



class create_box:
# Functor for click callback

    def __init__(self):
        
        self.corners = []
        self.color = 255

    def __call__(self, event, x,y, flags, param):

        if event == cv.EVENT_LBUTTONDOWN:

            cv.circle(img, (x,y), 10, (self.color,0,0), -1)
            self.corners.append([x,y])

    def rectangles(self):

        rects = []
        for x in xrange( 0,len(self.corners),4 ): rects += [self.corners[x:x+4]]
        print rects
        return rects

import sys

if __name__ == '__main__':

    # Init vars
    IMG_PATH = sys.argv[1]
    x = create_box()
    img = cv.imread(IMG_PATH)
    height, width, c = img.shape
    print img.shape
    scale = max( height/1080, width/1920 )
    img = cv.resize( img, (width/scale, height/scale) )
    print img.shape
    cv.namedWindow('test')
    cv.setMouseCallback('test', x)

    # Open a window for collecting rects until ESC is hit
    while(True):

        cv.imshow('test', img)
        if cv.waitKey(20) & 0xFF == 27: break
    
    cv.destroyAllWindows()

    # Write a csv containing the rects
    csv = [ ';'.join( [','.join([str(x) for x in corner]) for corner in rect] )
          for rect in x.rectangles() ]
    f = open(sys.argv[1][sys.argv[1].rfind('/')+1:]+'.csv','w')
    for rect in csv: f.write(rect+'\n')
