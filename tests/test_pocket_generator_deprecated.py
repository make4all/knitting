from pattern_modification.Deprecated_New_Pocket_Generator import Pocket_Generator
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
    #below pockets are generated using the deprecated set of functions
    #1 use polygon
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)])
    # parent_knitgraph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # generator = Pocket_Generator(parent_knitgraph, old_carrier_id=3, new_carrier_id=4, left_keynodes_child_fabric=[(4, 2), (6, 2)], right_keynodes_child_fabric=[(4, 4), (6, 4)], spliting_nodes = [19, 17, 18], parent_graph_course_to_loop_ids = polygon_generator.course_to_loop_ids, parent_graph_node_to_course_and_wale = polygon_generator.node_to_course_and_wale, parent_graph_course_and_wale_to_node = polygon_generator.course_and_wale_to_node, parent_graph_is_polygon= True, unmodified = True, child_graph_is_polygon = True)
    # generator.deprecated_build_pocket_graph(close_top=False, smaller_wale_edge_connected=True, bigger_wale_edge_connected = True)
    
    #2 use polygon
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)])
    # parent_knitgraph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # generator = Pocket_Generator(parent_knitgraph, old_carrier_id=3, new_carrier_id=4, left_keynodes_child_fabric=[(4, 3), (6, 3)], right_keynodes_child_fabric=[(4, 4), (6, 4)], spliting_nodes = [17, 18], parent_graph_course_to_loop_ids = polygon_generator.course_to_loop_ids, parent_graph_node_to_course_and_wale = polygon_generator.node_to_course_and_wale, parent_graph_course_and_wale_to_node = polygon_generator.course_and_wale_to_node, parent_graph_is_polygon= True, unmodified = True, child_graph_is_polygon = True)
    # generator.deprecated_build_pocket_graph(close_top=False, smaller_wale_edge_connected=True, bigger_wale_edge_connected = True)
    
    # 3 use predefined knit pattern
    parent_knitgraph = test_lace()
    generator = Pocket_Generator(parent_knitgraph, old_carrier_id=3, new_carrier_id=4, left_keynodes_child_fabric=[(3, 3), (6, 3)], right_keynodes_child_fabric=[(3, 4), (6, 4)], spliting_nodes = [19, 20], parent_graph_is_polygon= False, unmodified = True, child_graph_is_polygon = True)
    generator.deprecated_build_pocket_graph(close_top=False, smaller_wale_edge_connected = True, bigger_wale_edge_connected = True)
    
    #4 use polygon
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 9), (9, 9)])
    # parent_knitgraph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # generator = Pocket_Generator(parent_knitgraph, old_carrier_id=3, new_carrier_id=4, left_keynodes_child_fabric=[(4, 3), (6, 1)], right_keynodes_child_fabric=[(4, 5), (6, 7)], spliting_nodes = [36, 35, 34], parent_graph_course_to_loop_ids = polygon_generator.course_to_loop_ids, parent_graph_node_to_course_and_wale = polygon_generator.node_to_course_and_wale, parent_graph_course_and_wale_to_node = polygon_generator.course_and_wale_to_node, parent_graph_is_polygon= True, unmodified = True, child_graph_is_polygon = True)
    # generator.deprecated_build_pocket_graph(close_top=True, smaller_wale_edge_connected=True, bigger_wale_edge_connected = True)
    
    #5 use polygon: zipper jacket pocket but no control over each edge connection, still only left edge and right edge
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (15, 0)], right_keynodes_child_fabric = [(0, 15), (15, 15)])
    # parent_knitgraph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # generator = Pocket_Generator(parent_knitgraph, old_carrier_id=3, new_carrier_id=4, left_keynodes_child_fabric = [(3, 2), (12, 2)], right_keynodes_child_fabric = [(3, 5), (6, 8), (9, 8), (12, 5)], spliting_nodes = [37, 36, 35, 34], parent_graph_course_to_loop_ids = polygon_generator.course_to_loop_ids, parent_graph_node_to_course_and_wale = polygon_generator.node_to_course_and_wale, parent_graph_course_and_wale_to_node = polygon_generator.course_and_wale_to_node, parent_graph_is_polygon= True, unmodified = True, child_graph_is_polygon = True)
    # generator.deprecated_build_pocket_graph(close_top=True, smaller_wale_edge_connected=True, bigger_wale_edge_connected = True)

  
