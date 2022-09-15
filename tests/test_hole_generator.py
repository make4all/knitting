# from pattern_modification.New_Hole_Generator import Hole_Generator
from pattern_modification.New_Hole_Generator_Path_Search import Hole_Generator
from debugging_tools.new_knit_graph_viz import visualize_knitGraph
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.new_simple_knitgraphs import *
from debugging_tools.polygon_knitgraphs import *

# below are built-in knitgraph from either "simple_knitgraph" or "knitspeak_compiler"
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

def test_rib():
    knit_graph = rib(8, 9, 1)
    visualize_knitGraph(rib(8, 9, 1))
    return knit_graph

def test_stst():
    pattern = "all rs rows k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 5, pattern)
    visualize_knitGraph(knit_graph)
    return knit_graph

# below are for creating hole on rectangular shaped patterns
def test_stst_with_hole(node_to_delete = [6]):
    knit_graph = test_stst()
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete, new_carrier = 4, unmodified = True)
    knitGraph = hole_generator.add_hole(object_type = "sheet")
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph, node_to_course_and_wale

def test_lace_with_hole(node_to_delete = [19, 20, 28, 27]):
    knit_graph = test_lace()
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete , new_carrier = 4, unmodified = True)
    knitGraph = hole_generator.add_hole()
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph, node_to_course_and_wale

def test_cable_with_hole(node_to_delete = [26, 39]):
    knit_graph = test_cable()
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete, new_carrier = 4, unmodified = True)
    # knitGraph = hole_generator.add_hole()
    # below is for New_Hole_Generator_Path_Search 
    knitGraph = hole_generator.add_hole(object_type = "sheet")
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph, node_to_course_and_wale

def test_rib_with_hole(node_to_delete = [27, 36]):
    knit_graph = test_rib()
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete, new_carrier = 4, unmodified = True)
    # knitGraph = hole_generator.add_hole()
    # below is for New_Hole_Generator_Path_Search 
    knitGraph = hole_generator.add_hole(object_type = "sheet")
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph, node_to_course_and_wale

# below are for adding hole to polygon-shaped patterns
# test polygon1: triangle
def test_triangle_with_hole(node_to_delete = [10, 11, 12, 20, 21, 22]):
    polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (6, -6)], right_keynodes_child_fabric = [(0, 0), (6, 6)])
    knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete, new_carrier = 4, starting_nodes_coor = polygon_generator.starting_nodes_coor, ending_nodes_coor = polygon_generator.ending_nodes_coor, course_to_loop_ids = polygon_generator.course_to_loop_ids, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, course_and_wale_to_node = polygon_generator.course_and_wale_to_node, is_polygon = True, unmodified = True)
    knitGraph_with_hole = hole_generator.add_hole(object_type = "sheet")
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph_with_hole, node_to_course_and_wale

# test polygon2: zipper jacket pocket shaped hexagon (irregular hexagon)
def test_hexagon_with_hole(node_to_delete = [24, 25, 19, 18]):
    polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)])
    knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete, new_carrier = 4, starting_nodes_coor = polygon_generator.starting_nodes_coor, ending_nodes_coor = polygon_generator.ending_nodes_coor, course_to_loop_ids = polygon_generator.course_to_loop_ids, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, course_and_wale_to_node = polygon_generator.course_and_wale_to_node, is_polygon = True, unmodified = True)
    knitGraph_with_hole = hole_generator.add_hole(object_type = "sheet")
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph_with_hole, node_to_course_and_wale

#test polygon3: rectangle
def test_hexagon_with_hole(node_to_delete = [24, 25]):
    polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 6), (9, 6)])
    knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete, new_carrier = 4, starting_nodes_coor = polygon_generator.starting_nodes_coor, ending_nodes_coor = polygon_generator.ending_nodes_coor, course_to_loop_ids = polygon_generator.course_to_loop_ids, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, course_and_wale_to_node = polygon_generator.course_and_wale_to_node, is_polygon = True, unmodified = True)
    knitGraph_with_hole = hole_generator.add_hole(object_type = "sheet")
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph_with_hole, node_to_course_and_wale

if __name__ == '__main__':
    # 1
    # knitGraph, node_to_course_and_wale = test_lace_with_hole()
    # 2
    # knitGraph, node_to_course_and_wale = test_cable_with_hole()
    # 3
    knitGraph, node_to_course_and_wale = test_rib_with_hole()
    # 4
    # knitGraph, node_to_course_and_wale = test_stst_with_hole(node_to_delete=[12])
    # 5 polygon: triangle
    # test_triangle_with_hole()
    # 6 polygon: irregular hexagon (zipper jacket pocket)
    # test_hexagon_with_hole()
    # 7 polygon: rectangle
    # test_hexagon_with_hole()

    # below hole creation flow are archived, packed into test_xx_with_hole() above already
    #test pattern 1
    # knit_graph = test_stst()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [17, 18, 19], new_carrier = 4, unmodified = True)
   
    #test pattern 2
    # knit_graph = test_cable()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [26, 39], new_carrier = 4, unmodified = True)
    
    #test pattern 3
    # knit_graph = test_short_rows()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [24, 25, 26, 27], new_carrier = 4, unmodified = True)
    
    #test pattern 4
    # knit_graph = test_lace()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [22, 23, 25, 24], new_carrier = 4, unmodified = True)
    
    #test polygon1: triangle
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (6, -6)], right_keynodes_child_fabric = [(0, 0), (6, 6)])
    # knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [10, 11, 12, 20, 21, 22], new_carrier = 4, starting_nodes_coor = polygon_generator.starting_nodes_coor, ending_nodes_coor = polygon_generator.ending_nodes_coor, course_to_loop_ids = polygon_generator.course_to_loop_ids, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, course_and_wale_to_node = polygon_generator.course_and_wale_to_node, is_polygon = True, unmodified = True)
    
    # test polygon2: zipper jacket pocket
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)])
    # knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [24, 25, 19, 18], new_carrier = 4, starting_nodes_coor = polygon_generator.starting_nodes_coor, ending_nodes_coor = polygon_generator.ending_nodes_coor, course_to_loop_ids = polygon_generator.course_to_loop_ids, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, course_and_wale_to_node = polygon_generator.course_and_wale_to_node, is_polygon = True, unmodified = True)
    
    #test polygon3: rectangle
    # polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 6), (9, 6)])
    # knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [24, 25, 19, 18], new_carrier = 4, starting_nodes_coor = polygon_generator.starting_nodes_coor, ending_nodes_coor = polygon_generator.ending_nodes_coor, course_to_loop_ids = polygon_generator.course_to_loop_ids, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, course_and_wale_to_node = polygon_generator.course_and_wale_to_node, is_polygon = True, unmodified = True)

    #Finally, invoke add_hole to create a hole on the given knitgraph
    # knitGraph = hole_generator.add_hole()
