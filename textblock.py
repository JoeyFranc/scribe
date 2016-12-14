"""

textblock.py
By Joseph Franc
November 2016

This module contains a basic TextBlock datatype, as well as methods for
comparing the two

"""



# Constant allignment enum
LEFT   = 0
CENTER = 1
RIGHT  = 2

# Constant list-type enum
BULLET = 0
DASH   = 1
NUMBER = 2



class TextBlock(object):

    def init_values(self, tl, bl, br, tr):
    # Inits all values of a TextBlock object

        # Text
        self.text = ''

        # Bounds
        self.left  = (tl[0]+bl[0])/2
        self.right = (tr[0]+br[0])/2
        self.top   = (tl[1]+tr[1])/2
        self.bot   = (bl[1]+br[1])/2

        # Style information
        self.line = None
        self.indent = None
        self.heading = None
        self.list = None
        self.allign = LEFT

        # Actual corners KEPT FOR TESTING PURPOSES, I LIKE THE RECTANGLE
        # REPRESENTATION BUT DO WHAT YOU WILL
        self.corners = [ tl, bl, br, tr ]

    def __init__(self, *args):
    # ARGS: The TopLeft, TopRight, BottomLeft, and BottomRight coordinates
    #       of the TextBlock
    #
    # By default, text blocks are unindented, left allgined, paragraph blocks
        
        if len(args) == 1:
            corners = args[0]
            tl = tuple(corners[0])
            bl = tuple(corners[1])
            br = tuple(corners[2])
            tr = tuple(corners[3])
            self.init_values( tl,bl,br,tr )

        elif len(args) == 2:
            tl = tuple(args[0])
            bl = tuple([args[0][0],args[1][1]])
            br = tuple(args[1])
            tr = tuple([args[1][0],args[0][1]])
            self.init_values( tl,bl,br,tr )

        elif len(args) == 4:
            tl = tuple(args[0])
            bl = tuple(args[1])
            br = tuple(args[2])
            tr = tuple(args[3])
            self.init_values( tl,bl,br,tr )

        else: raise Exception('Invalid Number of arguments')

    def __repr__(self):
    # Used by print keyword.

        # Text representation of list-type
        list_type = 'n/a'
        if self.list == 0: list_type = 'BULLET'
        elif self.list == 1: list_type = 'DASH'
        elif self.list == 2: list_type = 'NUMBER'

        # Text representation of allignment
        allign = 'LEFT'
        if self.allign == 1: allign = 'CENTER'
        elif self.allign == 2: allign = 'RIGHT'

        # Return formatted version of text
        return \
        '<b:[ {0} {1} {2} {3} ] l:{8} i:{4} h:{5} l:{6} a:{7}>'.format(
            self.left, self.bot, self.right, self.top,
            self.indent, self.heading, list_type, allign, self.line
        )

    def same_style(self, tb):
    # Returns True if TextBlock TB is styled EXACTLY the same as this instance

        return self.indent == tb.indent and \
               self.heading == tb.heading and \
               self.list == tb.list and \
               self.allign == tb.allign

    def intersects( self, tb ):
    # Returns True if TextBlock TB intersects this instance of TextBlock object

        return tb.left <= self.right and self.left <= tb.right and \
               tb.top  <= self.bot   and self.top  <= tb.bot

    def contains( self, point ):
    # Returns True if Textblock instance contains pixel coordinate POINT
    
        return self.left <= point[0] and point[0] <= self.right and \
               self.top  <= point[1] and point[1] <= self.bot
