import cv2 as cv
import numpy as np
import sys
from textblock import TextBlock
from block import TextBlock as Obstacle
from preprocess import preprocess
from orient import fixSkew
from recTextBlock import recTextBlocks
from recWhiteSpace import recWhiteSpace
from components import get_components
from getLines import get_lines
from postprocess import post_process
import tbformat



def get_line_params(characters):
# Returns approximate x_height and descender line distance of characters

    x_height = np.median( [(h) for (x,y,w,h) in characters] )
    d_line   = x_height/2
    return (x_height, d_line)

pages = []
for file_name in sys.argv[1:]:

    # Preprocess
    image = cv.imread(file_name)
    img = preprocess(image)
    img = fixSkew(img)
    
    # Page Segmentation
    img_h,img_w = img.shape
    obstacles = recTextBlocks(img)
    white_spaces = recWhiteSpace(Obstacle(0,0,img_w,img_h), obstacles)
    white_spaces = [TextBlock((obs.x,obs.y), (obs.x+obs.w,obs.y+obs.h))
                    for obs in white_spaces]
    characters = get_components(img)
    x_height, d_line = get_line_params(characters)
    char_points = [ (np.array([r.x+r.w/2, r.y+r.h]), r) for r in characters ]
    print len(char_points), 'points'
#    for (x,y,w,h) in characters: cv.rectangle(img, (x,y), (x+w,y+h), (0,0,255),2)
    for p in char_points: cv.circle(img, tuple(p[0]),3,(0,255,0),2)
    text_lines = get_lines((img_h,img_w), char_points, white_spaces, (x_height, d_line))
    print len(text_lines), 'text lines'

    # Document Layout Analysis
    text_lines, text_blocks = post_process(text_lines, char_points, x_height, d_line)
    print len(text_blocks), 'lines after pruning'
    # Draw the lines gotten by this algorithm
    for block in text_blocks: block.draw(img)
    for (quality,(theta,r),pts) in text_lines:
        unit = np.array([np.cos(theta),np.sin(theta)])
        dist0 = np.dot(unit, pts[0][0]-(r*unit) )
        dist1 = np.dot(unit, pts[-1][0]-(r*unit) )
        cv.line(img, tuple((pts[0][0]-dist0*unit).astype(int)), 
            tuple((pts[-1][0]-dist1*unit).astype(int)), (0,0,255), 1)

    cv.imwrite('final.jpg', img)
    #tbformat.format(text_lines)

    # Optical Character Recognition
    # Make a Latex file
