from pattern_modification.New_Hole_Generator_Path_Search import Hole_Generator
from debugging_tools.new_knit_graph_viz import visualize_knitGraph
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.new_simple_knitgraphs import *
from debugging_tools.polygon_knitgraphs import *

def test_short_rows():
    knit_graph = short_rows(12, buffer_height=1)
    visualize_knitGraph(knit_graph)
    return knit_graph

def test_lace():
    knit_graph = lace(8, 8)
    visualize_knitGraph(knit_graph)
    return knit_graph

def test_tube():
    knit_graph = tube(6, 6)
    visualize_knitGraph(knit_graph, object_type = 'tube')
    return knit_graph

def test_decrease_tube():
    knit_graph = decrease_tube(10)
    visualize_knitGraph(knit_graph, object_type = 'tube')
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
    knit_graph = compiler.compile(3, 3, pattern)
    visualize_knitGraph(knit_graph)
    return knit_graph

def test_stockinette():
    knit_graph = stockinette(8, 7)
    visualize_knitGraph(stockinette(8, 7)) 
    return knit_graph

if __name__ == '__main__':
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

    #test tube 1
    # knit_graph = test_tube()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [15, 16, 27, 28], new_carrier = 4, unmodified = True)

    #test tube 2
    # knit_graph = test_tube()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [27, 28], new_carrier = 4, unmodified = True)
    
    # test tube 3
    # knit_graph = test_tube()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [15, 16, 27, 28, 39, 40], new_carrier = 4, unmodified = True)
    # knitGraph = hole_generator.add_hole(object_type = 'tube')

    # test decrease tube 1
    # knit_graph = test_decrease_tube()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [13, 14], new_carrier = 4, unmodified = True)
    # knitGraph = hole_generator.add_hole(object_type = 'tube')

    # test decrease tube 2 (the one used to test suggested solution on pp.153 on knitgraph slide)
    # knit_graph = test_decrease_tube()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [39], new_carrier = 4, unmodified = True)
    # knitGraph = hole_generator.add_hole(object_type = 'tube')

    # test decrease tube 3
    # knit_graph = test_decrease_tube()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [39, 40], new_carrier = 4, unmodified = True)
    # knitGraph = hole_generator.add_hole(object_type = 'tube')

    #test sheet 1
    # knit_graph = test_lace()
    # hole_generator = Hole_Generator(knit_graph, node_to_delete = [26, 27, 28, 29], new_carrier = 4, unmodified = True)
    # knitGraph = hole_generator.add_hole(object_type = 'sheet')
    
    # test sheet 2:diamond hole
    knit_graph = test_stockinette()
    # node_to_delete = [28, 29, 34, 35]
    # # node_to_delete = [18, 19]
    # # node_to_delete = [18, 19, 28, 29]
    # # node_to_delete = [28, 29, 34, 35, 44, 45]
    # [18, 19, 20, 21] like a slip

    # below are hole of non-rectangular shapes
    node_to_delete = [19, 27, 28, 29, 35] #  diamond hole
    # node_to_delete = [19, 20, 21, 25, 26, 27, 28, 29, 35, 36, 37] # hexagonal hole
    # node_to_delete = [19, 20, 26, 27] # Parallelogram hole
    # node_to_delete = [11, 19, 20, 21, 25, 26, 27, 28, 29, 35, 36, 37] #heart-shaped hole
    hole_generator = Hole_Generator(knit_graph, node_to_delete = [11, 19, 20, 21, 25, 26, 27, 28, 29, 35, 36, 37], new_carrier = 4, unmodified = True)
    #Finally, invoke add_hole to create a hole on the given knitgraph
    knitGraph = hole_generator.add_hole(object_type = 'sheet')

  
