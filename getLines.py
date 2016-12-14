import numpy as np
import cv2 as cv
from Queue import PriorityQueue
from copy import deepcopy



ANGLE_THRESH_DEGREES = 1
ANGLE_THRESH = ANGLE_THRESH_DEGREES*np.pi/180
QUALITY_THRESH = 1 - .8**2
global EPSILON_SQR



def get_line_vectors(linebox):

    # Calculate the unit vector of each of the 5 lines
    line_vectors = [ np.array([np.cos(theta),np.sin(theta)]) for theta in linebox[0] ]
    theta_average = sum(linebox[0])/2
    line_vectors += [ np.array([np.cos(theta_average),np.sin(theta_average)]) ]
    # Put the r_values in a list of equal length
    r_values = np.append( 
        linebox[1], 
        linebox[1][0]*(1-np.cos((linebox[0][1]-linebox[0][0])/2))
    )

    return line_vectors, r_values

def distance_info(line_vector, r, point, d=0):
# Returns the quality score, and a bool that is true if the point is
# above the line represented by r*line_vector and false otherwise

    global EPSILON_SQR

    line_dist = np.dot( point-r*line_vector, line_vector )
    score = abs(line_dist)
    if d:

        desc_dist = np.dot( point-(r-d)*line_vector, line_vector )
        # If the descender line is closer than the base, choose this instead
        if abs(desc_dist) < score:

            score = abs(desc_dist)
            line_dist = desc_dist
        
    # Return the log likelyhood score and its positional bool
    return \
    (max(0,1-(score**2)/EPSILON_SQR), (line_dist > 0)^(line_vector[1] < 0)) 

def is_inside_box(bounds, point):
# Returns true if a point is inside of a box's bounds
# REQ: bounds is True iff point is above the line at that index

    return \
    (bounds[0] or bounds[1] or bounds[4]) and not (bounds[2] and bounds[3])

def point_quality(line_vectors, r_values, point, d):
# This function returns the quality score of a linebox on a SINGLE point
# WARNING 'line_vectors' and 'point' MUST be np.array()

    # For each line in the linebox remember score info
    qualities = (

        distance_info(line_vectors[0],r_values[0],point,d),
        distance_info(line_vectors[1],r_values[0],point,d),
        distance_info(line_vectors[0],r_values[1],point,d),
        distance_info(line_vectors[1],r_values[1],point,d),
        distance_info(line_vectors[2],r_values[2],point,d)

    )
    
    # Return maximum value (1) if the point is inside the rectangle
    if is_inside_box( [quality[1] for quality in qualities], point ): return 1

    # Find the maximum score of the point from the bounding lines
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
    score = 0
    matchlist = []
    # Get unit vectors to each line's normal and their distance from the orign
    line_vectors, r_values = get_line_vectors(linebox)
    # Sum the quality over every point
    for point in points:
    
        score += point_quality(line_vectors, r_values, point,d)
        if score != 0: matchlist += [point]

    return score, matchlist

def is_accurate(linebox, line_thresh):

    return \
    abs(linebox[0][0]-linebox[0][1]) < ANGLE_THRESH and \
    abs(linebox[1][0]-linebox[1][1]) < line_thresh

def no_intersection(linebox, obstacle):
# The value is True if there is no intersection between any of the 
# lines in linebox and the obstacle

    line_vectors, r_values = get_line_vectors(linebox)
    
    # Are the bottom corners above the top bounds?
    botleft0 = distance_info(line_vectors[0],r_values[1],obstacle.corners[1])[1]
    botleft1 = distance_info(line_vectors[1],r_values[1],obstacle.corners[1])[1]
    botright0 = distance_info(line_vectors[0],r_values[1],obstacle.corners[2])[1]
    botright1 = distance_info(line_vectors[1],r_values[1],obstacle.corners[2])[1]

    # The obstacle is above all possible lines.  We're done
    if botleft0 and botleft1 and botright0 and botright1: return True

    # Likewise, if any of the bottom corners are above the top bounds, it cannot
    # be true that all the top corners will be below the bottom bounds.  Don't
    # bother checking
    elif botleft0 or botleft1 or botright0 or botright1: return False

    # Are the top corners below the bottom bounds?
    topleft0 = distance_info(line_vectors[0],r_values[0],obstacle.corners[0])[1]
    topleft1 = distance_info(line_vectors[1],r_values[0],obstacle.corners[0])[1]
    topleft2 = distance_info(line_vectors[2],r_values[2],obstacle.corners[0])[1]
    topright0 = distance_info(line_vectors[0],r_values[0],obstacle.corners[3])[1]
    topright1 = distance_info(line_vectors[1],r_values[0],obstacle.corners[3])[1]
    topright2 = distance_info(line_vectors[2],r_values[2],obstacle.corners[3])[1]

    # If the answer is yes.  The obstacle is below the line.  We're done.
    return \
    not (topleft0 or topleft1 or topleft2 or topright0 or topright1 or topright2)

def only_intersection(linebox, obstacle):
# The value is True if every possible value of the linebox interesects
# with the obstacle
    
    line_vectors, r_values = get_line_vectors(linebox)

    # Are the top corners above the top bounds?
    if \
    distance_info(line_vectors[0],r_values[1],obstacle.corners[0])[1] or \
    distance_info(line_vectors[1],r_values[1],obstacle.corners[0])[1] or \
    distance_info(line_vectors[0],r_values[1],obstacle.corners[3])[1] or \
    distance_info(line_vectors[1],r_values[1],obstacle.corners[3])[1]:
        return False

    # Are the bottom corners below the bottom bounds?
    if not (
    distance_info(line_vectors[0],r_values[0],obstacle.corners[1])[1] or \
    distance_info(line_vectors[1],r_values[0],obstacle.corners[1])[1] or \
    distance_info(line_vectors[2],r_values[2],obstacle.corners[1])[1] or \
    distance_info(line_vectors[0],r_values[0],obstacle.corners[2])[1] or \
    distance_info(line_vectors[1],r_values[0],obstacle.corners[2])[1] or \
    distance_info(line_vectors[2],r_values[2],obstacle.corners[2])[1]):
        return False

    # Otherwise, the rectangle is engulfed by this obstacle
    return True

def linebox_split(linebox, line_thresh):

    theta_range = linebox[0][1]-linebox[0][0]
    r_range     = linebox[1][1]-linebox[1][0]

    # Case Theta is much smaller than r
    if theta_range/ANGLE_THRESH < r_range/line_thresh:

        # Split this box in half along its r values
        avg_r     = np.mean(linebox[1])
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
    if sub_points and sub_quality/len(sub_points) > QUALITY_THRESH:
        queue.put((
            -sub_quality,
            sub_linebox,
            sub_points,
            obs
        ))

def get_lines( (img_h,img_w), points, obstacles, (eps, d)):
# Finds the optimal line via branch and bound methods

    # Set the distance threshold
    global EPSILON_SQR
    EPSILON_SQR = eps**2
    line_thresh = eps/8

    # The list of all line-point matches made by this algorithm
    lines = []

    # The initial bounds of the linebox
    # (All possible lines within 45 degrees of being horizontal)
    linebox = (
    
        [np.pi/4, 3*np.pi/4],
        [-img_w/np.sqrt(2), img_w/np.sqrt(2)+img_h/np.sqrt(2)]

    )

    # Keep track of things in a priority queue
    queue = PriorityQueue()
    queue.put( (-len(points), linebox, points, obstacles) )
    while not queue.empty():

        # Get the linebox with the highest upperbound on quality
        ub_quality, lb, points_p, obs_p = queue.get()
        ub_quality *= -1
        print ub_quality, len(points_p)

        # This box is small enough to convert into a line
        if is_accurate(lb, line_thresh):

            #print points_p
            lines += [ ((np.mean(lb[0]),np.mean(lb[1])), points_p) ]

        else:

            # Split this linebox to make is smaller
            sub_lineboxes = linebox_split(lb,line_thresh)
            # Get rid of obstacles that can't be encountered anymore
            pruned_obs = [ obs for obs in obs_p if not no_intersection(lb, obs) ]
            
            # Split the lineboxes along blocking obstacles
            for sub_linebox in sub_lineboxes:

                # Get index for all obstacles that completely block the path
                blocking = [ i for i in xrange(len(pruned_obs))
                            if only_intersection(sub_linebox, pruned_obs[i]) ]

                # Greedilly start splitting sub_linebox from left to right
                sort_functor = lambda i: pruned_obs[i].left
                blocking = sorted( blocking, key=sort_functor )

                # If there are no blocking obstacles, enqueue normally
                if not blocking:

                    enqueue_lb(queue, sub_linebox, points_p, pruned_obs, d)

                # Points need to be split along this lb/obstacle combo
                else:

                    relevant_obs = [ pruned_obs[i]
                                    for i in xrange(len(pruned_obs))
                                    if i not in blocking ]

                    # Start greedily splitting points along the leftmost obs
                    right = points_p
                    for i in blocking:

                        # Split points into a left and right subgroup divided
                        # by the obstacle
                        left = []
                        j = 0
                        while j < len(right):

                            if right[j][0] < pruned_obs[i].left:
                                
                                left += [right[j]]
                                right = right[:j] + right[j+1:]

                            else: j+=1

                        # Add these new split lineboxes to the queue
                        if left:
                            enqueue_lb(
                                queue,
                                sub_linebox,
                                left,
                                relevant_obs,
                                d
                            )

                    # Remember the last remaining right linebox
                    if right:
                        enqueue_lb(
                            queue,
                            sub_linebox,
                            right,
                            relevant_obs,
                            d
                        )

    return lines

if __name__ == '__main__':

    # Calculate the largest possible linebox
    linebox = [ [0, PAGE_HEIGHT], [np.pi/4, 3*np.pi/4] ]
    points  = get_points(image)
