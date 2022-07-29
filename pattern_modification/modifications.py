from typing import Optional, List
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph
from debugging_tools.knit_graph_viz import visualize_knitGraph
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler

def test_cable():
    pattern = r"""
        1st row k, lc2|2, k, rc2|2, [k] to end.
        all ws rows p.
        3rd row k 2, lc2|1, k, rc1|2, [k] to end.
        5th row k 3, lc1|1, k, rc1|1, [k] to end.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(11, 6, pattern)
    # visualize_knitGraph(knit_graph)
    return knit_graph
    

def test_stst():
    pattern = "all rs rows k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(8, 6, pattern)
    # visualize_knitGraph(knit_graph, "stst.html")
    # visualize_knitGraph(knit_graph)
    return knit_graph


def add_hole(knit_graph: Knit_Graph, hole_start_row:int, hole_start_wale:int, hole_height:int, hole_width:int):
    yarns = [*knit_graph.yarns.values()]
    yarn = yarns[0]
    node_to_delete = []
    new_yarn_course_to_loop_ids= {}
    old_yarn_course_to_margin_loop_ids = {}
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    pattern_height = len(course_to_loop_ids)
    pattern_width = max([len(i) for i in [*course_to_loop_ids.values()]])
    assert hole_start_row + hole_height < pattern_height, f'hole height is too large that it is exceeding the knit graph border'
    #first remove nodes in hole
    for course_id in range(hole_start_row, hole_start_row + hole_height):
        if course_id % 2 == 0:
            loop_ids = course_to_loop_ids[course_id][hole_start_wale:(hole_start_wale+hole_width)]
        elif course_id % 2 == 1:
            loop_ids = course_to_loop_ids[course_id][pattern_width-(hole_start_wale+hole_width):pattern_width - hole_start_wale]
        node_to_delete.extend(loop_ids)
    #check if any node violates the constraint for a node to be part of a hole
    for node in node_to_delete:
        #first, each node should have exactly one parent. 
        #If more than one, it is part of a decrease; If less than one, it itself is an increase.
        #Likewise, each node should have exactly one child.
        #If no child, it is a slip.
        parent_ids = [*knit_graph.graph.predecessors(node)]
        child_ids = [*knit_graph.graph.successors(node)]
        if len(parent_ids) != 1:
            print(f'node {node} is not qualified for a hole for having {len(parent_ids)} parents')
            exit()
        if len(child_ids) != 1:
            print(f'node {node} is not qualified for a hole for having {len(child_ids)} parents')
            exit()
        #Second, on knit graph, any edge related to the node must have a parent offset that is 0
        parent_id = parent_ids[0]
        parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
        if parent_offset != 0:
            print(f'node {node} is not qualified for a hole for having parent offset of {parent_offset}')
            exit()
        child_id = child_ids[0]
        child_offset = knit_graph.graph[node][child_id]["parent_offset"]
        if parent_offset != 0:
            print(f'node {node} is not qualified for a hole for having child offset of {child_offset}')
            exit()
        #Third, on yarn graph, the number of yarn edges related to the node must be 2
        #If less than one, it can be node on the border, or part of a short row
        parent_ids = [*yarn.yarn_graph.predecessors(node)]
        child_ids = [*yarn.yarn_graph.successors(node)]
        if len(parent_ids) != 1 or len(child_ids) != 1:
            print(f'node {node} is not qualified for a hole for having no parent node or child node on yarn')
            exit()
        #Fourth, on yarn graph, parent node and child node of the node should be on the same course
        #If not, it can be a slip on sheet
        parent_id = parent_ids[0]
        child_id = child_ids[0]
        if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
            print(f'node {node} is not qualified for a hole for having parent node and child node that are not on the same course')
            exit()
    
    knit_graph.graph.remove_nodes_from(node_to_delete)
    yarn.yarn_graph.remove_nodes_from(node_to_delete)
    print('node_to_delete', node_to_delete)
    print('course_to_loop_ids', course_to_loop_ids)
    
    if hole_start_row % 2 == 0:
        for course_id in range(hole_start_row, hole_start_row + hole_height):
            if course_id % 2 == 0:
                old_yarn_course_to_margin_loop_ids[course_id] = course_to_loop_ids[course_id][hole_start_wale-1]
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id][hole_start_wale + hole_width:]
            else:
                old_yarn_course_to_margin_loop_ids[course_id] = course_to_loop_ids[course_id][pattern_width - hole_start_wale]
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id][:pattern_width - (hole_start_wale + hole_width)]
        if hole_height % 2 == 0:
            pass
        elif hole_height % 2 == 1:
            for course_id in range(hole_start_row + hole_height, pattern_height):
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
        # reconnect old yarn at its margin
        for course_id in old_yarn_course_to_margin_loop_ids:
            if course_id%2==0 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                start_node = old_yarn_course_to_margin_loop_ids[course_id]
                next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                yarn.yarn_graph.add_edge(start_node, next_node)

    if hole_start_row % 2 == 1:
        for course_id in range(hole_start_row, hole_start_row + hole_height):
            if course_id % 2 == 0:
                old_yarn_course_to_margin_loop_ids[course_id] = course_to_loop_ids[course_id][hole_start_wale-1]
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id][:hole_start_wale]
            else:
                old_yarn_course_to_margin_loop_ids[course_id] = course_to_loop_ids[course_id][pattern_width - hole_start_wale]
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id][-hole_start_wale:]
        if hole_height % 2 == 0:
            pass
        elif hole_height % 2 == 1:
            for course_id in range(hole_start_row + hole_height, pattern_height):
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
        # reconnect old yarn at its margin
        for course_id in old_yarn_course_to_margin_loop_ids:
            if course_id%2==0 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                start_node = old_yarn_course_to_margin_loop_ids[course_id]
                next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                yarn.yarn_graph.add_edge(start_node, next_node)

    print('old_yarn_course_to_margin_loop_ids', old_yarn_course_to_margin_loop_ids)
    print('new_yarn_course_to_loop_ids', new_yarn_course_to_loop_ids)
    
    # remove loop_ids from old yarn and add loop_ids to new yarn and connect them
    new_carrier = 4
    assert new_carrier != None, f'new carrier is needed to introduce new yarn'
    new_yarn = Yarn("new_yarn", knit_graph, carrier_id=new_carrier)
    knit_graph.add_yarn(new_yarn)
    for course_id in new_yarn_course_to_loop_ids:
        loop_ids = new_yarn_course_to_loop_ids[course_id]
        for loop_id in loop_ids:
            yarn.yarn_graph.remove_node(loop_id)
            child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)

    return knit_graph

if __name__ == '__main__':
    # knit_graph = test_stst()
    knit_graph = test_cable()
    knitGraph = add_hole(knit_graph, hole_start_row=1, hole_start_wale=5, hole_height=1, hole_width=1)
    visualize_knitGraph(knitGraph)