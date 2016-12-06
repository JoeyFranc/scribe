import cv2 as cv
import block
import tbformat
import getTextLineDots
import grayscale
import orient
import textblock



# The whole program
if __name__ == '__main__':

    pages = []
    for file_name in sys.argv[1:]:

        # Open an image
        img = cv.imread(file_name)

        # Preprocess
        img = rgb2gray.rgb2gray(img)
        img = orient.fixSkew(img)
        
        # Doc Layout analysis
        white_spaces = recWhiteSpace.recWhiteSpace(img)
        letters = getTextLineDots.getTextLineBox(img)
        text_lines = getLines.get_constrained_lines(letters, obstacles)
        tbformat.format(text_lines)

        # Optical Character Recognition
        # Make a Latex file

    print pages
