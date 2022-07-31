from typing import Optional, List, Dict
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
import warnings

def test_short_rows():
    knit_graph = short_rows(5, buffer_height=1)
    # _, __ = knit_graph.get_courses()
    # visualize_knitGraph(knit_graph)
    return knit_graph

def test_lace():
    knit_graph = lace(8, 8)
    visualize_knitGraph(knit_graph)
    return knit_graph

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
    visualize_knitGraph(knit_graph)
    return knit_graph

def add_hole1(knit_graph: Knit_Graph, hole_start_row:int, hole_start_wale:int, hole_height:int, hole_width:int, unmodified: bool, new_carrier: int = None):
    yarns = [*knit_graph.yarns.values()]
    #since given knit graph has only one yarn before being modified
    yarn = yarns[0]
    node_to_course_and_wale = {}
    course_and_wale_to_node = {}
    node_to_delete = []
    new_yarn_course_to_loop_ids= {}
    old_yarn_course_to_margin_loop_ids = {}
    new_yarn_course_to_margin_loop_ids = {}
    loop_ids_to_course, course_to_loop_ids, loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified=True)
    pattern_height = len(course_to_loop_ids)
    pattern_width = max([len(i) for i in [*course_to_loop_ids.values()]])
    assert hole_start_row + hole_height < pattern_height, f'hole height is too large that it is exceeding the knit graph border'
    #if taking (hole_start_row, hole_start_wale, hole_height, hole_width) as input, use below assertion
    assert hole_width <= 6, f'hole width: {hole_width} is too large to achieve the racking bound by 3 on the machine'

    def rebuild_knitgraph():    
        #get the [course, wale] coordinate of each node in the knit graph
        def get_node_course_and_wale():
            for node in knit_graph.graph.nodes:
                # node_to_course_and_wale[node] = []
                course = loop_ids_to_course[node]
                wale = loop_ids_to_wale[node]
                node_to_course_and_wale[node] = [course, wale]
            #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
            course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
            # print('loop_ids_to_course', loop_ids_to_course)
            print('course_and_wale_to_node', course_and_wale_to_node)
            print('node_to_course_and_wale', node_to_course_and_wale)
        get_node_course_and_wale()
        print('haha', course_and_wale_to_node)
        print('lala', node_to_course_and_wale)
        #identify location of the nodes to delete
        def get_nodes_to_delete():
            locations_to_delete_node = []
            for course in range(hole_start_row, hole_start_row + hole_height):
                for wale in range(hole_start_wale, hole_start_wale + hole_width):
                    locations_to_delete_node.append((course, wale))
            print('locations_to_delete_node', locations_to_delete_node)
            for location in locations_to_delete_node:
                if location not in course_and_wale_to_node.keys():
                    print(f'Error: no node is found at given location {location}')
                    exit()
                node = course_and_wale_to_node[location]
                node_to_delete.append(node)
            print('node_to_delete', node_to_delete)
        get_nodes_to_delete()

        def hole_location_warnings():
            #check if any node violates the constraint for a node to be part of a hole
            for node in node_to_delete:
                #first, each node should have exactly one parent. 
                #If more than one, it is part of a decrease; If less than one, it itself is an increase.
                #Likewise, each node should have exactly one child (it can only be one or zero child).
                #If no child, it might be a node on top course/top border, which we do not consider. 
                #Or simply it can be an error node in the knit graph signaling something wrong with the program.
                parent_ids = [*knit_graph.graph.predecessors(node)]
                child_ids = [*knit_graph.graph.successors(node)]
                if len(parent_ids) != 1:
                    # warnings.warn("xxx")
                    print(f'Warning: node {node} might break a special stitch for having {len(parent_ids)} parents')
                if len(child_ids) != 1:
                    print(f'Warning: node {node} is suspicious or a node on border for for having {len(child_ids)} child')
                #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
                #If not, it is part of decrease or cable.
                parent_id = parent_ids[0]
                parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
                if parent_offset != 0:
                    print(f'Warning: node {node} might break a special stitch for having parent offset of {parent_offset}')
                child_id = child_ids[0]
                child_offset = knit_graph.graph[node][child_id]["parent_offset"]
                if child_offset != 0:
                    print(f'Warning: node {node} might break a special stitch for having child offset of {child_offset}')
                #Third, on yarn graph, the number of yarn edges related to the node must be 2
                #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
                yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
                yarn_child_ids = [*yarn.yarn_graph.successors(node)]
                if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                    print(f'Warning: node {node} is suspicious for having no parent node or child node on yarn')
                #Fourth, on yarn graph, parent node and child node of the node should be on the same course
                #If not, it might be part of short row, or a node on the border. Currently, we do not consider add hole on border.
                parent_id = yarn_parent_ids[0]
                child_id = yarn_child_ids[0]
                if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
                    print(f'Warning: node {node} might break a special stitch or a node on border for having parent node and child node that are not on the same course')
                
        def hole_location_errors():
            for node in node_to_delete:
                #First, if a node has no child and is not a node on top course/top border 
                #it would be an error node in the knit graph signaling something wrong with the program.
                parent_ids = [*knit_graph.graph.predecessors(node)]
                child_ids = [*knit_graph.graph.successors(node)]
                course_id = node_to_course_and_wale[node][0]
                top_course_id = pattern_height - 1
                if len(child_ids) != 1 and course_id != top_course_id:
                    print(f'Error: node {node} is suspicious for for having {len(child_ids)} child')
                    exit()
            
            #Second, on yarn graph, the number of yarn edges related to the node must be 2
            #If less than one, and is not the start node or end node of the yarn, it would be a huge error when adding loop with the yarn
            for node in yarn.yarn_graph.nodes:
                yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
                yarn_child_ids = [*yarn.yarn_graph.successors(node)]
                if node not in [0, len(yarn.yarn_graph.nodes)-1]:
                    if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                        print(f'Error: node {node} is suspicious for having no parent node or child node on yarn')
                        exit()
            
        hole_location_errors()
        hole_location_warnings()
        
        # @deprecated("Deprecated because we assume users know where she/he is going to place the hole, so instead of strictly limiting
        # the user on the place to generate a hole, more freedom is offered to the users. May be a good idea to send warning rather than
        # error")
        #check if any node violates the constraint for a node to be part of a hole
        def deprecated_hole_location_constraints():
            #check if any node violates the constraint for a node to be part of a hole
            for node in node_to_delete:
                #first, each node should have exactly one parent. 
                #If more than one, it is part of a decrease; If less than one, it itself is an increase.
                #Likewise, each node should have exactly one child (it can only be one or zero child).
                #If no child, it might be a node on top course/top border, if deleted, will cause the whole knitted item to unravel. Or simply
                #it can be an error node in the knit graph signaling something wrong with the program.
                parent_ids = [*knit_graph.graph.predecessors(node)]
                child_ids = [*knit_graph.graph.successors(node)]
                if len(parent_ids) != 1:
                    print(f'Error: node {node} is not qualified for a hole for having {len(parent_ids)} parents')
                    exit()
                if len(child_ids) != 1:
                    print(f'Error: node {node} is not qualified for a hole for having {len(child_ids)} parents')
                    exit()
                #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
                #If not, it is part of decrease or cable.
                parent_id = parent_ids[0]
                parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
                if parent_offset != 0:
                    print(f'Error: node {node} is not qualified for a hole for having parent offset of {parent_offset}')
                    exit()
                child_id = child_ids[0]
                child_offset = knit_graph.graph[node][child_id]["parent_offset"]
                if child_offset != 0:
                    print(f'Error: node {node} is not qualified for a hole for having child offset of {child_offset}')
                    exit()
                #Third, on yarn graph, the number of yarn edges related to the node must be 2
                #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
                parent_ids = [*yarn.yarn_graph.predecessors(node)]
                child_ids = [*yarn.yarn_graph.successors(node)]
                if len(parent_ids) != 1 or len(child_ids) != 1:
                    print(f'Error: node {node} is not qualified for a hole for having no parent node or child node on yarn')
                    exit()
                #Fourth, on yarn graph, parent node and child node of the node should be on the same course
                #If not, it might be part of short row, or a node on the border. If node on border got deleted, 
                #will cause the whole knitted item to unravel.
                parent_id = parent_ids[0]
                child_id = child_ids[0]
                if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
                    print(f'Error: node {node} is not qualified for a hole for having parent node and child node that are not on the same course')
                    exit()
                #Fifth is related to margin nodes, that is, nodes that are immediately on the two side of the hole. Check 
            
        #remove the nodes for hole from both knit graph and yarn
        def remove_hole_nodes_from_graph():
            # print(f'knit graph edges before deleting the nodes is {knit_graph.graph.edges}, number of {len(knit_graph.graph.edges)}')
            knit_graph.graph.remove_nodes_from(node_to_delete)
            # print(f'knit graph edges after deleting the nodes is {knit_graph.graph.edges}, number of {len(knit_graph.graph.edges)}')
            yarn.yarn_graph.remove_nodes_from(node_to_delete)
            #And update dict: node_to_course_and_wale and dict: course_and_wale_to_node
            #remove nodes from node position dict: node_to_course_and_wale
            for node in node_to_delete:
                del node_to_course_and_wale[node]
            #remove nodes from course_and_wale_to_node with updated "node_to_course_and_wale"
            course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
            print('course_and_wale_to_node after deleting nodes', course_and_wale_to_node)
            print('node_to_course_and_wale after deleting nodes', node_to_course_and_wale)
        remove_hole_nodes_from_graph()

        def get_new_yarn_loop_ids():
            if hole_start_row % 2 == 0:
                #new yarn spread between the hole_end_wale and the last wale_id, old yarn is between the wale_id = 0 to the hole_start_wale 
                for course_id in range(hole_start_row, hole_start_row + hole_height):
                    if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                        print(f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}')
                    # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}'
                    else:
                        old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
                    if (course_id, hole_start_wale + hole_width) not in course_and_wale_to_node.keys():
                        print(f'no node is found on the new yarn margin {(course_id, hole_start_wale + hole_width)}')
                    # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale + hole_width)}'
                    else:
                        new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale + hole_width)]
                    new_yarn_course_to_loop_ids[course_id] = []
                    if course_id % 2 == 0:
                        for wale_id in range(hole_start_wale+hole_width, pattern_width):
                            if (course_id, wale_id) in course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
                    elif course_id % 2 ==1:
                        for wale_id in range(hole_start_wale+hole_width, pattern_width):
                            if (course_id, wale_id) in course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])
                
                if hole_height % 2 == 0:
                    pass
                elif hole_height % 2 == 1:
                    for course_id in range(hole_start_row + hole_height, pattern_height):
                        new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
                
            if hole_start_row % 2 == 1:
                #Contrary to the above,
                #new yarn spread between the wale_id = 0 to the hole_start_wale, old yarn is between the hole_end_wale and the last wale_id
                for course_id in range(hole_start_row, hole_start_row + hole_height):
                    if (course_id, hole_start_wale + hole_width) not in course_and_wale_to_node.keys():
                        print(f'no node is found on the old yarn margin {(course_id, hole_start_wale + hole_width)}')
                    # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale + hole_width)}'
                    else:
                        old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale + hole_width)]
                    if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                        print(f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}')
                    # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}'
                    else:
                        new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
                    new_yarn_course_to_loop_ids[course_id] = []
                    if course_id % 2 == 0:
                        for wale_id in range(0, hole_start_wale):
                            if (course_id, wale_id) in course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
                    elif course_id % 2 == 1:
                        for wale_id in range(0, hole_start_wale):
                            if (course_id, wale_id) in course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])
                if hole_height % 2 == 0:
                    pass
                elif hole_height % 2 == 1:
                    for course_id in range(hole_start_row + hole_height, pattern_height):
                        new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
            print('old_yarn_course_to_margin_loop_ids', old_yarn_course_to_margin_loop_ids)
            print('new_yarn_course_to_loop_ids', new_yarn_course_to_loop_ids)
        get_new_yarn_loop_ids()

        # reconnect old yarn at its margin
        def reconnect_old_yarn_at_margin(hole_start_row):
            if hole_start_row % 2 == 0:
                for course_id in old_yarn_course_to_margin_loop_ids: 
                    if course_id%2 == 0 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                        start_node = old_yarn_course_to_margin_loop_ids[course_id]
                        next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                        yarn.yarn_graph.add_edge(start_node, next_node)
            elif hole_start_row % 2 == 1:
                for course_id in old_yarn_course_to_margin_loop_ids: 
                    if course_id%2 == 1 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                        start_node = old_yarn_course_to_margin_loop_ids[course_id]
                        next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                        yarn.yarn_graph.add_edge(start_node, next_node)
        reconnect_old_yarn_at_margin(hole_start_row)

        '''
        WRONG! 
        #Fifth, nodes on the margin should have both child and parent, otherwise, when the neighbor node is deleted for 
        #a hole, (tbd it will be a isolated node, which is impossible)
        def deprecated_check_margin_nodes():
            for node in old_yarn_course_to_margin_loop_ids.values():
                parent_ids = [*knit_graph.graph.predecessors(node)]
                child_ids = [*knit_graph.graph.successors(node)]
                if len(parent_ids) == 0 or len(child_ids) == 0:
                    print(f'Error: unqualified hole location for margin node {node} on old yarn not having both child and parent')
                    exit()

            for node in new_yarn_course_to_margin_loop_ids.values():
                parent_ids = [*knit_graph.graph.predecessors(node)]
                child_ids = [*knit_graph.graph.successors(node)]
                if len(parent_ids) == 0 or len(child_ids) == 0:
                    print(f'Error: unqualified hole location for margin node {node} on new yarn not having both child and parent')
                    exit()
        ''' 

        # remove loop_ids from old yarn and add loop_ids to new yarn and connect them
        def remove_old_and_add_new_yarn():
            assert new_carrier != None, f'new carrier is needed to introduce new yarn'
            new_yarn = Yarn("new_yarn", knit_graph, carrier_id=new_carrier)
            knit_graph.add_yarn(new_yarn)
            for course_id in new_yarn_course_to_loop_ids:
                loop_ids = new_yarn_course_to_loop_ids[course_id]
                for loop_id in loop_ids:
                    yarn.yarn_graph.remove_node(loop_id)
                    child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
            print(f'old yarn edges are {yarn.yarn_graph.edges}, new yarn edges are {new_yarn.yarn_graph.edges}')
        remove_old_and_add_new_yarn()
        '''
        get_node_course_and_wale()
        get_nodes_to_delete()
        hole_location_errors()
        hole_location_warnings()
        remove_hole_nodes_from_graph()
        get_new_yarn_loop_ids()
        reconnect_old_yarn_at_margin
        remove_old_and_add_new_yarn()
        '''
        visualize_knitGraph(knit_graph, node_to_course_and_wale=node_to_course_and_wale, unmodified = False)
    rebuild_knitgraph()
    # return knit_graph

def add_hole2(knit_graph: Knit_Graph, hole_start_row:int, hole_start_wale:int, hole_height:int, hole_width:int, unmodified: bool, new_carrier: int = None):
    yarns = [*knit_graph.yarns.values()]
    #since given knit graph has only one yarn before being modified
    yarn = yarns[0]
    node_to_course_and_wale = {}
    course_and_wale_to_node = {}
    node_to_delete = []
    new_yarn_course_to_loop_ids= {}
    old_yarn_course_to_margin_loop_ids = {}
    new_yarn_course_to_margin_loop_ids = {}
    loop_ids_to_course, course_to_loop_ids, loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified=True)
    pattern_height = len(course_to_loop_ids)
    pattern_width = max([len(i) for i in [*course_to_loop_ids.values()]])
    assert hole_start_row + hole_height < pattern_height, f'hole height is too large that it is exceeding the knit graph border'
    #if taking (hole_start_row, hole_start_wale, hole_height, hole_width) as input, use below assertion
    assert hole_width <= 6, f'hole width: {hole_width} is too large to achieve the racking bound by 3 on the machine'

    #get the [course, wale] coordinate of each node in the knit graph
    def get_node_course_and_wale():
        for node in knit_graph.graph.nodes:
            # node_to_course_and_wale[node] = []
            course = loop_ids_to_course[node]
            wale = loop_ids_to_wale[node]
            node_to_course_and_wale[node] = [course, wale]
        #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
        course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
        # print('loop_ids_to_course', loop_ids_to_course)
        print('course_and_wale_to_node', course_and_wale_to_node)
        print('node_to_course_and_wale', node_to_course_and_wale)
    get_node_course_and_wale()
    print('haha', course_and_wale_to_node)
    print('lala', node_to_course_and_wale)
    #identify location of the nodes to delete
    def get_nodes_to_delete():
        locations_to_delete_node = []
        for course in range(hole_start_row, hole_start_row + hole_height):
            for wale in range(hole_start_wale, hole_start_wale + hole_width):
                locations_to_delete_node.append((course, wale))
        print('locations_to_delete_node', locations_to_delete_node)
        for location in locations_to_delete_node:
            if location not in course_and_wale_to_node.keys():
                print(f'Error: no node is found at given location {location}')
                exit()
            node = course_and_wale_to_node[location]
            node_to_delete.append(node)
        print('node_to_delete', node_to_delete)
    get_nodes_to_delete()

    def hole_location_warnings():
        #check if any node violates the constraint for a node to be part of a hole
        for node in node_to_delete:
            #first, each node should have exactly one parent. 
            #If more than one, it is part of a decrease; If less than one, it itself is an increase.
            #Likewise, each node should have exactly one child (it can only be one or zero child).
            #If no child, it might be a node on top course/top border, which we do not consider. 
            #Or simply it can be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) != 1:
                # warnings.warn("xxx")
                print(f'Warning: node {node} might break a special stitch for having {len(parent_ids)} parents')
            if len(child_ids) != 1:
                print(f'Warning: node {node} is suspicious or a node on border for for having {len(child_ids)} child')
            #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
            #If not, it is part of decrease or cable.
            parent_id = parent_ids[0]
            parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
            if parent_offset != 0:
                print(f'Warning: node {node} might break a special stitch for having parent offset of {parent_offset}')
            child_id = child_ids[0]
            child_offset = knit_graph.graph[node][child_id]["parent_offset"]
            if child_offset != 0:
                print(f'Warning: node {node} might break a special stitch for having child offset of {child_offset}')
            #Third, on yarn graph, the number of yarn edges related to the node must be 2
            #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
            yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*yarn.yarn_graph.successors(node)]
            if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                print(f'Warning: node {node} is suspicious for having no parent node or child node on yarn')
            #Fourth, on yarn graph, parent node and child node of the node should be on the same course
            #If not, it might be part of short row, or a node on the border. Currently, we do not consider add hole on border.
            parent_id = yarn_parent_ids[0]
            child_id = yarn_child_ids[0]
            if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
                print(f'Warning: node {node} might break a special stitch or a node on border for having parent node and child node that are not on the same course')
            
    def hole_location_errors():
        for node in node_to_delete:
            #First, if a node has no child and is not a node on top course/top border 
            #it would be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            course_id = node_to_course_and_wale[node][0]
            top_course_id = pattern_height - 1
            if len(child_ids) != 1 and course_id != top_course_id:
                print(f'Error: node {node} is suspicious for for having {len(child_ids)} child')
                exit()
        
        #Second, on yarn graph, the number of yarn edges related to the node must be 2
        #If less than one, and is not the start node or end node of the yarn, it would be a huge error when adding loop with the yarn
        for node in yarn.yarn_graph.nodes:
            yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*yarn.yarn_graph.successors(node)]
            if node not in [0, len(yarn.yarn_graph.nodes)-1]:
                if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                    print(f'Error: node {node} is suspicious for having no parent node or child node on yarn')
                    exit()
        
    hole_location_errors()
    hole_location_warnings()
    
    # @deprecated("Deprecated because we assume users know where she/he is going to place the hole, so instead of strictly limiting
    # the user on the place to generate a hole, more freedom is offered to the users. May be a good idea to send warning rather than
    # error")
    #check if any node violates the constraint for a node to be part of a hole
    def deprecated_hole_location_constraints():
        #check if any node violates the constraint for a node to be part of a hole
        for node in node_to_delete:
            #first, each node should have exactly one parent. 
            #If more than one, it is part of a decrease; If less than one, it itself is an increase.
            #Likewise, each node should have exactly one child (it can only be one or zero child).
            #If no child, it might be a node on top course/top border, if deleted, will cause the whole knitted item to unravel. Or simply
            #it can be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) != 1:
                print(f'Error: node {node} is not qualified for a hole for having {len(parent_ids)} parents')
                exit()
            if len(child_ids) != 1:
                print(f'Error: node {node} is not qualified for a hole for having {len(child_ids)} parents')
                exit()
            #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
            #If not, it is part of decrease or cable.
            parent_id = parent_ids[0]
            parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
            if parent_offset != 0:
                print(f'Error: node {node} is not qualified for a hole for having parent offset of {parent_offset}')
                exit()
            child_id = child_ids[0]
            child_offset = knit_graph.graph[node][child_id]["parent_offset"]
            if parent_offset != 0:
                print(f'Error: node {node} is not qualified for a hole for having child offset of {child_offset}')
                exit()
            #Third, on yarn graph, the number of yarn edges related to the node must be 2
            #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
            parent_ids = [*yarn.yarn_graph.predecessors(node)]
            child_ids = [*yarn.yarn_graph.successors(node)]
            if len(parent_ids) != 1 or len(child_ids) != 1:
                print(f'Error: node {node} is not qualified for a hole for having no parent node or child node on yarn')
                exit()
            #Fourth, on yarn graph, parent node and child node of the node should be on the same course
            #If not, it might be part of short row, or a node on the border. If node on border got deleted, 
            #will cause the whole knitted item to unravel.
            parent_id = parent_ids[0]
            child_id = child_ids[0]
            if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
                print(f'Error: node {node} is not qualified for a hole for having parent node and child node that are not on the same course')
                exit()
            #Fifth is related to margin nodes, that is, nodes that are immediately on the two side of the hole. Check 
        
    #remove the nodes for hole from both knit graph and yarn
    def remove_hole_nodes_from_graph():
        # print(f'knit graph edges before deleting the nodes is {knit_graph.graph.edges}, number of {len(knit_graph.graph.edges)}')
        knit_graph.graph.remove_nodes_from(node_to_delete)
        # print(f'knit graph edges after deleting the nodes is {knit_graph.graph.edges}, number of {len(knit_graph.graph.edges)}')
        yarn.yarn_graph.remove_nodes_from(node_to_delete)
        #And update dict: node_to_course_and_wale and dict: course_and_wale_to_node
        #remove nodes from node position dict: node_to_course_and_wale
        for node in node_to_delete:
            del node_to_course_and_wale[node]
        #remove nodes from course_and_wale_to_node with updated "node_to_course_and_wale"
        course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
        print('course_and_wale_to_node after deleting nodes', course_and_wale_to_node)
        print('node_to_course_and_wale after deleting nodes', node_to_course_and_wale)
    remove_hole_nodes_from_graph()

    def get_new_yarn_loop_ids():
        if hole_start_row % 2 == 0:
            #new yarn spread between the hole_end_wale and the last wale_id, old yarn is between the wale_id = 0 to the hole_start_wale 
            for course_id in range(hole_start_row, hole_start_row + hole_height):
                if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                    print(f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}')
                    # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}'
                else:
                    old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
                if (course_id, hole_start_wale + hole_width) not in course_and_wale_to_node.keys():
                    print(f'no node is found on the new yarn margin {(course_id, hole_start_wale + hole_width)}')
                    # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale + hole_width)}'
                else:
                    new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale + hole_width)]
                new_yarn_course_to_loop_ids[course_id] = []
                if course_id % 2 == 0:
                    for wale_id in range(hole_start_wale+hole_width, pattern_width):
                        if (course_id, wale_id) in course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
                elif course_id % 2 ==1:
                    for wale_id in range(hole_start_wale+hole_width, pattern_width):
                        if (course_id, wale_id) in course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])
            
            if hole_height % 2 == 0:
                pass
            elif hole_height % 2 == 1:
                for course_id in range(hole_start_row + hole_height, pattern_height):
                    new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
            
        if hole_start_row % 2 == 1:
            #Contrary to the above,
            #new yarn spread between the wale_id = 0 to the hole_start_wale, old yarn is between the hole_end_wale and the last wale_id
            for course_id in range(hole_start_row, hole_start_row + hole_height):
                if (course_id, hole_start_wale + hole_width) not in course_and_wale_to_node.keys():
                    print(f'no node is found on the margin {(course_id, hole_start_wale + hole_width)}')
                # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale + hole_width)}'
                else:
                    old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale + hole_width)]
                if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                    print(f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}')
                # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}'
                else:
                    new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
                new_yarn_course_to_loop_ids[course_id] = []
                if course_id % 2 == 0:
                    for wale_id in range(0, hole_start_wale):
                        if (course_id, wale_id) in course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
                elif course_id % 2 == 1:
                    for wale_id in range(0, hole_start_wale):
                        if (course_id, wale_id) in course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])
            if hole_height % 2 == 0:
                pass
            elif hole_height % 2 == 1:
                for course_id in range(hole_start_row + hole_height, pattern_height):
                    new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
        print('old_yarn_course_to_margin_loop_ids', old_yarn_course_to_margin_loop_ids)
        print('new_yarn_course_to_loop_ids', new_yarn_course_to_loop_ids)
    get_new_yarn_loop_ids()

    # reconnect old yarn at its margin
    def reconnect_old_yarn_at_margin(hole_start_row):
        if hole_start_row % 2 == 0:
            for course_id in old_yarn_course_to_margin_loop_ids: 
                if course_id%2 == 0 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                    start_node = old_yarn_course_to_margin_loop_ids[course_id]
                    next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                    yarn.yarn_graph.add_edge(start_node, next_node)
        elif hole_start_row % 2 == 1:
            for course_id in old_yarn_course_to_margin_loop_ids: 
                if course_id%2 == 1 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                    start_node = old_yarn_course_to_margin_loop_ids[course_id]
                    next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                    yarn.yarn_graph.add_edge(start_node, next_node)
    reconnect_old_yarn_at_margin(hole_start_row)

    '''
    WRONG! 
    #Fifth, nodes on the margin should have both child and parent, otherwise, when the neighbor node is deleted for 
    #a hole, (tbd it will be a isolated node, which is impossible)
    def deprecated_check_margin_nodes():
        for node in old_yarn_course_to_margin_loop_ids.values():
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) == 0 or len(child_ids) == 0:
                print(f'Error: unqualified hole location for margin node {node} on old yarn not having both child and parent')
                exit()

        for node in new_yarn_course_to_margin_loop_ids.values():
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) == 0 or len(child_ids) == 0:
                print(f'Error: unqualified hole location for margin node {node} on new yarn not having both child and parent')
                exit()
    ''' 

    # remove loop_ids from old yarn and add loop_ids to new yarn and connect them
    def remove_old_and_add_new_yarn():
        assert new_carrier != None, f'new carrier is needed to introduce new yarn'
        new_yarn = Yarn("new_yarn", knit_graph, carrier_id=new_carrier)
        knit_graph.add_yarn(new_yarn)
        for course_id in new_yarn_course_to_loop_ids:
            loop_ids = new_yarn_course_to_loop_ids[course_id]
            for loop_id in loop_ids:
                yarn.yarn_graph.remove_node(loop_id)
                child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
        print(f'old yarn edges are {yarn.yarn_graph.edges}, new yarn edges are {new_yarn.yarn_graph.edges}')
    remove_old_and_add_new_yarn()
    '''
    get_node_course_and_wale()
    get_nodes_to_delete()
    hole_location_errors()
    hole_location_warnings()
    remove_hole_nodes_from_graph()
    get_new_yarn_loop_ids()
    reconnect_old_yarn_at_margin
    remove_old_and_add_new_yarn()
    '''
    visualize_knitGraph(knit_graph, node_to_course_and_wale=node_to_course_and_wale, unmodified = False)
    # return knit_graph

def add_hole3(knit_graph: Knit_Graph, hole_start_row:int, hole_start_wale:int, hole_height:int, hole_width:int, unmodified: bool, new_carrier: int = None):
    yarns = [*knit_graph.yarns.values()]
    #since given knit graph has only one yarn before being modified
    yarn = yarns[0]
    node_to_course_and_wale = {}
    course_and_wale_to_node = {}
    node_to_delete = []
    new_yarn_course_to_loop_ids= {}
    old_yarn_course_to_margin_loop_ids = {}
    new_yarn_course_to_margin_loop_ids = {}
    loop_ids_to_course, course_to_loop_ids, loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified=True)
    pattern_height = len(course_to_loop_ids)
    pattern_width = max([len(i) for i in [*course_to_loop_ids.values()]])
    assert hole_start_row + hole_height < pattern_height, f'hole height is too large that it is exceeding the knit graph border'
    #if taking (hole_start_row, hole_start_wale, hole_height, hole_width) as input, use below assertion
    assert hole_width <= 6, f'hole width: {hole_width} is too large to achieve the racking bound by 3 on the machine'

    #get the [course, wale] coordinate of each node in the knit graph
    for node in knit_graph.graph.nodes:
        # node_to_course_and_wale[node] = []
        course = loop_ids_to_course[node]
        wale = loop_ids_to_wale[node]
        node_to_course_and_wale[node] = [course, wale]
    #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
    course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
    # print('loop_ids_to_course', loop_ids_to_course)
    print('course_and_wale_to_node', course_and_wale_to_node)
    print('node_to_course_and_wale', node_to_course_and_wale)

    #identify location of the nodes to delete
    locations_to_delete_node = []
    for course in range(hole_start_row, hole_start_row + hole_height):
        for wale in range(hole_start_wale, hole_start_wale + hole_width):
            locations_to_delete_node.append((course, wale))
    print('locations_to_delete_node', locations_to_delete_node)
    for location in locations_to_delete_node:
        if location not in course_and_wale_to_node.keys():
            print(f'Error: no node is found at given location {location}')
            exit()
        node = course_and_wale_to_node[location]
        node_to_delete.append(node)
    print('node_to_delete', node_to_delete)

    def hole_location_warnings():
        #check if any node violates the constraint for a node to be part of a hole
        for node in node_to_delete:
            #first, each node should have exactly one parent. 
            #If more than one, it is part of a decrease; If less than one, it itself is an increase.
            #Likewise, each node should have exactly one child (it can only be one or zero child).
            #If no child, it might be a node on top course/top border, which we do not consider. 
            #Or simply it can be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) != 1:
                # warnings.warn("xxx")
                print(f'Warning: node {node} might break a special stitch for having {len(parent_ids)} parents')
            if len(child_ids) != 1:
                print(f'Warning: node {node} is suspicious or a node on border for for having {len(child_ids)} child')
            #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
            #If not, it is part of decrease or cable.
            parent_id = parent_ids[0]
            parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
            if parent_offset != 0:
                print(f'Warning: node {node} might break a special stitch for having parent offset of {parent_offset}')
            child_id = child_ids[0]
            child_offset = knit_graph.graph[node][child_id]["parent_offset"]
            if parent_offset != 0:
                print(f'Warning: node {node} might break a special stitch for having child offset of {child_offset}')
            #Third, on yarn graph, the number of yarn edges related to the node must be 2
            #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
            yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*yarn.yarn_graph.successors(node)]
            if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                print(f'Warning: node {node} is suspicious for having no parent node or child node on yarn')
            #Fourth, on yarn graph, parent node and child node of the node should be on the same course
            #If not, it might be part of short row, or a node on the border. Currently, we do not consider add hole on border.
            parent_id = yarn_parent_ids[0]
            child_id = yarn_child_ids[0]
            if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
                print(f'Warning: node {node} might break a special stitch or a node on border for having parent node and child node that are not on the same course')
            
    def hole_location_errors():
        for node in node_to_delete:
            #First, if a node has no child and is not a node on top course/top border 
            #it would be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            course_id = node_to_course_and_wale[node][0]
            top_course_id = pattern_height - 1
            if len(child_ids) != 1 and course_id != top_course_id:
                print(f'Error: node {node} is suspicious for for having {len(child_ids)} child')
                exit()
        
        #Second, on yarn graph, the number of yarn edges related to the node must be 2
        #If less than one, and is not the start node or end node of the yarn, it would be a huge error when adding loop with the yarn
        for node in yarn.yarn_graph.nodes:
            yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*yarn.yarn_graph.successors(node)]
            if node not in [0, len(yarn.yarn_graph.nodes)-1]:
                if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                    print(f'Error: node {node} is suspicious for having no parent node or child node on yarn')
                    exit()
        
    hole_location_errors()
    hole_location_warnings()

    # @deprecated("Deprecated because we assume users know where she/he is going to place the hole, so instead of strictly limiting
    # the user on the place to generate a hole, more freedom is offered to the users. May be a good idea to send warning rather than
    # error")
    #check if any node violates the constraint for a node to be part of a hole
    def deprecated_hole_location_constraints():
        #check if any node violates the constraint for a node to be part of a hole
        for node in node_to_delete:
            #first, each node should have exactly one parent. 
            #If more than one, it is part of a decrease; If less than one, it itself is an increase.
            #Likewise, each node should have exactly one child (it can only be one or zero child).
            #If no child, it might be a node on top course/top border, if deleted, will cause the whole knitted item to unravel. Or simply
            #it can be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) != 1:
                print(f'Error: node {node} is not qualified for a hole for having {len(parent_ids)} parents')
                exit()
            if len(child_ids) != 1:
                print(f'Error: node {node} is not qualified for a hole for having {len(child_ids)} parents')
                exit()
            #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
            #If not, it is part of decrease or cable.
            parent_id = parent_ids[0]
            parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
            if parent_offset != 0:
                print(f'Error: node {node} is not qualified for a hole for having parent offset of {parent_offset}')
                exit()
            child_id = child_ids[0]
            child_offset = knit_graph.graph[node][child_id]["parent_offset"]
            if parent_offset != 0:
                print(f'Error: node {node} is not qualified for a hole for having child offset of {child_offset}')
                exit()
            #Third, on yarn graph, the number of yarn edges related to the node must be 2
            #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
            parent_ids = [*yarn.yarn_graph.predecessors(node)]
            child_ids = [*yarn.yarn_graph.successors(node)]
            if len(parent_ids) != 1 or len(child_ids) != 1:
                print(f'Error: node {node} is not qualified for a hole for having no parent node or child node on yarn')
                exit()
            #Fourth, on yarn graph, parent node and child node of the node should be on the same course
            #If not, it might be part of short row, or a node on the border. If node on border got deleted, 
            #will cause the whole knitted item to unravel.
            parent_id = parent_ids[0]
            child_id = child_ids[0]
            if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
                print(f'Error: node {node} is not qualified for a hole for having parent node and child node that are not on the same course')
                exit()
            #Fifth is related to margin nodes, that is, nodes that are immediately on the two side of the hole. Check 
        
    #remove the nodes for hole from both knit graph and yarn
    # print(f'knit graph edges before deleting the nodes is {knit_graph.graph.edges}, number of {len(knit_graph.graph.edges)}')
    knit_graph.graph.remove_nodes_from(node_to_delete)
    # print(f'knit graph edges after deleting the nodes is {knit_graph.graph.edges}, number of {len(knit_graph.graph.edges)}')
    yarn.yarn_graph.remove_nodes_from(node_to_delete)
    #And update dict: node_to_course_and_wale and dict: course_and_wale_to_node
    #remove nodes from node position dict: node_to_course_and_wale
    for node in node_to_delete:
        del node_to_course_and_wale[node]
    #remove nodes from course_and_wale_to_node with updated "node_to_course_and_wale"
    course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
    print('course_and_wale_to_node after deleting nodes', course_and_wale_to_node)
    print('node_to_course_and_wale after deleting nodes', node_to_course_and_wale)

    if hole_start_row % 2 == 0:
        #new yarn spread between the hole_end_wale and the last wale_id, old yarn is between the wale_id = 0 to the hole_start_wale 
        for course_id in range(hole_start_row, hole_start_row + hole_height):
            if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                print(f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}')
                # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}'
            else:
                old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
            if (course_id, hole_start_wale + hole_width) not in course_and_wale_to_node.keys():
                print(f'no node is found on the new yarn margin {(course_id, hole_start_wale + hole_width)}')
                # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale + hole_width)}'
            else:
                new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale + hole_width)]
            new_yarn_course_to_loop_ids[course_id] = []
            if course_id % 2 == 0:
                for wale_id in range(hole_start_wale+hole_width, pattern_width):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
            elif course_id % 2 ==1:
                for wale_id in range(hole_start_wale+hole_width, pattern_width):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])
        
        if hole_height % 2 == 0:
            pass
        elif hole_height % 2 == 1:
            for course_id in range(hole_start_row + hole_height, pattern_height):
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
        
    if hole_start_row % 2 == 1:
        #Contrary to the above,
        #new yarn spread between the wale_id = 0 to the hole_start_wale, old yarn is between the hole_end_wale and the last wale_id
        for course_id in range(hole_start_row, hole_start_row + hole_height):
            if (course_id, hole_start_wale + hole_width) not in course_and_wale_to_node.keys():
                print(f'no node is found on the margin {(course_id, hole_start_wale + hole_width)}')
            # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale + hole_width)}'
            else:
                old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale + hole_width)]
            if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                print(f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}')
            # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}'
            else:
                new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
            new_yarn_course_to_loop_ids[course_id] = []
            if course_id % 2 == 0:
                for wale_id in range(0, hole_start_wale):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
            elif course_id % 2 == 1:
                for wale_id in range(0, hole_start_wale):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])
        if hole_height % 2 == 0:
            pass
        elif hole_height % 2 == 1:
            for course_id in range(hole_start_row + hole_height, pattern_height):
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]
    print('old_yarn_course_to_margin_loop_ids', old_yarn_course_to_margin_loop_ids)
    print('new_yarn_course_to_loop_ids', new_yarn_course_to_loop_ids)


    # reconnect old yarn at its margin 
    if hole_start_row % 2 == 0:
        for course_id in old_yarn_course_to_margin_loop_ids: 
            if course_id%2 == 0 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                start_node = old_yarn_course_to_margin_loop_ids[course_id]
                next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                yarn.yarn_graph.add_edge(start_node, next_node)
    elif hole_start_row % 2 == 1:
        for course_id in old_yarn_course_to_margin_loop_ids: 
            if course_id%2 == 1 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                start_node = old_yarn_course_to_margin_loop_ids[course_id]
                next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                yarn.yarn_graph.add_edge(start_node, next_node)

    '''
    WRONG! 
    #Fifth, nodes on the margin should have both child and parent, otherwise, when the neighbor node is deleted for 
    #a hole, (tbd it will be a isolated node, which is impossible)
    def deprecated_check_margin_nodes():
        for node in old_yarn_course_to_margin_loop_ids.values():
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) == 0 or len(child_ids) == 0:
                print(f'Error: unqualified hole location for margin node {node} on old yarn not having both child and parent')
                exit()

        for node in new_yarn_course_to_margin_loop_ids.values():
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) == 0 or len(child_ids) == 0:
                print(f'Error: unqualified hole location for margin node {node} on new yarn not having both child and parent')
                exit()
    ''' 

    # remove loop_ids from old yarn and add loop_ids to new yarn and connect them

    assert new_carrier != None, f'new carrier is needed to introduce new yarn'
    new_yarn = Yarn("new_yarn", knit_graph, carrier_id=new_carrier)
    knit_graph.add_yarn(new_yarn)
    for course_id in new_yarn_course_to_loop_ids:
        loop_ids = new_yarn_course_to_loop_ids[course_id]
        for loop_id in loop_ids:
            yarn.yarn_graph.remove_node(loop_id)
            child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
    print(f'old yarn edges are {yarn.yarn_graph.edges}, new yarn edges are {new_yarn.yarn_graph.edges}')

    '''
    get_node_course_and_wale()
    get_nodes_to_delete()
    hole_location_errors()
    hole_location_warnings()
    remove_hole_nodes_from_graph()
    get_new_yarn_loop_ids()
    reconnect_old_yarn_at_margin
    remove_old_and_add_new_yarn()
    '''
    visualize_knitGraph(knit_graph, node_to_course_and_wale=node_to_course_and_wale, unmodified = False)
    # return knit_graph

# #this one takes node ids as input.
def add_hole4(knit_graph: Knit_Graph, node_to_delete: List[int], unmodified: bool = True, new_carrier: int = None):
    '''biggest assumption: the function currently only apply for hole that are rectagular and only one hole. More yarns are needed if 
    the above condition is not satisfied.
    '''
    yarns = [*knit_graph.yarns.values()]
    #since given knit graph has only one yarn before being modified
    yarn = yarns[0]
    node_to_delete = []
    new_yarn_course_to_loop_ids= {}
    old_yarn_course_to_margin_loop_ids = {}
    new_yarn_course_to_margin_loop_ids = {}
    loop_ids_to_course, course_to_loop_ids, loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified)
    #pattern_height is the total number of courses 
    pattern_height = len(course_to_loop_ids)
    #pattern_width is the total number of wales
    pattern_width = len(wale_to_loop_ids)
    # pattern_width = max([len(i) for i in [*course_to_loop_ids.values()]])
    
    #get the [course, wale] coordinate of each node in the knit graph
    node_to_course_and_wale = {}
    for node in knit_graph.graph.nodes:
        # node_to_course_and_wale[node] = []
        course = loop_ids_to_course[node]
        wale = loop_ids_to_wale[node]
        node_to_course_and_wale[node] = [course, wale]
    #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
    course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
    # print('loop_ids_to_course', loop_ids_to_course)
    print('course_and_wale_to_node', course_and_wale_to_node)
    print('node_to_course_and_wale', node_to_course_and_wale)

    #if taking node ids as input, use below assertion
    #number of unique wale id can not exceed 6 to make it a feasible to knit on knittimg machine taking into account racking constraint
    wale_involved = set() 
    #hole_start_course is the minimal course_id of any node in nodes_to_delete
    hole_start_course = pattern_height - 1
    #hole_end_course is the maximal course_id of any node in nodes_to_delete
    hole_end_course = 0
    #hole_start_wale is the minimal wale_id of any node in nodes_to_delete
    hole_start_wale =  pattern_width - 1
    #hole_end_wale is the maximal wale_id of any node in nodes_to_delete
    hole_end_wale = 0
    '''packed as a function later'''
    for node in node_to_delete:
        wale_id = node_to_course_and_wale[node][1]
        wale_involved.add(wale_id)
        course_id = node_to_course_and_wale[node][0]
        if course_id > hole_end_course:
            hole_end_course = course_id
        if course_id < hole_start_course:
            hole_start_course = course_id
        if wale_id < hole_start_wale:
            hole_start_wale = wale_id
        if wale_id > hole_end_wale:
            hole_end_wale = wale_id
    print(f'hole_start_course is {hole_start_course}, hole_end_course is {hole_end_course}, hole_start_wale is {hole_start_wale}, hole_end_wale is {hole_end_wale}')
    #number of unique wale id can not exceed 6 to make it a feasible to knit on knittimg machine taking into account racking constraint
    assert len(wale_involved) <= 6, f'hole width is too large to achieve the racking bound by 3 on the machine'
    assert hole_end_course < pattern_height - 1, f'hole height is too large that it is exceeding the knit graph border'
    #hole_height: the height of the hole
    hole_height = hole_end_course - hole_start_course + 1
    #hole_width
    hole_width = hole_end_wale - hole_start_wale + 1
    def hole_location_warnings():
        #check if any node violates the constraint for a node to be part of a hole
        for node in node_to_delete:
            #first, each node should have exactly one parent. 
            #If more than one, it is part of a decrease; If less than one, it itself is an increase.
            #Likewise, each node should have exactly one child (it can only be one or zero child).
            #If no child, it might be a node on top course/top border, which we do not consider. 
            #Or simply it can be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            if len(parent_ids) != 1:
                # warnings.warn("xxx")
                print(f'Warning: node {node} might break a special stitch for having {len(parent_ids)} parents')
            if len(child_ids) != 1:
                print(f'Warning: node {node} is suspicious or a node on border for for having {len(child_ids)} child')
            #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
            #If not, it is part of decrease or cable.
            parent_id = parent_ids[0]
            parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
            if parent_offset != 0:
                print(f'Warning: node {node} might break a special stitch for having parent offset of {parent_offset}')
            child_id = child_ids[0]
            child_offset = knit_graph.graph[node][child_id]["parent_offset"]
            if parent_offset != 0:
                print(f'Warning: node {node} might break a special stitch for having child offset of {child_offset}')
            #Third, on yarn graph, the number of yarn edges related to the node must be 2
            #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
            yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*yarn.yarn_graph.successors(node)]
            if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                print(f'Warning: node {node} is suspicious for having no parent node or child node on yarn')
            #Fourth, on yarn graph, parent node and child node of the node should be on the same course
            #If not, it might be part of short row, or a node on the border. Currently, we do not consider add hole on border.
            parent_id = yarn_parent_ids[0]
            child_id = yarn_child_ids[0]
            if loop_ids_to_course[parent_id] != loop_ids_to_course[child_id]:
                print(f'Warning: node {node} might break a special stitch or a node on border for having parent node and child node that are not on the same course')
            
    def hole_location_errors():
        for node in node_to_delete:
            #First, if a node has no child and is not a node on top course/top border 
            #it would be an error node in the knit graph signaling something wrong with the program.
            parent_ids = [*knit_graph.graph.predecessors(node)]
            child_ids = [*knit_graph.graph.successors(node)]
            course_id = node_to_course_and_wale[node][0]
            top_course_id = pattern_height - 1
            if len(child_ids) != 1 and course_id != top_course_id:
                print(f'Error: node {node} is suspicious for for having {len(child_ids)} child')
                exit()
        
        #Second, on yarn graph, the number of yarn edges related to the node must be 2
        #If less than one, and is not the start node or end node of the yarn, it would be a huge error when adding loop with the yarn
        for node in yarn.yarn_graph.nodes:
            yarn_parent_ids = [*yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*yarn.yarn_graph.successors(node)]
            if node not in [0, len(yarn.yarn_graph.nodes)-1]:
                if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                    print(f'Error: node {node} is suspicious for having no parent node or child node on yarn')
                    exit()
        
    hole_location_errors()
    hole_location_warnings()

    #remove the nodes for hole from both knit graph and yarn
    knit_graph.graph.remove_nodes_from(node_to_delete)
    yarn.yarn_graph.remove_nodes_from(node_to_delete)
    print('course_to_loop_ids', course_to_loop_ids)
    
    if hole_start_course % 2 == 0:
        #new yarn spread between the hole_end_wale and the last wale_id, old yarn is between the wale_id = 0 to the hole_start_wale 
        for course_id in range(hole_start_course, hole_end_course + 1):
            if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                print(f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}')
                # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}'
            else:
                old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
            if (course_id, hole_start_wale + hole_width) not in course_and_wale_to_node.keys():
                print(f'no node is found on the new yarn margin {(course_id, hole_end_wale + 1)}')
                # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_end_wale + 1)}'
            else:
                new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_end_wale + 1)]
            new_yarn_course_to_loop_ids[course_id] = []
            if course_id % 2 == 0:
                for wale_id in range(hole_end_wale + 1, pattern_width):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
            elif course_id % 2 ==1:
                for wale_id in range(hole_end_wale + 1, pattern_width):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])
        if hole_height % 2 == 0:
            pass
        elif hole_height % 2 == 1:
            for course_id in range(hole_end_course + 1, pattern_height):
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]

        # reconnect old yarn at its margin
        for course_id in old_yarn_course_to_margin_loop_ids:
            if course_id%2==0 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                start_node = old_yarn_course_to_margin_loop_ids[course_id]
                next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                yarn.yarn_graph.add_edge(start_node, next_node)

    if hole_start_course % 2 == 1:
        #Contrary to the above,
        #new yarn spread between the wale_id = 0 to the hole_start_wale, old yarn is between the hole_end_wale and the last wale_id
        for course_id in range(hole_start_course, hole_end_course + 1):
            if (course_id, hole_end_wale + 1) not in course_and_wale_to_node.keys():
                print(f'no node is found on the old yarn margin {(course_id, hole_end_wale + 1)}')
                # assert (course_id, hole_end_wale + 1) in course_and_wale_to_node.keys(), f'no node is found on old yarn the margin {(course_id, hole_end_wale + 1)}'
            else:
                old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_end_wale + 1)]
            if  (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                print(f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}')
                # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}'
            else:
                new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_end_wale + 1)]
            new_yarn_course_to_loop_ids[course_id] = []
            if course_id % 2 == 0:
                for wale_id in range(0, hole_start_wale):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
            elif course_id % 2 == 1:
                for wale_id in range(0, hole_start_wale):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])

        for course_id in range(hole_start_course, hole_end_course + 1):
            if (course_id, hole_start_wale - 1) not in course_and_wale_to_node.keys():
                print(f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}')
                # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}'
            else:
                old_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_start_wale - 1)]
            if (course_id, hole_end_wale + 1) not in course_and_wale_to_node.keys():
                print(f'no node is found on the old yarn margin {(course_id, hole_end_wale + 1)}')
                # assert (course_id, hole_start_wale + hole_width) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale + hole_width)}'
            else:
                new_yarn_course_to_margin_loop_ids[course_id] = course_and_wale_to_node[(course_id, hole_end_wale + 1)]
            new_yarn_course_to_loop_ids[course_id] = []
            if course_id % 2 == 0:
                for wale_id in range(hole_start_wale+hole_width, pattern_width):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].append(course_and_wale_to_node[(course_id, wale_id)])
            elif course_id % 2 ==1:
                for wale_id in range(hole_start_wale+hole_width, pattern_width):
                    if (course_id, wale_id) in course_and_wale_to_node.keys():
                        new_yarn_course_to_loop_ids[course_id].insert(0, course_and_wale_to_node[(course_id, wale_id)])

        if hole_height % 2 == 0:
            pass
        elif hole_height % 2 == 1:
            for course_id in range(hole_end_wale + 1, pattern_height):
                new_yarn_course_to_loop_ids[course_id] = course_to_loop_ids[course_id]

        # reconnect old yarn at its margin
        for course_id in old_yarn_course_to_margin_loop_ids:
            if course_id%2==1 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                start_node = old_yarn_course_to_margin_loop_ids[course_id]
                next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                yarn.yarn_graph.add_edge(start_node, next_node)

    print('old_yarn_course_to_margin_loop_ids', old_yarn_course_to_margin_loop_ids)
    print('new_yarn_course_to_loop_ids', new_yarn_course_to_loop_ids)
        
    # remove loop_ids from old yarn and add loop_ids to new yarn and connect them
    assert new_carrier != None, f'new carrier is needed to introduce new yarn'
    new_yarn = Yarn("new_yarn", knit_graph, carrier_id=new_carrier)
    knit_graph.add_yarn(new_yarn)
    for course_id in new_yarn_course_to_loop_ids:
        loop_ids = new_yarn_course_to_loop_ids[course_id]
        for loop_id in loop_ids:
            yarn.yarn_graph.remove_node(loop_id)
            child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
    print(f'old yarn edges are {yarn.yarn_graph.edges}, new yarn edges are {new_yarn.yarn_graph.edges}')
    return knit_graph

if __name__ == '__main__':
    # knit_graph = test_stst()
    # knit_graph = test_cable()
    # knit_graph = test_short_rows()
    knit_graph = test_lace()
    knitGraph = add_hole3(knit_graph, hole_start_row=3, hole_start_wale=1, hole_height=1, hole_width=1, unmodified = True, new_carrier = 4)
    # visualize_knitGraph(knitGraph)