"""Simple knitgraph generators used primarily for debugging"""
from turtle import width
from typing import List, Optional
from knit_graphs.Knit_Graph import Knit_Graph, Pull_Direction
from knit_graphs.Yarn import Yarn


def stockinette(width: int = 4, height: int = 4, carrier:int=3) -> Knit_Graph:
    """
    :param carrier:
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: a knitgraph of stockinette on one yarn of width stitches by height course
    """
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph, carrier_id=carrier)
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        # loop_id, loop = yarn.add_loop_to_end(width)
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    prior_row = first_row
    for _ in range(1, height):
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            # child_id, child = yarn.add_loop_to_end(width)
            next_row.append(child_id)
            knitGraph.add_loop(child)
            knitGraph.connect_loops(parent_id, child_id)
        prior_row = next_row
    return knitGraph

def tube(width: int = 4, height: int = 4, carrier:int=3) -> Knit_Graph:
    """
    :param carrier:
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: a knitgraph of stockinette on one yarn of width stitches by height course
    """
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph, carrier_id=carrier)
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width*2):
        loop_id, loop = yarn.add_loop_to_end()
        # loop_id, loop = yarn.add_loop_to_end(width)
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    prior_row = first_row
    for _ in range(1, height):
        next_row = []
        for parent_id in (prior_row):
            child_id, child = yarn.add_loop_to_end()
            # child_id, child = yarn.add_loop_to_end(width)
            next_row.append(child_id)
            knitGraph.add_loop(child)
            knitGraph.connect_loops(parent_id, child_id)
        prior_row = next_row
    return knitGraph, yarn

def add_hole_on_tube(tube_width, tube_height, hole_start_course, hole_start_wale, hole_width, hole_height, carrier: int =3, new_carrier: Optional[int] = None) -> Knit_Graph:
    assert hole_width != tube_width*2 - 1, f"invalid hole width"
    assert tube_height > hole_start_course + hole_height, f'tube_height is not sufficient to produce this hole'
    # knitGraph = Knit_Graph()
    # yarn = Yarn("yarn", knitGraph, carrier_id=carrier)
    # knitGraph.add_yarn(yarn)
    knitGraph, yarn = tube(height = hole_start_course, width = tube_width, carrier = carrier)
    loop_ids_to_course, course_to_loop_ids = knitGraph.get_courses()
    top_course_index = max(*course_to_loop_ids.keys())
    top_course = course_to_loop_ids[top_course_index]
    hole_end_wale = hole_start_wale + hole_width
    #indicator is used to indicate each case below.
    indicator = 0
    #case 1: when hole_start_wale == 0
    if hole_start_wale == 0:
        indicator = 1 
        # if hole_height % 2 == 0:
        parent_loops = top_course[hole_width: ]
        for _ in range(hole_height):
            next_row = []
            for parent_id in [*reversed(parent_loops)]:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            parent_loops = next_row
        #next_row is used to hold loops of the recovery row  
        next_row = []
        for parent_id in [*reversed(parent_loops)]:
            child_id, loop = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(loop)
            knitGraph.connect_loops(parent_id, child_id)
        #add remain new loops for the recovery row, these new loops are increase loops (i.e., no parent loop)
        for  i in range(hole_width):
            child_id, loop = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(loop)
        #build complete tube again based on this complete row
        parent_loops = next_row 
        for _ in range(tube_height - hole_start_course - hole_height - 1):
            next_row = []
            for parent_id in parent_loops:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            parent_loops = next_row 

    #case 2: when hole_end_wale  == 2*tube_width 
    # hole_end_wale = hole_start_wale + hole_width
    if hole_end_wale  == 2*tube_width:
        indicator = 2
        parent_loops = top_course[ :hole_start_wale] 
        next_row = []
        for parent_id in parent_loops:
            child_id, loop = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(loop)
            knitGraph.connect_loops(parent_id, child_id)
        parent_loops = next_row
        # -1 is because we have build one row above
        for _ in range(hole_height - 1): 
            next_row = []
            for parent_id in [*reversed(parent_loops)]:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            parent_loops = next_row
        #next_row is used to hold loops of the recovery row  
        next_row = []
        for parent_id in [*reversed(parent_loops)]:
            child_id, loop = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(loop)
            knitGraph.connect_loops(parent_id, child_id)
        #add remain new loops for the recovery row, these new loops are increase loops (i.e., no parent loop)
        for i in range(hole_width):
            child_id, loop = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(loop)
        #build complete tube again based on this complete row
        parent_loops = next_row 
        for _ in range(tube_height - hole_start_course - hole_height - 1):
            next_row = []
            for parent_id in parent_loops: # not reversed because it is tube
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            parent_loops = next_row 
    
    #case 3: when hole_start_wale != 0 and hole_end_wale != 2*tube_width. More than one yarns are needed for this case.
    if hole_start_wale > 0 and hole_end_wale < 2*tube_width:
        assert new_carrier!=None, f'new carrier is needed to inroduce new yarn'
        indicator = 3
        #now introduce the new yarn and add loops
        new_yarn = Yarn("new_yarn", knitGraph, carrier_id=new_carrier)
        knitGraph.add_yarn(new_yarn)
        parent_loops_old_yarn = top_course[hole_start_wale + hole_width: ]
        parent_loops_new_yarn = top_course[ :hole_start_wale]
        for _ in range(hole_height):
            next_row = []
            next_row_new_yarn = []
            #for old yarn
            for parent_id in [*reversed(parent_loops_old_yarn)]:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            parent_loops_old_yarn = next_row
            # print('parent_loops_old_yarn_1', parent_loops_old_yarn)
            #for new yarn
            for parent_id in parent_loops_new_yarn:
                child_id, loop = new_yarn.add_loop_to_end()
                # print('new yarn loop', child_id)
                next_row_new_yarn.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            parent_loops_new_yarn = [*reversed(next_row_new_yarn)]
        # print('knit_graph.last_loop_id_1', knitGraph.last_loop_id)
        #next_row is used to hold loops of the recovery row  
        #keep adding loops and connect until loop over the parent_loops 
        next_row = []
        for parent_id in [*reversed(parent_loops_old_yarn)]:
            child_id, loop = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(loop)
            knitGraph.connect_loops(parent_id, child_id)
        # print('knit_graph.last_loop_id_2', knitGraph.last_loop_id)
        
        if hole_height % 2 == 0:
        #add remain new loops for the recovery row, these new loops are increase loops (i.e., no parent loop)
            #first add loops that have no parents, the number of which should  = hole_width
            for i in range(hole_width):
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
            #then add remaining loops and connect them to last row of loops formed by the new yarn
            #first reverse the reversed last row of loops formed by the new yarn
            parent_loops_new_yarn = [*reversed(parent_loops_new_yarn)]
            #add and connect
            for parent_id in parent_loops_new_yarn:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
        elif hole_end_wale == 2*tube_width -1 and hole_height % 2 == 1:
        #add remain new loops for the recovery row, these new loops are increase loops (i.e., no parent loop)
            #first add loops that have no parents, the number of which should  = hole_width
            for i in range(hole_width):
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
            #then add remaining loops and connect them to last row of loops formed by the new yarn
            #should not reverse the reversed last row of loops formed by the new yarn
            #add and connect
            for parent_id in parent_loops_new_yarn:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
        elif hole_end_wale != 2*tube_width - 1 and hole_height % 2 ==1:
        #first add loops and connect, followed by adding loops that have no parents. (opposite of what happen for the above condition)
            parent_loops_new_yarn = [*reversed(parent_loops_new_yarn)]
            for parent_id in parent_loops_new_yarn:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            #add loops that have no parents, the number of which should  = hole_width
            for i in range(hole_width):
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
        #build complete tube again based on this complete row
        parent_loops = next_row 
        # print('tube_height - hole_start_course - hole_height - 1', tube_height - hole_start_course - hole_height - 1)
        for _ in range(tube_height - hole_start_course - hole_height - 1):
            next_row = []
            for parent_id in parent_loops:
                child_id, loop = yarn.add_loop_to_end()
                next_row.append(child_id)
                knitGraph.add_loop(loop)
                knitGraph.connect_loops(parent_id, child_id)
            parent_loops = next_row 
        # print('knit_graph.last_loop_id_4', knitGraph.last_loop_id)
        # print('knit_graph.graph.nodes', knitGraph.graph.nodes)
    return knitGraph, indicator, hole_end_wale

def rib(width: int = 4, height: int = 4, rib_width: int = 1) -> Knit_Graph:
    """
    :param rib_width: determines how many columns of knits and purls are in a single rib.
    (i.e.) the first course of width=4 and rib_width=2 will be kkpp. Always start with knit columns
    :param width: a number greater than 0 to set the number of stitches in the swatch
    :param height: A number greater than 2 to set the number of courses in the swatch
    :return: A knit graph with a repeating columns of knits (back to front) then purls (front to back).
    """
    assert width > 0
    assert height > 1
    assert rib_width <= width

    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph)
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        # loop_id, loop = yarn.add_loop_to_end(width)
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    prior_row = first_row
    next_row = []
    for column, parent_id in reversed([*enumerate(prior_row)]):
        child_id, child = yarn.add_loop_to_end()
        # child_id, child = yarn.add_loop_to_end(width)
        next_row.append(child_id)
        knitGraph.add_loop(child)
        rib_id = int(int(column) / int(rib_width))
        if rib_id % 2 == 0:  # even ribs:
            pull_direction = Pull_Direction.BtF
        else:
            pull_direction = Pull_Direction.FtB
        knitGraph.connect_loops(parent_id, child_id, pull_direction=pull_direction)

    for _ in range(2, height):
        prior_row = next_row
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            # child_id, child = yarn.add_loop_to_end(width)
            next_row.append(child_id)
            knitGraph.add_loop(child)
            grand_parent = [*knitGraph.graph.predecessors(parent_id)][0]
            parent_pull_direction = knitGraph.graph[grand_parent][parent_id]["pull_direction"]
            knitGraph.connect_loops(parent_id, child_id, pull_direction=parent_pull_direction)

    return knitGraph


def seed(width: int = 4, height=4) -> Knit_Graph:
    """
    :param width: a number greater than 0 to set the number of stitches in the swatch
    :param height: A number greater than 0 to set teh number of courses in the swatch
    :return: A knit graph with a checkered pattern of knit and purl stitches of width and height size.
    The first stitch should be a knit
    """
    assert width > 0
    assert height > 1

    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph)
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    prior_row = first_row
    next_row = []
    for column, parent_id in enumerate(reversed(prior_row)):
        child_id, child = yarn.add_loop_to_end()
        next_row.append(child_id)
        knitGraph.add_loop(child)
        if column % 2 == 0:  # even seed:
            pull_direction = Pull_Direction.BtF
        else:
            pull_direction = Pull_Direction.FtB
        knitGraph.connect_loops(parent_id, child_id, pull_direction=pull_direction)

    for _ in range(2, height):
        prior_row = next_row
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(child)
            grand_parent = [*knitGraph.graph.predecessors(parent_id)][0]
            parent_pull_direction = knitGraph.graph[grand_parent][parent_id]["pull_direction"]
            knitGraph.connect_loops(parent_id, child_id, pull_direction=parent_pull_direction.opposite())
    print('parent_pull_direction',parent_pull_direction)
    print('parent_pull_direction.opposite()', parent_pull_direction.opposite())
    return knitGraph

def hole_by_short_row(hole_position: List[int], hole_width: int = 1, hole_height: int = 1, width: int = 5, height: int = 5) -> Knit_Graph:
    # hole_position: List[int], i.e., [course_index, wale_index]
    """
    :param buffer_height: THe height of the buffer on top and bottom
    :param width: the width of the swatch, must be greater than 4
    :return: a knitgraph with width in stockinette with 4 short rows in the center of a buffer
    """
    # assert width > 4, "Not enough stitches to short row"

    # Get the base of the graph
    hole_course_index = hole_position[0]
    hole_wale_index = hole_position[1]

    buffer_height = hole_course_index
    knit_graph = stockinette(width=width, height=buffer_height)

    # print('[*knit_graph.yarns.values()][0]', [*knit_graph.yarns.values()][0])
    yarn = [*knit_graph.yarns.values()][0]

    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    if len(course_to_loop_ids) == 1:
        top_course = course_to_loop_ids[0]
    else:
        top_course_index = max(*course_to_loop_ids.keys())
        top_course = course_to_loop_ids[top_course_index]

    # Knit to last two loops and reserve on left
    reversed_top_course = [*reversed(top_course)]
    if hole_course_index % 2 == 0:
        left_border = hole_wale_index
        grow_area = reversed_top_course[:left_border]
        right_border = hole_wale_index + hole_width
        reserved_top_right = reversed_top_course[right_border:]
    else:
        right_border = width - (hole_wale_index + hole_width)
        grow_area = reversed_top_course[:right_border]
        left_border = - hole_wale_index 
        reserved_top_left = reversed_top_course[left_border:]

    for _ in range(hole_course_index, hole_course_index + hole_height):
        next_row = []
        for parent_id in grow_area:
            child_id, child = yarn.add_loop_to_end()
            # child_id, child = yarn.add_loop_to_end(width)
            next_row.append(child_id)
            knit_graph.add_loop(child)
            knit_graph.connect_loops(parent_id, child_id)
        grow_area = reversed(next_row)

    # Knit over last row and reserved loops on left
    current_row = [*reversed(next_row)]
    if hole_course_index % 2 == 0:
        current_row.extend(reserved_top_right)
    else: 
        current_row.extend(reserved_top_left)
    print('current_row', current_row)

    next_course = []
    if (hole_course_index + hole_height) % 2 == 1:
        left = width - (hole_wale_index + hole_width)
    else:
        left = hole_wale_index
    for _ in range(width):
        child_id, child = yarn.add_loop_to_end()
        # child_id, child = yarn.add_loop_to_end(width)
        knit_graph.add_loop(child)
        next_course.append(child_id)
        if _ not in range(left, left + hole_width):
            print('{} not in range {}'.format(_, (left, left + hole_width)))
            parent_id = current_row.pop(0)
            knit_graph.connect_loops(parent_id, child_id)

    # add 5 stst rows
    prior_row = next_course
    # for _ in range(0, buffer_height):
    for _ in range(hole_course_index + hole_height + 1, height):
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            # child_id, child = yarn.add_loop_to_end(width)
            next_row.append(child_id)
            knit_graph.add_loop(child)
            knit_graph.connect_loops(parent_id, child_id)
        prior_row = next_row

    return knit_graph

def twisted_stripes(width: int = 4, height=5, left_twists: bool = True) -> Knit_Graph:
    """
    :param left_twists: if True, make the left leaning stitches in front, otherwise right leaning stitches in front
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: A knitgraph with repeating pattern of twisted stitches surrounded by knit wales
    """
    assert width % 4 == 0, "Pattern is 4 loops wide"
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph)
    knitGraph.add_yarn(yarn)

    # Add the first course of loops
    first_course = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_course.append(loop_id)
        knitGraph.add_loop(loop)

    def add_loop_and_knit(p_id, depth=0, parent_offset: int = 0, pull_direction= Pull_Direction.BtF):
        """
        adds a loop by knitting to the knitgraph
        :param parent_offset: Set the offset of the parent loop in the cable. offset = parent_index - child_index
        :param p_id: the parent loop's id
        :param depth: the crossing- depth to knit at
        """
        child_id, child = yarn.add_loop_to_end()
        next_course.append(child_id)
        knitGraph.add_loop(child)
        knitGraph.connect_loops(p_id, child_id, depth=depth, parent_offset=parent_offset, pull_direction=pull_direction)

    if left_twists:  # set the depth for the first loop in the twist (1 means it will cross in front of other stitches)
        twist_depth = 1
    else:
        twist_depth = -1

    # add new courses
    prior_course = first_course
    for course in range(1, height):
        next_course = []
        reversed_prior_course = [*reversed(prior_course)]

        print('reversed_prior_course', reversed_prior_course)
        for col, parent_id in enumerate(reversed_prior_course):
            #if course % 2 == 0 or col % 4 == 0 or col % 4 == 3:  # knit on even rows and before and after twists
            if course % 2 == 0 or col % 4 == 0 or col % 4 == 3:
                add_loop_and_knit(parent_id)
            elif col % 4 == 1:
                next_parent_id = reversed_prior_course[col + 1]
                print('col',col, col+1, next_parent_id)
                # add_loop_and_knit(next_parent_id, depth=twist_depth, parent_offset=1)
                add_loop_and_knit(next_parent_id, depth=twist_depth, parent_offset=-1)
                twist_depth = -1 * twist_depth  # switch depth for neighbor
            elif col % 4 == 2:
                next_parent_id = reversed_prior_course[col - 1]
                print('col',col, col-1, next_parent_id)
                # add_loop_and_knit(next_parent_id, depth=twist_depth, parent_offset=-1)
                add_loop_and_knit(next_parent_id, depth=twist_depth, parent_offset=1)
                twist_depth = -1 * twist_depth  # switch depth for next twist
            
        prior_course = next_course

    return knitGraph


def both_twists(height=20) -> Knit_Graph:
    """
    :param left_twists: if True, make the left leaning stitches in front, otherwise right leaning stitches in front
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: A knitgraph with repeating pattern of twisted stitches surrounded by knit wales
    """
    width = 10
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph)
    knitGraph.add_yarn(yarn)

    # Add the first course of loops
    first_course = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_course.append(loop_id)
        knitGraph.add_loop(loop)

    def add_loop_and_knit(p_id, depth=0, parent_offset: int = 0):
        """
        adds a loop by knitting to the knitgraph
        :param parent_offset: Set the offset of the parent loop in the cable. offset = parent_index - child_index
        :param p_id: the parent loop's id
        :param depth: the crossing- depth to knit at
        """
        child_id, child = yarn.add_loop_to_end()
        next_course.append(child_id)
        knitGraph.add_loop(child)
        knitGraph.connect_loops(p_id, child_id, depth=depth, parent_offset=parent_offset)

    # add new courses
    prior_course = first_course
    for course in range(1, height):
        next_course = []
        reversed_prior_course = [*reversed(prior_course)]
        for col, parent_id in enumerate(reversed_prior_course):
            if course % 2 == 1 or col in {0, 1, 4, 5,8, 9}:  # knit on odd rows and borders or middle
                add_loop_and_knit(parent_id)
            elif col == 2:
                parent_id = reversed_prior_course[3]
                add_loop_and_knit(parent_id, depth=-1, parent_offset=-1)
            elif col == 3:
                parent_id = reversed_prior_course[2]
                add_loop_and_knit(parent_id, depth=1, parent_offset=1)
            elif col == 6:
                parent_id = reversed_prior_course[7]
                add_loop_and_knit(parent_id, depth=1, parent_offset=-1)
            elif col == 7:
                parent_id = reversed_prior_course[6]
                add_loop_and_knit(parent_id, depth=-1, parent_offset=1)
        prior_course = next_course

    return knitGraph


# def twisted_stripes(width: int = 4, height=5) -> Knit_Graph:
#     """
#     :param width: the number of stitches of the swatch
#     :param height:  the number of courses of the swatch
#     :return: A knitgraph with repeating pattern of twisted stitches surrounded by knit wales
#     """
#     knitGraph = Knit_Graph()
#     yarn = Yarn("yarn")
#     knitGraph.add_yarn(yarn)
#     first_row = []
#     for _ in range(0, width):
#         loop_id, loop = yarn.add_loop_to_end()
#         first_row.append(loop_id)
#         knitGraph.add_loop(loop)
#
#     def add_loop_and_knit(p_id, depth=0):
#         """
#         adds a loop by knitting to the knitgraph
#         :param p_id: the parent loop's id
#         :param depth: the crossing- depth to knit at
#         """
#         child_id, child = yarn.add_loop_to_end()
#         next_row.append(child_id)
#         knitGraph.add_loop(child)
#         knitGraph.connect_loops(p_id, child_id, depth=depth)
#
#     prior_row = first_row
#     first_depth = 1  # switch between left and right twists
#     for row in range(1, height):
#         next_row = []
#         prior_parent_id = -1
#         reversed_prior_row = [*reversed(prior_row)]
#         for col, parent_id in enumerate(reversed_prior_row):
#             if row % 2 == 0 or col % 4 == 0 or col % 4 == 3:  # knit on even rows and before and after twists
#                 add_loop_and_knit(parent_id)
#             elif col % 4 == 1:
#                 prior_parent_id = parent_id
#                 next_parent_id = reversed_prior_row[col + 1]
#                 add_loop_and_knit(next_parent_id, first_depth)  # set to opposite depth of crossing partner
#             elif col % 4 == 2:
#                 add_loop_and_knit(prior_parent_id, -1 * first_depth)  # set to opposite depth of crossing partner
#                 first_depth = -1 * first_depth  # switch depth for next twist course
#         prior_row = next_row
#
#     return knitGraph


def lace(width: int = 4, height: int = 4):
    """
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: a knitgraph with k2togs and yarn-overs surrounded by knit wales
    """
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph)
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    def add_loop_and_knit(p_id, offset: int = 0):
        """
        Knits a loop into the graph
        :param p_id: the id of the parent loop being knit through
        :return: the id of the child loop created
        """
        c_id, c = yarn.add_loop_to_end()
        next_row.append(c_id)
        knitGraph.add_loop(c)
        knitGraph.connect_loops(p_id, c_id, pull_direction=Pull_Direction.BtF, parent_offset=offset)
        return c_id

    prior_row = first_row
    for row in range(1, height):
        next_row = []
        prior_parent_id = -1
        reversed_prior_row = [*reversed(prior_row)]
        for col, parent_id in enumerate(reversed_prior_row):
            if row % 2 == 0 or col % 4 == 0 or col % 4 == 3:  # knit on even rows and before and after twists
                add_loop_and_knit(parent_id)
            elif col % 4 == 1:
                child_id, child = yarn.add_loop_to_end()
                knitGraph.add_loop(child)
                next_row.append(child_id)  # yarn over
                prior_parent_id = parent_id
            elif col % 4 == 2:
                child_id = add_loop_and_knit(parent_id)
                knitGraph.connect_loops(prior_parent_id, child_id, parent_offset=-1)
        prior_row = next_row

    return knitGraph


def lace_and_twist():
    """

    :return:
    """
    width = 13
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn", knitGraph)
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    next_row = []
    for _ in range(0, width):
        child_id, child = yarn.add_loop_to_end()
        knitGraph.add_loop(child)
        next_row.append(child_id)
    # knit edge
    knitGraph.connect_loops(0, 25)
    knitGraph.connect_loops(12, 13)
    # bottom of decrease stack
    knitGraph.connect_loops(1, 24, stack_position=0)
    knitGraph.connect_loops(6, 19, stack_position=0)
    knitGraph.connect_loops(11, 14, stack_position=0)
    # 2nd of decrease stack
    knitGraph.connect_loops(2, 24, stack_position=1, parent_offset=1)
    knitGraph.connect_loops(5, 19, stack_position=1, parent_offset=-1)
    knitGraph.connect_loops(10, 14, stack_position=1, parent_offset=-1)
    # 3rd of decrease stack
    knitGraph.connect_loops(7, 19, stack_position=2, parent_offset=1)
    # twist  right
    knitGraph.connect_loops(3, 21, depth=1, parent_offset=1)
    knitGraph.connect_loops(4, 22, depth=-1, parent_offset=-1)
    # twist left
    knitGraph.connect_loops(8, 16, depth=-1, parent_offset=1)
    knitGraph.connect_loops(9, 17, depth=1, parent_offset=-1)

    for parent_id in reversed(next_row):
        child_id, child = yarn.add_loop_to_end()
        knitGraph.add_loop(child)
        knitGraph.connect_loops(parent_id, child_id)

    return knitGraph


def short_rows(width: int = 10, buffer_height: int = 2) -> Knit_Graph:
    """
    :param buffer_height: THe height of the buffer on top and bottom
    :param width: the width of the swatch, must be greater than 4
    :return: a knitgraph with width in stockinette with 4 short rows in the center of a buffer
    """
    assert width > 4, "Not enough stitches to short row"
    # Get the base of the graph
    knit_graph = stockinette(width=width, height=buffer_height)
    # print('[*knit_graph.yarns.values()][0]', [*knit_graph.yarns.values()][0])
    yarn = [*knit_graph.yarns.values()][0]

    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    if len(course_to_loop_ids) == 1:
        top_course = course_to_loop_ids[0]
    else:
        top_course_index = max(*course_to_loop_ids.keys())
        top_course = course_to_loop_ids[top_course_index]
    print(course_to_loop_ids, course_to_loop_ids.keys(), *course_to_loop_ids.keys())
    print('top course', top_course)
    # Knit to last two loops and reserve on left
    next_row = []
    reversed_top_course = [*reversed(top_course)]
    reserved_top_left = reversed_top_course[-2:]
    for parent_id in reversed_top_course[:-2]:
        child_id, child = yarn.add_loop_to_end()
        next_row.append(child_id)
        knit_graph.add_loop(child)
        knit_graph.connect_loops(parent_id, child_id)

    # Knit to last two loops and reserve on right
    top_course = next_row
    next_row = []
    reversed_top_course = [*reversed(top_course)]
    reserved_top_right = reversed_top_course[-2:]
    for parent_id in reversed_top_course[:-2]:
        child_id, child = yarn.add_loop_to_end()
        next_row.append(child_id)
        knit_graph.add_loop(child)
        knit_graph.connect_loops(parent_id, child_id)

    # Knit over last row and reserved loops on left
    top_course = next_row
    next_row = []
    reversed_top_course = [*reversed(top_course)]
    reversed_top_course.extend(reserved_top_left)
    for parent_id in reversed_top_course:
        child_id, child = yarn.add_loop_to_end()
        next_row.append(child_id)
        knit_graph.add_loop(child)
        knit_graph.connect_loops(parent_id, child_id)

    # knit over last row and reserved loops on right
    top_course = next_row
    next_row = []
    reversed_top_course = [*reversed(top_course)]
    reversed_top_course.extend(reserved_top_right)
    for parent_id in reversed_top_course:
        child_id, child = yarn.add_loop_to_end()
        next_row.append(child_id)
        knit_graph.add_loop(child)
        knit_graph.connect_loops(parent_id, child_id)

    # add 5 stst rows
    prior_row = next_row
    for _ in range(0, buffer_height):
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            next_row.append(child_id)
            knit_graph.add_loop(child)
            knit_graph.connect_loops(parent_id, child_id)
        prior_row = next_row

    return knit_graph
