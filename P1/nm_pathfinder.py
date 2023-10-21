from heapq import heappop, heappush
from math import inf, sqrt

def find_path(source_point, destination_point, mesh):
    """
    Searches for a path from source_point to destination_point through the mesh
    
    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to
        
    Returns:
        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """
    # Top Left = (0, 0)
    # Bottom Right = (height, width)

    # List of points to draw paths
    path = []

    # Dict of boxes visited (or enqueued)
    boxes = {}

    # Identify the source and destination boxes
    source_box = get_boxes(source_point, mesh)
    destination_box = get_boxes(destination_point, mesh)

    # Point is not within a box (On an outline of the pickled image)
    if (source_box is None) or (destination_box is None):
        print("No path!")
        return path, boxes.keys()

    # Dict of parent boxes found in Breadth First Search (BFS)
    # parent_dict = bfs(mesh, source_box, destination_box)

    # Dict of parent boxes found in A*
    # parent_dict = a_star(mesh, source_box, destination_box)
    # parent_dict.update({source_box: source_point})

    # Dict of parent boxes found in Bidirectional A*
    parent_dict = a_star_bi(mesh, source_box, destination_box)
    parent_dict.update({source_box: source_point})

    # Modify your simple search to compute a legal list of line segments demonstrating the path.
    # Instead of doing your search purely at the box level,
    # add an extra table (dict) to keep track of the precise x,y position within that box that your path will traverse.
    # In the solution code, we call this table 'detail_points', a dictionary that maps boxes to (x,y) pairs.
    # Midpoints of boxes will not work for this assignment.

    path_list = []
    detail_points = {}
 
    # Successfully add boxes visited to path_list, still stuck on detail_points
    get_path(path_list, detail_points, parent_dict, source_box, destination_box, source_point, destination_point)

    if len(path_list) == 0:
        # Goal is NOT reachable from the start
        print("No path!")
        return path, boxes.keys()

    # Goal is reachable from the start

    # When the search terminates (assuming it found a path),
    # construct a list of line segments to return by looking up the detail points for each box along the path.
    # In this assignment, the order of the line segments is not important.
    # What matters is that the line is legal by visual inspection of the visualization it produces.

    # Add boxes visited
    for box in path_list:
        boxes.update({box: None})

    # Print variables as needed
    print(
        f'Source Point: {source_point}\n'
        # f'Source Box: {source_box}\n'
        f'Destination Point: {destination_point}\n'
        # f'Destination Box: {destination_box}\n'
        f'Boxes Visited: {path_list}\n'
        f'Detail_Points (Line Segment Points): {detail_points}\n'
    )

    for box in detail_points:
        # Add line segments to be drawn (start_coordinates, end_coordinates) in any order
        path.append(detail_points[box])

    return path, boxes.keys()

# 
def get_boxes(point, mesh):
    """
    Returns the box containing the given point
    
    Args:
        point: (x, y) coordinates of the point
        mesh: pathway constraints the path adheres to
        
    Returns:
        The box that contains the point, or None if no box contains the point
    """
    for box in mesh["boxes"]:
        if (box[0] <= point[0] <= box[1]) and (box[2] <= point[1] <= box[3]):
            return box
    return None

def bfs(mesh, start, goal):
    # IMPLEMENT THE SIMPLEST COMPLETE SEARCH ALGORITHM YOU CAN.
    # Starting with the source box, run BFS looking for a sequence of boxes that reaches the destination box.
    # You can also use this to evaluate your A* outputs!

    frontier = [start]
    parent_dict = dict()
    parent_dict[start] = None

    while not len(frontier) == 0:
        current = frontier.pop(0)

        # Early exit BFS
        if current == goal:
            break

        for box in mesh["adj"][current]:
            if box not in parent_dict:
                frontier.append(box)
                parent_dict[box] = current

    return parent_dict

def a_star(mesh, start, goal):
    frontier = [(0, start)]  # (priority, box)
    parent_dict = dict()
    distance_table = dict()  # distance from start to box
    distance_table[start] = 0

    while not len(frontier) == 0:
        _, current = heappop(frontier) # lowest priority box

        # Early exit A*
        if current == goal:
            break

        for box in mesh["adj"][current]: # for all neighbors
            new_distance = distance_table[current] + euclidean_distance(current, box)
            if box not in distance_table or new_distance < distance_table[box]:
                distance_table[box] = new_distance
                priority = new_distance + euclidean_distance(box, goal)
                heappush(frontier, (priority, box))
                parent_dict[box] = current

    return parent_dict

def a_star_bi(mesh, start, goal):
    # Copies for each direction of the Search 
    forward_queue = [(0, start, 'destination')]  # (priority, box, goal)
    forward_prev = dict()
    forward_dist = dict()
    forward_dist[start] = 0
    
    backward_queue = [(0, goal, 'source')]  # (priority, box, goal)
    backward_prev = dict()
    backward_dist = dict()
    backward_dist[goal] = 0

    intersection_box = None  # Common box found by both searches

    while forward_queue and backward_queue:
        forward_priority, forward_curr_box, forward_curr_goal = heappop(forward_queue)
        # Check if current box is visited by backwards search
        if forward_curr_box in backward_prev:
            intersection_box = forward_curr_box
            break
        
        for forward_neighbor_box in mesh["adj"][forward_curr_box]:
            new_forward_distance = forward_dist[forward_curr_box] + euclidean_distance(forward_curr_box, forward_neighbor_box)
            # Update distance and priority if shorter path found
            if forward_neighbor_box not in forward_dist or new_forward_distance < forward_dist[forward_neighbor_box]:
                forward_dist[forward_neighbor_box] = new_forward_distance
                forward_priority = new_forward_distance + euclidean_distance(forward_neighbor_box, goal)
                heappush(forward_queue, (forward_priority, forward_neighbor_box, forward_curr_goal))
                forward_prev[forward_neighbor_box] = forward_curr_box

        backward_priority, backward_curr_box, backward_curr_goal = heappop(backward_queue)

        if backward_curr_box in forward_prev:
            intersection_box = backward_curr_box
            break

        for backward_neighbor_box in mesh["adj"][backward_curr_box]:
            new_backward_distance = backward_dist[backward_curr_box] + euclidean_distance(backward_curr_box, backward_neighbor_box)
            if backward_neighbor_box not in backward_dist or new_backward_distance < backward_dist[backward_neighbor_box]:
                backward_dist[backward_neighbor_box] = new_backward_distance
                backward_priority = new_backward_distance + euclidean_distance(backward_neighbor_box, start)
                heappush(backward_queue, (backward_priority, backward_neighbor_box, backward_curr_goal))
                backward_prev[backward_neighbor_box] = backward_curr_box

    if intersection_box is None:
        return None

    parent_dict = {}
    current_box = intersection_box

    # Construct the parent_dict from the intersection to the source box
    while current_box in forward_prev:
        parent_dict[current_box] = forward_prev[current_box]
        current_box = forward_prev[current_box]

    # Construct the parent_dict from the intersection to the goal box
    current_box = intersection_box
    while current_box in backward_prev:
        parent_dict[backward_prev[current_box]] = current_box
        current_box = backward_prev[current_box]

    return parent_dict

def get_path(path_list, detail_points, parent_dict, start_box, current_box, start_point, goal_point):
    if len(path_list) == 0:
        detail_points.update({current_box: goal_point})
    constrained_point = goal_point

    if current_box not in parent_dict:
        # goal is NOT reachable from the start
        return path_list

    if current_box == start_box:
        # Add a line segment in start_box
        detail_points.update({parent_dict[current_box]: start_point})
        path_list.append(start_box)
    else:
        # Add a line segment in current_box
        # When considering a move from one box to another, copy the x,y position within the current box
        # and constrain it (with mins and maxes) to the bounds of the destination box.
        border = get_border(current_box, parent_dict[current_box])
        constrained_point = constrain(border, constrained_point)
        detail_points.update({parent_dict[current_box]: constrained_point})

        get_path(path_list, detail_points, parent_dict, start_box, parent_dict[current_box], start_point, constrained_point)

        path_list.append(current_box)

    return constrained_point


def get_border(box1, box2):
    # x range of border:
    # [max(b1x1, b2x1), min(b1x2, b2x2)]

    # y range of border:
    # [max(b1y1, b2y1), min(b1y2, b2y2)]

    # Box points: [x1, x2, y1, y2]
    
    border = [max(box1[0], box2[0]), min(box1[1], box2[1]),
              max(box1[2], box2[2]), min(box1[3], box2[3])]

    # Print variables as needed
    print(
        f'B1: {box1}\n'
        f'B2: {box2}\n'
        f'Border: {border}\n'
    )

    return border


def constrain(border, constrained_point):
    if not (border[0] < constrained_point[0] < border[1]):
        constrained_point = (max(border[0], constrained_point[0]), constrained_point[1])
        constrained_point = (min(border[1], constrained_point[0]), constrained_point[1])
    if not (border[2] < constrained_point[1] < border[3]):
        constrained_point = (constrained_point[0], max(border[2], constrained_point[1]))
        constrained_point = (constrained_point[0], min(border[3], constrained_point[1]))
    return constrained_point


def euclidean_distance(start, goal):
    # Use the Euclidean distances between these two points as the length of the edge in the graph you are exploring
    # (not the distance between the midpoints of the two boxes).

    # Two-dimensional formula
    # Sqrt( (q1 - p1)^2 + (q2 - p2)^2 )
    return pow((pow((goal[0] - start[0]), 2) + pow((goal[1] - start[1]), 2)), 0.5)
