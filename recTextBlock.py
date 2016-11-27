import cv2
import numpy as np
import block

def recTextBlocks(img_name):
    # implement RLSA
    im = cv2.imread(img_name, 0)
    im_blur = cv2.GaussianBlur(im, (5,5), 0)
    thre_val, im_thre = cv2.threshold(im_blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # apply RLSA on binary images
    C_h = 50
    C_v = 30

    rows, cols = im_thre.shape
    # horizontal
    im_h = im_thre
    for i in xrange(rows):
        zero_start = -1
        for j in xrange(cols):
            if im_h[i,j] == 255:
                if zero_start != -1:
                    zero_length = j - zero_start
                    # change the zeros to one
                    if zero_length <= C_h:
                        im_h[i, zero_start:j] = 255
                    zero_start = -1
            else:
                if zero_start == -1:
                    zero_start = j

    # vertical
    im_v = im_thre
    for j in xrange(cols):
        zero_start = -1
        for i in xrange(rows):
            if im_v[i,j] == 255:
                if zero_start != -1:
                    zero_length = i - zero_start
                    # change the zeros to one
                    if zero_length <= C_v:
                        im_v[zero_start:i, j] = 255
                    zero_start = -1
            else:
                if zero_start == -1:
                    zero_start = i

    # combine
    im_thre = np.logical_and(im_h, im_v)
    im_thre = im_thre * 255

    # find contours
    ctrs, hierarchy = cv2.findContours(im_thre.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    obstacles = []
    for ctr in ctrs:
        x,y,w,h = cv2.boundingRect(ctr)
        obstacles.append(block.TextBlock(x,y,w,h))

    # return recognized rectangles for whitespace recognition
    return obstacles

if __name__ == "__main__":
    img_name = "./test/test2.png"
    recTextBlocks(img_name)
