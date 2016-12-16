import numpy as np
import getLines

def seperate_sets(lines):

    points = 0
    processed_lines = []
    # Remove points
    while lines:

        # If lines are still good enough
        best_line = max(lines, key=lambda x: x[0])
        if best_line[0] > 3:

            # Get rid of the best line, and remove all of its points from
            # every other line
            processed_lines += [best_line]
            points += len(best_line[2])
            new_lines = []
            lines.remove(best_line)
            for line in lines:

                # Keep this line's points ONLY if they are not in best_line
                new_points = []
                for point in line[2]:
                    # Assume its unique until a match is found
                    is_unique = True
                    for processed_point in best_line[2]:

                        if np.array_equal( point, processed_point):
                            is_unique = False
                            break

                    if is_unique: new_points += [point]

                # Add this line if it still contains points
                if new_points: new_lines += [(line[0],line[1], new_points)]

            lines = new_lines

            # Calculate new quality for each line
            for line in lines:

                linebox = [ [line[1][0]]*2, [line[1][1]]*2 ]
                qual, _ = getLines.quality( linebox, line[2] )
                line = (qual,line[1],line[2])

        else: break

    return processed_lines

def post_process(text_lines):
    pass
