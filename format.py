"""

format.py
By Joseph Franc
November 2016

This module contains all functions needed to organize text blocks into
groups that are likewise formatted.

"""



import textblock as tb



class value_cmp:
# Textblock comparitor functor for the sort function.
# Values compared are the values returned by function get_value

    def __init__(self, get_value): self.get_value = get_value

    def __call__(self, lhs, rhs):
    # What happens when object is called as function

        if self.get_value(lhs) < self.get_value(rhs): return -1
        elif self.get_value(lhs) == self.get_value(rhs): return 0
        else: return 1

def get_indent_value( text_block ): return text_block.left
# Returns the left bound of the text_block

def get_heading_value( text_block ): return text_block.top - text_block.bot
# Returns the negative vertical size (in pixels) of the text line
# NOTE: Values are negative on purpose

def add_indent_value( text_block, value ): text_block.indent = value
# Changes a TextBlock's INDENT variable to VALUE

def add_heading_value( text_block, value ): text_block.heading = value
# Change a TextBlock's HEADING variable to VALUE


def group_values( text_blocks, residual, get_value, add_value ):
# Takes a list of textblock objects TEXT_BLOCKS and modifies their indent
# level attribute.  Groups blocks into seemingly same indent levels using 
# their left bounds and an incremental point fitting method.
#
# The RESIDUAL is the maximum distance between indent centroids.
#
# This function is used for adding heading and indent values to text-blocks

    # Start by sorting the text_blocks from smallest left bound to largest
    sorted( text_blocks, cmp = value_cmp(get_value) )

    lvl = 1 #Current group level
    grouped = 0 #Number of grouped blocks
    while grouped != len(text_blocks):
    # Group every item in text_blocks

        sum_value = 0 #Sum of measured values of current level
        group_size = 0 #Number of blocks in this group
        for block in text_blocks[grouped:]:
        # Add ungrouped blocks until the residual grows too large 

            sum_value += get_value(block)
            mean = sum_value / (group_size+1)
            
            # Adding this point puts point outside of residual range
            if text_blocks[grouped].left < mean - residual or \
               mean + residual < block.left: break

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

def get_geometric_order( text_blocks, obstacles ):
    pass

def get_allignment( text_blocks ):
# REQ:  text_blocks are in geometric order
    return 1

def format( text_blocks ):

    text_blocks = sys.args[1:]
    group_values( text_blocks, 10, get_indent_value, add_indent_value )
    group_values( text_blocks, 5 , get_heading_value, add_heading_value )
