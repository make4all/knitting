from pattern_modification.New_Mul_Hole_Generator import Hole_Generator
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from debugging_tools.polygon_generator import Polygon_Generator
from debugging_tools.simple_knitgraph_generator import Simple_Knitgraph_Generator

# below are built-in knitgraph from either "simple_knitgraph" or "knitspeak_compiler"
def test_short_rows():
    knit_graph = short_rows(12, buffer_height=1)
    visualize_knitGraph(knit_graph)
    return knit_graph

# below are for creating hole on rectangular shaped patterns 
# yarns_and_holes_to_add = {4:[29], 6:[11, 12, 19, 20]}
# {4:[19, 20, 28, 27], 2:[42, 37]}
# {2: [29, 17, 18, 19],  4: [36, 37], 6:[45]}
# {2: [29],  4: [35], 6:[27]} the one that tells us how to optimize code to stabilize unstable node. refer to slide pp. 203
def test_stst_with_hole(yarns_and_holes_to_add = {2: [29],  4: [35], 6:[27]}):
    hole_generator = Hole_Generator(yarns_and_holes_to_add = yarns_and_holes_to_add, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='stockinette', width = 8, height = 7, carrier = 3, gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

def test_lace_with_hole(yarns_and_holes_to_add = {4:[19, 20, 28, 27]}):
    hole_generator = Hole_Generator(yarns_and_holes_to_add = yarns_and_holes_to_add, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='lace', width = 8, height = 7, carrier = 3, gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

def test_rib_with_hole(yarns_and_holes_to_add = {4: [27, 36]}):
    hole_generator = Hole_Generator(yarns_and_holes_to_add = yarns_and_holes_to_add, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='rib', width = 8, height = 8, rib_width = 4, carrier = 3, gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

# below are for adding hole to polygon-shaped patterns
# test polygon1: triangle
def test_triangle_with_hole(yarns_and_holes_to_add = {2:  [10, 11, 12, 20, 21, 22]}):
    hole_generator = Hole_Generator(yarns_and_holes_to_add = yarns_and_holes_to_add, polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (6, -6)], right_keynodes_child_fabric = [(0, 0), (6, 6)], gauge = 0.5))
    knitGraph = hole_generator.add_hole()
    return knitGraph

# test polygon2: zipper jacket pocket shaped hexagon (irregular hexagon)
def test_hexagon_with_hole(yarns_and_holes_to_add = {2: [24, 25, 19, 18]}):
    hole_generator = Hole_Generator(yarns_and_holes_to_add = yarns_and_holes_to_add, polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)], gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

#test polygon3: rectangle
def test_rectangle_with_hole(node_to_delete = [24, 25]):
    polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 6), (9, 6)])
    knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    hole_generator = Hole_Generator(knit_graph, node_to_delete = node_to_delete, new_carrier = 4, starting_nodes_coor = polygon_generator.starting_nodes_coor, ending_nodes_coor = polygon_generator.ending_nodes_coor, course_to_loop_ids = polygon_generator.course_to_loop_ids, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, course_and_wale_to_node = polygon_generator.course_and_wale_to_node, is_polygon = True, unmodified = True)
    knitGraph_with_hole = hole_generator.add_hole(object_type = "sheet")
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph_with_hole, node_to_course_and_wale

# test hole on tube: non-decreased tube
def test_non_decrease_tube_with_hole(yarns_and_holes_to_add = {2: [25, 26,  38], 4: [40, 28], 6:[51]} ):
    knit_graph = test_non_decreased_tube()
    hole_generator = Hole_Generator(knit_graph, yarns_and_holes_to_add = yarns_and_holes_to_add, unmodified = True,gauge = 0.5, object_type = 'tube')
    knitGraph = hole_generator.add_hole()
    node_to_course_and_wale = hole_generator.node_to_course_and_wale
    return knitGraph, node_to_course_and_wale


if __name__ == '__main__':
    # rectangular shape
    # knitGraph, node_to_course_and_wale = test_lace_with_hole()
    # 2
    # knitGraph, node_to_course_and_wale = test_rib_with_hole()
    # 3
    # knitGraph, node_to_course_and_wale = test_stst_with_hole()
    # polygon: triangle
    # test_triangle_with_hole()
    # 6 polygon: irregular hexagon (zipper jacket pocket)
    test_hexagon_with_hole()
    # 7 polygon: rectangle
    # test_rectangle_with_hole()

    # 8 on tube
    # test_non_decrease_tube_with_hole()


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
