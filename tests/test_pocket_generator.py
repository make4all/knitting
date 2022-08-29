from pattern_modification.New_Pocket_Generator import Pocket_Generator
from debugging_tools.knit_graph_viz import visualize_knitGraph
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.simple_knitgraphs import *
from debugging_tools.polygon_knitgraphs import *

def test_short_rows():
    knit_graph = short_rows(12, buffer_height=1)
    visualize_knitGraph(knit_graph)
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
    visualize_knitGraph(knit_graph)
    return knit_graph
    
def test_stst():
    pattern = "all rs rows k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(8, 6, pattern)
    visualize_knitGraph(knit_graph)
    return knit_graph

if __name__ == '__main__':
    #below pockets are generated using the newly set of rewritten functions rather than deprecated functions
    #1 zipper jacket pocket with control over each edge connection
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (10, 0)], right_keynodes_child_fabric = [(0, 10), (10, 10)])
    # parent_knitgraph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # generator = Pocket_Generator(parent_knitgraph, old_carrier_id=3, new_carrier_id=4, left_keynodes_child_fabric = [(3, 2), (9, 2)], right_keynodes_child_fabric = [(3, 5), (5, 7), (7, 7), (9, 5)], spliting_nodes = [24, 25, 26, 27], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True, False, False], parent_graph_course_to_loop_ids = polygon_generator.course_to_loop_ids, parent_graph_node_to_course_and_wale = polygon_generator.node_to_course_and_wale, parent_graph_course_and_wale_to_node = polygon_generator.course_and_wale_to_node, parent_graph_is_polygon= True, unmodified = True, child_graph_is_polygon = True)
    # generator.build_pocket_graph()
    #2 heart
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (2, -2), (3, -1)], right_keynodes_child_fabric = [(0, 0), (2, 2), (3, 1)])
    # parent_knitgraph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    #3
    parent_knitgraph = test_lace()
    generator = Pocket_Generator(parent_knitgraph, old_carrier_id=3, new_carrier_id=4, left_keynodes_child_fabric=[(3, 3), (6, 3)], right_keynodes_child_fabric=[(3, 4), (6, 4)], spliting_nodes = [19, 20], close_top=False, edge_connection_left_side = [False], edge_connection_right_side = [True], parent_graph_is_polygon= False, unmodified = True, child_graph_is_polygon = True)
    generator.build_pocket_graph()
  
