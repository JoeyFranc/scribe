import numpy as np
import cv2 as cv
from Queue import PriorityQueue



ANGLE_THRESH_DEGREES = 2.5
ANGLE_THRESH = ANGLE_THRESH_DEGREES*np.pi/180
EPSILON_SQR = min(PAGE_DIMENSIONS)**2/1600



def get_line_vectors(linebox):

    # Calculate the unit vector of each of the 5 lines
    line_vectors = [ np.array([np.cos(theta),np.sin(theta)]) for theta in linebox[0] ]
    theta_average = sum(linebox[0])/2
    line_vectors += [ np.array([np.cos(theta_average),np.sin(theta_average)]) ]
    # Put the r_values in a list of equal length
    r_values = linebox[1]*2 + [linebox[1][0]*(1-np.cos(theta_average))]

    return line_vectors, r_values

def distance_info(line_vector, r, point, d):
# Returns the quality score, and a bool representing whether the point is
# above or below the line represented by r*line_vector

    line_dist = np.dot( point-r*line_vector, line_vector )
    base_dist = np.dot( point-(r-d)*line_vector, line_vector )
    this_score = 1-min(abs(line_dist),abs(base_dist))**2/EPISOLON_SQR

    return (this_score, line_dist >= 0) 

def is_inside_box(bounds, point):
# Returns true if a point is inside of a box's bounds
# REQ: bounds is True iff point is above the line at that index

    return \
    (bounds[0] or bounds[1] or bounds[4]) and not (bounds[2] and bounds[3])

def point_quality(line_vectors, r_values, point, d):
# This function returns the quality score of a linebox on a SINGLE point
# WARNING 'line_vectors' and 'point' MUST be np.array()

    # For each line in the linebox remember score info
    qualities = [

        distance_info(line_vectors[0],r[0],point,d),
        distance_info(line_vectors[1],r[0],point,d),
        distance_info(line_vectors[0],r[1],point,d),
        distance_info(line_vectors[1],r[1],point,d),
        distance_info(line_vectors[2],r[2],point,d)

    ]
    
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

def is_accurate(linebox):

    return \
    abs(linebox[0][0]-linebox[0][1]) < ANGLE_THRESH and \
    abs(linebox[1][0]-linebox[1][1]) < LINE_THRESH

def no_intersect(linebox, obstacle):
# Returns True if there is no intersection between any of the lines in linebox
# and the obstacle

    line_vectors, r_values = get_line_vectors(linebox)

    # Are the top cornes above or below the bottom bounds?
    topleft0 = distance_info(line_vectors[0],r_values[0],obstacle.topleft)[1]
    topleft1 = distance_info(line_vectors[1],r_values[0],obstacle.topleft)[1]
    topright0 = distance_info(line_vectors[0],r_values[0],obstacle.topright)[1]
    topright1 = distance_info(line_vectors[1],r_values[0],obstacle.topright)[1]
    topleft4 = distance_info(line_vectors[4],r_values[4],obstacle.topleft)[1]
    topright4 = distance_info(line_vectors[4],r_values[4],obstacle.topright)[1]

    # Are the bottom corners above or below the top bounds?
    botleft0 = distance_info(line_vectors[0],r_values[1],obstacle.botleft)[1]
    botleft1 = distance_info(line_vectors[1],r_values[1],obstacle.botleft)[1]
    botright0 = distance_info(line_vectors[0],r_values[1],obstacle.botright)[1]
    botright1 = distance_info(line_vectors[1],r_values[1],obstacle.botright)[1]

    # Return true if either the rectangle is above or below the linebox
    return \
    (botleft0 and botleft1 and botright0 and botright1) or not \
    (topleft0 or topleft1 or topleft4 or topright0 or topright1 or topright4)



def get_constrained_lines(linebox, points, obstacles):
# Finds the optimal line via branch and bound methods

    # All line-point matches made by this algorithm
    lines = []

    # Keep track of things in a priority queue
    queue = PriorityQueue()
    queue.put( (quality(linebox, points), linebox, points, obstacles) )
    while not queue.empty():

        # Get the linebox with the highest upperbound on quality
        up_bound_q, lb, points_p, obs_p = queue.get()

        # This box is small enough to convert into a line
        if is_accurate(lb): lines += [ (lb, points_p) ]
        else:

            # Split the linebox at excluded obstacles
            pruned_obs = [ obs for obs in obs_p if not no_intersect(lb, obs) ]
                    
            # Split the linebox into more accurate 
            for sub_linebox in linebox_split(lb):

                sub_quality, sub_points = quality(sub_linebox, points_p)
                queue.put(
                    sub_quality,
                    sub_linebox,
                    sub_points,
                    pruned_obs
                )

    return lines



if __name__ == '__main__':

    # Calculate the largest possible linebox
    linebox = [ [0, PAGE_HEIGHT], [-np.pi, np.pi ] ]
    points  = get_points(image)
