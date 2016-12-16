import numpy as np
import cv2 as cv
import math
from Queue import PriorityQueue
from copy import deepcopy



ANGLE_THRESH_DEGREES = .5
ANGLE_THRESH = ANGLE_THRESH_DEGREES*np.pi/180
QUALITY_THRESH = 1 - .2**2
COARSE = .2


def get_line_vectors(linebox):

    # Calculate the unit vector of each of the 5 lines
    line_vectors = [ np.array([np.cos(theta),np.sin(theta)]) for theta in linebox[0] ]
    theta_average = sum(linebox[0])/2
    line_vectors += [ np.array([np.cos(theta_average),np.sin(theta_average)]) ]
    # Put the r_values in a list of equal length
    r_values = np.append( 
        linebox[1], 
        linebox[1][0]*np.cos((linebox[0][1]-linebox[0][0])/2)
    )

    return line_vectors, r_values

def distance_info(line_vector, r, point, d=0):
# Returns the quality score, and a bool that is true if the point is
# above the line represented by r*line_vector and false otherwise

    global EPSILON_SQR

    line_dist = np.dot( point-r*line_vector, line_vector )
    score = abs(line_dist)
    if d:

        desc_dist = np.dot( point-(r+d)*line_vector, line_vector )
        # If the descender line is closer than the base, choose this instead
        # NOTE: Score is weighted differently to avoid matching multiple lines
        # to lines of text that lack descenders
        if abs(desc_dist) < score:

            score = abs(desc_dist)
            line_dist = desc_dist
        
    # Return the log likelyhood score and its positional bool
    return ( float(max(0,1-(score**2)/EPSILON_SQR)),
        (line_dist > 0)^(line_vector[1] < 0)
    )

def is_inside_box(bounds, point):
# Returns true if a point is inside of a box's bounds
# REQ: bounds is True iff point is above the line at that index

    return \
    (bounds[0] or bounds[1] or bounds[4]) and not (bounds[2] and bounds[3])

def point_quality(line_vectors, r_values, point, d):
# This function returns the quality score of a linebox on a SINGLE point
# WARNING 'line_vectors' and 'point' MUST be np.array()

    if r_values[0] > 300 and point[1] > 300:
        pass

    # For each line in the linebox remember score info
    qualities = (

        distance_info(line_vectors[0],r_values[0],point,d),
        distance_info(line_vectors[1],r_values[0],point,d),
        distance_info(line_vectors[0],r_values[1],point,d),
        distance_info(line_vectors[1],r_values[1],point,d),
        distance_info(line_vectors[2],r_values[2],point,d)

    )
    
    # Return maximum value (1) if the point is inside the rectangle
    if is_inside_box( [qual[1] for qual in qualities], point ): return 1

    # Find the maximum score of the point from the bounding lines
    else:
        get_score = lambda info: info[0]
        score = max(qualities, key=get_score)[0]

        # Return the score between [0,1] (Always 1 if the point is inside the box)
        return score

def quality(linebox, points, d=0):
# This function returns a double scoring the quality of a linebox
# Linebox is a 2x2 matrix representing the min/max theta and the
# min/max r value for each line in the box
# WARNING:  'points' MUST be an np.array()

    # Initialize score to 0
    i = 0
    score = 0
    matchlist = []
    # Get unit vectors to each line's normal and their distance from the orign
    line_vectors, r_values = get_line_vectors(linebox)
    # Sum the quality over every point
    for point in points:
    
        this_score = point_quality(line_vectors, r_values, point,d)
        if this_score != 0:
            score += this_score
            matchlist += [point]

    return score, matchlist

def is_subseq(set1, set2):
# Returns True if one set is a subsequence of the other

    small_set = set1
    big_set = set2
    if len(set2) < len(set1):

        big_set = set1
        small_set = set2

    limit = len(small_set)
    count = 0
    i = 0
    while count < limit and i < limit:
        
        if np.array_equal(small_set[count], big_set[i]): count+=1
        i+=1

    return count >= .95*limit

class is_accurate:
# Effects:
# Returns True if this line is accurate.
# Also adds accurate lines to the lines list if it makes sense

    def __init__(self, min_angle, max_angle, min_line, max_line, line_thresh):
        self.line_size = 0
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_line = min_line
        self.max_angle = max_line
        self.max_r = int(COARSE*math.ceil((max_line-min_line)/line_thresh))+1
        self.max_theta = int(2*COARSE*math.ceil((max_angle-min_angle)/ANGLE_THRESH))+1
        # The list of all line-point matches made by this algorithm
        self.lines = \
        [ [None for x in xrange(self.max_r)]
        for x in xrange(self.max_theta) ]

    def __call__(self, linebox, points, line_thresh, d):

        # This line meets the threshold
        if abs(linebox[0][0]-linebox[0][1]) < ANGLE_THRESH and \
        abs(linebox[1][0]-linebox[1][1]) < line_thresh:

            # Calculate final line and its quality
            theta_avg = np.mean(linebox[0])
            r_avg = np.mean(linebox[1])
            new_quality, _ = \
            quality(((theta_avg, theta_avg),(r_avg,r_avg)), points, d)
            theta = int(2*COARSE*(theta_avg-self.min_angle)/ANGLE_THRESH)
            r = int(COARSE*(r_avg-self.min_line)/line_thresh)

#            # Get any adjacent lines
#            adj_lines = []
#            for adj_theta in xrange(max(0,theta-1),min(self.max_theta,theta+2)):
#                for adj_r in xrange(max(0,r-1),min(self.max_r, r+2)):
#                    if self.lines[adj_theta][adj_r] is not None:
#                        adj_lines += [(adj_theta,adj_r)]
#
#            # If there is a nearby line, just pick the best version
#            if adj_lines:
#                functor = lambda (a,b): self.lines[a][b][0]
#                (max_theta, max_r) = max(adj_lines, key=functor)
#                if new_quality > self.lines[max_theta][max_r][0]:
#                    self.lines[max_theta][max_r] = \
#                    (new_quality,(theta,r),new_points)

            # Don't add this line if a better line is in the bin
            if not (self.lines[theta][r] and
            self.lines[theta][r][0] >= new_quality and
            new_quality < len(points)*QUALITY_THRESH):
            
                self.lines[theta][r] = (new_quality,(theta_avg,r_avg),points)
                print self.lines[theta][r][0]

            return True

        return False

    def output(self):
    # Present output

        lines = []
        for row in self.lines:
            for line in row:
                if line: lines += [line]

        return lines

def has_intersection(set1, set2):
# True if set1 and set2 have an intersection

    for point1 in set1:
        for point2 in set2:
            if np.array_equal(point1,point2): return True

    return False
                    
def small_enough(linebox, points, line_thresh, lines, d):

    # This line meets the threshold
    if abs(linebox[0][0]-linebox[0][1]) < ANGLE_THRESH and \
    abs(linebox[1][0]-linebox[1][1]) < line_thresh:

        theta_avg = np.mean(linebox[0])
        r_avg = np.mean(linebox[1])
        new_line = (theta_avg, r_avg)
        lb = ((new_line[0],new_line[0]),(new_line[1],new_line[1]))
        new_quality, _ = quality(lb, points, d)
        lines += [(new_quality, (theta_avg, r_avg), points)]
        return True

    return False

#        theta_avg = np.mean(linebox[0])
#        r_avg = np.mean(linebox[1])
#        new_line = (theta_avg, r_avg)
#        lb = ((new_line[0],new_line[0]),(new_line[1],new_line[1]))
#        new_quality, _ = quality(lb, points, d)
#        # This line is a near duplicate of a previous line
#        duplicate_found = False
#        i = 0
#        j = 0
#        while i < len(lines):
#            # These lines are too similar to coexist
#            if (abs(lines[i][1][0] - new_line[0]) < 2*ANGLE_THRESH and \
#            abs(lines[i][1][1] - new_line[1]) < 2*line_thresh) or \
#            has_intersection(points,lines[i][2]):
#
#                # The new_line is more accurate.  Replace the old
#                if not duplicate_found:
#                    if lines[i][0] < new_quality: 
#                        lines[i] = (new_quality, new_line, points)
#                        # Stop searching for duplicates
#                        duplicate_found = True
#                        j = i
#                        i += 1
#                        break
#                    else: break
#
#                # Absorb other duplicates
#                else:
#                    if lines[j][0] < lines[i][0]: lines[j] = lines[i]
#                    lines = lines[:i] + lines[i+1:]
#
#            else: i+=1
#    
#        # This line is not a duplicate
#        if not duplicate_found: lines += [ (new_quality, new_line, points) ]
#        return True
#
#    return False

def only_intersection(linebox, obstacle):
# The value is True if there is an intersection between any of the 
# lines in linebox and the obstacle

    line_vectors, r_values = get_line_vectors(linebox)

    # Only_intersection is true iff 
    # 1. At least one bottom corner is below all lower bounds
    # 2. At least one top corner is above all upper bounds

    return (

        not (
        distance_info(line_vectors[0],r_values[0],obstacle.corners[0])[1] or
        distance_info(line_vectors[1],r_values[0],obstacle.corners[0])[1] or
        distance_info(line_vectors[2],r_values[2],obstacle.corners[0])[1]
        ) or not (
        distance_info(line_vectors[0],r_values[0],obstacle.corners[3])[1] or
        distance_info(line_vectors[1],r_values[0],obstacle.corners[3])[1] or
        distance_info(line_vectors[2],r_values[2],obstacle.corners[3])[1] )

    ) and (

        (distance_info(line_vectors[0],r_values[1],obstacle.corners[1])[1] and
        distance_info(line_vectors[1],r_values[1],obstacle.corners[1])[1]
        ) or (
        distance_info(line_vectors[0],r_values[1],obstacle.corners[2])[1] and
        distance_info(line_vectors[1],r_values[1],obstacle.corners[2])[1] )

    )

def no_intersection(linebox, obstacle):
# The value is True if every possible value of the linebox misses the obstacle
#
# Returns True if c0 and c3 are above all upperbounds
# OR
# Returns True if c1 and c2 are below all lower bounds
    
    line_vectors, r_values = get_line_vectors(linebox)

    return ( 

        distance_info(line_vectors[0],r_values[1],obstacle.corners[0])[1] and 
        distance_info(line_vectors[1],r_values[1],obstacle.corners[0])[1] and 
        distance_info(line_vectors[0],r_values[1],obstacle.corners[3])[1] and 
        distance_info(line_vectors[1],r_values[1],obstacle.corners[3])[1]

    ) or not (
    
        distance_info(line_vectors[0],r_values[0],obstacle.corners[1])[1] or
        distance_info(line_vectors[1],r_values[0],obstacle.corners[1])[1] or
        distance_info(line_vectors[2],r_values[2],obstacle.corners[1])[1] or
        distance_info(line_vectors[0],r_values[0],obstacle.corners[2])[1] or
        distance_info(line_vectors[1],r_values[0],obstacle.corners[2])[1] or
        distance_info(line_vectors[2],r_values[2],obstacle.corners[2])[1]

    )

def linebox_split(linebox, line_thresh):

    theta_range = linebox[0][1]-linebox[0][0]
    r_range     = linebox[1][1]-linebox[1][0]

    # Case Theta is much smaller than r
    if (not r_range < line_thresh) and \
    (theta_range < ANGLE_THRESH or
    theta_range/ANGLE_THRESH < r_range/line_thresh):

        # Split this box in half along its r values
        avg_r   = np.mean(linebox[1])
        low_box = deepcopy(linebox)
        low_box[1][1] = avg_r
        linebox[1][0] = avg_r

    # Case: Theta is much bigger than r
    else:
        # Split this box in half along its theta values
        avg_theta = np.mean(linebox[0])
        low_box = deepcopy(linebox)
        low_box[0][1] = avg_theta
        linebox[0][0] = avg_theta
    
    return (low_box, linebox)

def enqueue_lb( queue, sub_linebox, points, obs, d ):
# Enqueues the new sub_linebox 
    
    # Only look at lines that have the potential to be quality
    sub_quality, sub_points = quality(sub_linebox, points, d)
    if len(sub_points) > 1 and sub_quality > QUALITY_MIN:

        queue.put((
            -sub_quality,
            sub_linebox,
            sub_points,
            obs
        ))

def get_lines( (img_h,img_w), points, obstacles, (eps, d)):
# Finds the optimal line via branch and bound methods

    # Set some thresholds
    global EPSILON_SQR
    global QUALITY_MIN
    QUALITY_MIN = QUALITY_THRESH * int(np.sqrt(len(points)))/6
    EPSILON_SQR = eps**2/4
    line_thresh = eps*COARSE
    min_angle = np.pi/2-.2
    max_angle = np.pi/2+.2
    min_line = -img_w/np.sqrt(2)
    max_line = img_w/np.sqrt(2)+img_h/np.sqrt(2)

    # Functor for terminating splits and adding accepted lines
    acceptor = is_accurate( min_angle, max_angle, min_line, max_line, line_thresh)
    lines = []
    
    # The initial bounds of the linebox
    # (All possible lines within 45 degrees of being horizontal)
    linebox = (
    
        [min_angle, max_angle],
        [min_line, max_line]

    )

    # Keep track of things in a priority queue
    queue = PriorityQueue()
    queue.put( (-len(points), linebox, points, obstacles) )
    while not queue.empty():

        # Get the linebox with the highest upperbound on quality
        ub_quality, lb, points_p, obs_p = queue.get()
        ub_quality *= -1
#        if lines:
#            print len(lines), lines[-1][0]

        # Split this box if its too large to attempt to add to our lines
        if not acceptor(lb, points_p, line_thresh, d):

            # Split this linebox to make is smaller
            sub_lineboxes = linebox_split(lb,line_thresh)
            # Get rid of obstacles that can't be encountered anymore
            pruned_obs = [obs for obs in obs_p if not no_intersection(lb, obs)]
            # Split the lineboxes along blocking obstacles
            for sub_linebox in sub_lineboxes:

                enqueue_lb(queue, sub_linebox, points_p, pruned_obs, d)

#                # Get index for all obstacles that completely block the path
#                blocking = [ i for i in xrange(len(pruned_obs))
#                            if only_intersection(sub_linebox, pruned_obs[i]) ]
#                # Greedilly start splitting sub_linebox from left to right
#                sort_functor = lambda i: pruned_obs[i].left
#                blocking = sorted( blocking, key=sort_functor )
#                # If there are no blocking obstacles, enqueue normally
#                if not blocking:
#
#                    enqueue_lb(queue, sub_linebox, points_p, pruned_obs, d)
#
#                # Points need to be split along this lb/obstacle combo
#                else:
#
#                    relevant_obs = [ pruned_obs[i]
#                                    for i in xrange(len(pruned_obs))
#                                    if i not in blocking ]
#                    # Start greedily splitting points along the leftmost obs
#                    right = points_p
#                    for i in blocking:
#
#                        # Split points into a left and right subgroup divided
#                        # by the obstacle
#                        left = []
#                        j = 0
#                        while j < len(right):
#
#                            if right[j][0] < pruned_obs[i].left:
#                                
#                                left += [right[j]]
#                                right = right[:j] + right[j+1:]
#
#                            else: j+=1
#
#                        # Add these new split lineboxes to the queue
#                        if left:
#                            enqueue_lb(
#                                queue,
#                                sub_linebox,
#                                left,
#                                relevant_obs,
#                                d
#                            )
#
#                    # Remember the last remaining right linebox
#                    if right:
#                        enqueue_lb(
#                            queue,
#                            sub_linebox,
#                            right,
#                            relevant_obs,
#                            d
#                        )

    return acceptor.output()

import sys
import components
from preprocess import preprocess 
from textblock import TextBlock
from orient import fixSkew
if __name__ == '__main__':
    
    global EPSILON_SQR
    EPSILON_SQR = 10

    # Calculate the largest possible linebox
    # image = cv.imread(sys.argv[1])
    # img = preprocess(image)
    # img = fixSkew(img)

    linebox = (

        [np.pi/2, np.pi/2],
        [np.sqrt(10), 2*np.sqrt(10)]

    )

    obs = TextBlock( (2,9),(3,11) )

    print only_intersection(linebox, obs)
    print no_intersection(linebox, obs)
