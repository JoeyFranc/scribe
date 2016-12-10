import cv2
import numpy as np
import math
import block

from heapq import *
from recTextBlock import *

def area(bound):
    return bound.w * bound.h

# need improvement
def pickPivot(bound, rectangles):
    mid_x = bound.x + w / 2
    mid_y = bound.y + h / 2
    min_dist = -1
    for rect in rectangles:
        dist = math.sqrt((rect.x - mid_x)**2 + (rect.y - mid_y)**2)
        if min_dist == -1 or dist < min_dist:
            pivot = rect
            min_dist = dist
    return pivot

def overlap(rect_l, rect_r):
    # easy usage
    if rect_r == None:
        return False

    # check width
    if rect_l.x < rect_r.x:
        det_w = rect_l.w
    else:
        det_w = rect_r.w
    check_w = abs(rect_l.x - rect_r.x) < det_w

    # check height
    if rect_l.y < rect_r.y:
        det_h = rect_l.h
    else:
        det_h = rect_r.h
    check_h = abs(rect_l.y - rect_r.y) < det_h

    return check_w and check_h


def recWhiteSpace(bound, rectangles):
    white_spaces = []
    new_whitespace = None
    pq = []
    heappush(pq, (-area(bound), bound, rectangles))
    # loop until white space found
    while pq:
        q, b, obstacles = heappop(pq)
        if q > 0:
            break
        if not obstacles:
            if b.h / b.w < 3: continue
            white_spaces.append(b)
            if len(white_spaces) == 10:
                break
            new_whitespace = b
        else:
            if overlap(b, new_whitespace) and new_whitespace not in obstacles:
                obstacles.append(new_whitespace)

            pivot = pickPivot(b, obstacles)
            # four rectangles generated around the pivot
            rect_l = block.TextBlock(b.x, b.y, pivot.x-b.x, b.h)
            rect_r = block.TextBlock(pivot.x+pivot.w, b.y, \
                                         b.w-pivot.w-pivot.x+b.x, b.h)
            rect_u = block.TextBlock(b.x, b.y, b.w, pivot.y-b.y)
            rect_d = block.TextBlock(b.x, pivot.y+pivot.h, \
                                         b.w, b.h-pivot.h-pivot.y+b.y)
            subrects = [rect_l, rect_r, rect_u, rect_d]
            # check through subrects
            for sub_b in subrects:
                sub_q = area(sub_b)
                sub_obstacles = [ob for ob in obstacles if overlap(sub_b, ob)]
                heappush(pq, (-sub_q, sub_b, sub_obstacles))

    return white_spaces

if __name__ == "__main__":
    img_name = "./white.png"
    im = cv2.imread(img_name, 0)
    h,w = im.shape
    obstacles = recTextBlocks(img_name)
    white_spaces = recWhiteSpace(block.TextBlock(0,0,w,h), obstacles)

    # draw the white spaces
    for white_space in white_spaces:
        x = white_space.x
        y = white_space.y
        w = white_space.w
        h = white_space.h
        cv2.rectangle(im, (x,y), (x+w, y+h), (0,255,0), 2)

    cv2.imwrite("result.png", im)
    #cv2.imshow('im', im)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
