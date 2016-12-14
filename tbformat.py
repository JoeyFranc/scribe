"""

format.py
By Joseph Franc
November 2016

This module contains all functions needed to organize text blocks into
groups that are likewise formatted.

"""


from textblock import TextBlock



def get_indent_value( text_block ): return text_block.left
# Returns the left bound of the text_block

def get_heading_value( text_block ): return text_block.bot - text_block.top
# Returns the negative vertical size (in pixels) of the text line
# NOTE: Values are negative on purpose

def seperated(lhs,rhs, obstacles):
# Returns true if the two textblocks are seperated by an obstacle in

    # Check and see if an obstacle is in the way
    for obstacle in obstacles:

        if obstacle.top >= lhs.top and obstacle.top >= rhs.top \
        and lhs.bot <= obstacle.bot and rhs.bot <= obstacle.bot \
        and lhs.right < obstacle.left and obstacle.right < rhs.left:

            # There is an obstacle between these lines
            return True

    return False

def cmp_geometric( lhs, rhs ):

    def __init__(self, obstacles): self.obs = osbtacles

    def __call__(self, lhs,rhs):

        # Always read lhs first if it's to the left of an obstacle
        # rhs is to the right of
        if seperated(lhs,rhs, self.obs): return -1

        if lhs.line < rhs.line: return -1
        elif lhs.line == rhs.line:

            if lhs.left < rhs.left: return -1
            elif lhs.left == rhs.left: return 0

        return 1

def add_indent_value( text_block, value ): text_block.indent = value
# Changes a TextBlock's INDENT variable to VALUE

def add_heading_value( text_block, value ): text_block.heading = value
# Change a TextBlock's HEADING variable to VALUE

def add_line_value( text_block , value ): text_block.line = value

#def get_allignment( text_blocks, obstacles ):
## REQ:  text_blocks are in geometric order
## EFF:  Adds the allignment to each text_block
#
#    # Divide text_blocks into paragraphs
#
#    for paragraph in paragraphs:
#
#        # Special case: orphaned, indented lines
#        if len(paragraph) == 1 and paragraph[0].indent != 1:
#
#            # If the center of the block is closer to the margin or 
#            # the gutter to its immediate left, center allign it
#            center = (paragraph[0].left+paragraph[0].right)/2
#            if not obstacle: obstacle = 0
#            if abs(center-PAPER_WIDTH/2) < abs(center-obstacle):
#                pass
#
#        initial_indent = paragraph[0].indent
#
#        for block in paragraph:
#
#            if block.left != initial_indent+1 and block.left !=initial_indent-1:
#
#                try_allign_center( paragraph )
#                
#
#        left_bound = initial_indent
#        right_bound = initial_indent
#
#        # Find the 
#        for block in paragraph:
#
#            if block.indent == initial_indent+1:
#
#                right_bound += 1
#                break
#
#            if block.indent == initial_indent-1:
#
#                left_bound -= 1
#                break

def group_values( text_blocks, threshold, get_value, add_value, key_functor ):
# Takes a list of textblock objects TEXT_BLOCKS and modifies their indent
# level attribute.  Groups blocks into seemingly same indent levels using 
# their left bounds and an incremental point fitting method.
#
# The THRESHOLD is the maximum distance between indent centroids.
#
# This function is used for adding heading and indent values to text-blocks

    # Idiot test: only one text block
    if len( text_blocks ) < 2: raise BaseException('REQUIRES 2+ textblocks')

    # Start by sorting the text_blocks from smallest left bound to largest
    sorted( text_blocks, key=key_functor )

    lvl = 1 #Current group level
    grouped = 0 #Number of grouped blocks
    while grouped != len(text_blocks):
    # Group every item in text_blocks

        sum_value = 0 #Sum of measured values of current level
        group_size = 0 #Number of blocks in this group
        for block in text_blocks[grouped:]:
        # Add ungrouped blocks until the threshold grows too large 
            
            sum_value += get_value(block)
            mean = sum_value / (group_size+1)
            
            # Adding this point puts point outside of threshold range
            if get_value(text_blocks[grouped]) < mean - threshold or \
               mean + threshold < get_value(block): break

            # TODO: Add a 'lone point' condition where outliars at 
            # the beginning of the dataset can be partitioned into their
            # own group

            else:
            # Otherwise, adding this point to the group is fine. Check next
                group_size += 1
                add_value(block, lvl)

        # Add new points to the grouped area
        grouped += group_size
        lvl += 1



def normalize_headings(text_blocks):
# REQ:  text_blocks are sorted by heading
# EFF:  Changes the most common block and smaller blocks to paragraphs

    heading = 1
    headings = []
    paragraph = 0
    while sum(headings) < len(text_blocks):
        
        # Count text_blocks with this heading
        while text_blocks[headings[-1]+i] == heading: i+=1
        # Remember how many blocks had this heading
        headings += [i]
        # Mark new most popular heading level
        if headings[paragraph] < headings[-1]: paragraph = heading-1
        # Iterate to next heading
        heading += 1

    # Change all smaller headings to paragraphs
    new_heading = paragraph
    heading_lines = sum(headings[:paragraph])
    for block in text_blocks[heading_lines:]: block.heading = None

def sort_geometric_order( text_blocks, obstacles ):
    
    functor = cmp_geometric(obstacles)
    sort( text_blocks, cmp=functor )

def format( text_blocks, img_height, img_width ):

    # TODO: More eloquent way of calculating Threshhold values
    THRESH_H = img_width / 20
    THRESH_V = img_height / 80

    # Get indent values
    key_functor = lambda block: get_indent_value(block)
    group_values( text_blocks,THRESH_H,key_functor,add_indent_value,key_functor)
    # Get heading values
    key_functor = lambda block: -get_heading_value(block)
    group_values(text_blocks,THRESH_V,get_heading_value,add_heading_value,key_functor)
    # Get line values
    key_functor = lambda block: (block.top+block.bottom)/2
    group_values(text_blocks,THRESH_V,key_functor,add_line_value,key_functor)
    # Normalize heading values (most common heading is 0)
    normalize_headings(text_blocks)
    # Sort text lines into geometric order using obstacles
    sort_geometric_order(text_blocks, obstacles)



if __name__ == '__main__':

    # Get the textblocks from a .csv
    f = open(sys.argv[1])
    text_blocks = \
    [ TextBlock([[int(c) for c in p.split(',')] for p in line.split(';')]) for line in f ]
    # Format what's in the .csv
    format( text_blocks )

    print text_blocks