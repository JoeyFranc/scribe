import textblock

'''
Convert the raw text (under textblock ADT) into LaTex encoded string
Output an .tex file with the encoded string
'''



# some useful LaTex MACRO
TITLE = '\\'+'title'                        # title/heading
BULLET_BEGIN = '\\'+'begin{itemize}'        # begin of a bullet list (bullet)
BULLET_END = '\\'+'end{itemize}'            # end of a bullet list
NUMBER_LIST_BEGIN = '\\'+'begin{enumerate}' # begin of a numbered list
NUMBER_LIST_END = '\\'+'end{enumerate}'     # end of a numbered list
DASH_LABEL = '[label='+'\\textendash]'      # label for dash bullet list (-)
ITEM_LABEL = '\\'+'item '                   # item to enumerate
RIGHT_BEGIN = '\\'+ 'begin{flushright}'
RIGHT_END = '\\'+'end{flushright}'
CENTER_BEGIN = '\\'+'begin{center}'
CENTER_END = '\\'+'end{center}'
LEFT_BEGIN = '\\'+ 'begin{flushleft}'
LEFT_END = '\\'+'end{flushleft}'
SEC_HEADING_ONE = '\\'+'section*'
SEC_HEADING_TWO = '\\'+'subsection*'
SEC_HEADING_THREE = '\\'+'subsubsection*'
BEGIN = '\\'+'begin{document}\n'
END = '\\'+'end{document}\n'
DOC_CLASS = '\\' + 'documentclass[a4paper,12pt]{article}\n'
PACKAGES = '\\'+'usepackage[margin=1in]{geometry}\n'+
           '\\'+'usepackage{enumitem}\n'


# assume the block passed is of heading type
def makeTitle(blockIn):
    outStr = ''
    contentStr = blockIn.text
    outStr = TITLE + '{' + contentStr + '}\n'
    return outStr

# pass in a list of blocks
def makeList(blocksIn):
    outStr= ''
    endType = -1
    # add list begin
    if blocksIn[0].list == 0:       # bullet
        outStr += BULLET_BEGIN + '\n'
        endType = 0
    elif blocksIn[0].list == 1:  # dash
        outStr += BULLET_BEGIN + DASH_LABEL + '\n'
        endType = 0
    elif blcoksIn[0].list == 2:  # number
        outStr += NUMBER_LIST_BEGIN + '\n'
        endType = 1

    # add item
    for block in blocksIn:
        itStr = ITEM_LABEL + block.text + '\n'
        outStr += itStr
    # add end
    if endType == 0:
        outStr += BULLET_END + '\n'
    elif endType == 1:
        outStr +=  NUMBER_LIST_END + '\n'

    return outStr

# pass a plain paragraph
def alignText(blockIn):
    outStr = ''
    '''Begin'''
    if blockIn.allign == 1:     # center
        outStr += CENTER_BEGIN + '\n'
    elif blockIn.allign == 2:   # right
        outStr += RIGHT_BEGIN + '\n'
    outStr += blockIn.text
    '''End'''
    if blockIn.allign == 1:     # center
        outStr += CENTER_END + '\n'
    elif blockIn.allign == 2:   # right
        outStr += RIGHT_END + '\n'
    return outStr

def makeHeading(blockIn):
    outStr = ''
    if block.heading == 0:      # level one heading
        outStr = SEC_HEADING_ONE + '{' + block.text + '}\n'
    elif block.heading == 1:
        outStr = SEC_HEADING_TWO + '{' + block.text + '}\n'
    elif block.heading == 2:
        outStr = SEC_HEADING_THREE + '{' + block.text + '}\n'
    return outStr

# process all the blocks
def parseAll(blocksIn):
    outStr = ''
    outStr += DOC_CLASS + PACKAGES
    outStr+=BEGIN
    tempBlockList = []
    for block in blocksIn:
        if block.list is not None:    # read a block
            tempBlockList.append(block)
        else:
            if len(tempBlockList) > 0:
                outStr += makeList(tempBlockList)
                del tempBlockList[:]    # clear list
            if block.heading is not None: # read a heading
                headStr = makeHeading(block)
                outStr += headStr
            elif block.align != LEFT:
                outStr += alignText(block)
            else:
                outStr += block.text + '\n'
    outStr+=END
    return outStr


def writeFile(blocksIn):
    # output file
    filename = 'out.tex'
    outfile = open(filename, 'w')
    outStr = parseAll(blocksIn)
    outfile.write(outStr)
    outfile.close()
