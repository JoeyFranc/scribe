import numpy as np
import cv2
import PIL
import pytesseract
import textract
import block
from recTextBlock import *

img_name = './handwrite.png'
im = cv2.imread(img_name, 0)
im_blur = cv2.GaussianBlur(im, (5,5), 0)
thre_val, im_thre = cv2.threshold(im_blur, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

C_h = 50
rows, cols = im_thre.shape
im_h = np.copy(im_thre)
for i in range(rows):
    zero_start = -1
    for j in range(cols):
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

out, ctrs, hierarchy = cv2.findContours(im_h.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
text_extracted = []
for ctr in ctrs:
    x,y,w,h = cv2.boundingRect(ctr)
    #cv2.rectangle(im_thre, (x,y), (x+w, y+h), (0,255,0), 2)
    im_region = PIL.Image.fromarray(im_thre[y:y+h, x:x+w])
    # text = pytesseract.image_to_string(im_region)
    text = textract.process(im_region, method='tesseract')
    text_extracted.append(text)
print (text_extracted)
#cv2.imshow('im', im_thre)
#cv2.waitKey(0)
