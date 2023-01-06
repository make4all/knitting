from pattern_modification.New_Mul_Hole_Generator_on_Sheet_KS import Hole_Generator_on_Sheet
# from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from debugging_tools.polygon_generator import Polygon_Generator
from debugging_tools.simple_knitgraph_generator import Simple_Knitgraph_Generator

# below are for creating hole on rectangular shaped patterns 
# yarns_and_holes_to_add = {4:[29], 6:[20, 21, 22]}
# {4:[19, 20, 28, 27], 2:[42, 37]}
# {2: [29, 17, 18, 19],  4: [36, 37], 6:[45]}
# {2: [45], 4: [36, 37], 6:[11, 12, 19, 20]} bind-off would fail in this case because a hole_start_course is 2.
# {2: [29], 4: [35], 6:[27]} the one that tells us how to optimize code to stabilize unstable node. refer to slide pp. 203
# {2: [20, 26, 27, 28, 34, 35, 36, 37, 38, 42, 44]} a heart-shaped hole
# yarns_and_holes_to_add = {6:[29], 4:[20, 21, 22]}
def test_stst_with_hole(yarns_and_holes_to_add = {6:[28], 4:[33, 34, 35, 36, 37]}):
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = yarns_and_holes_to_add, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='stockinette', width = 8, height = 7, carrier = 3, gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

def test_lace_with_hole(yarns_and_holes_to_add = {4:[19, 20, 28, 27]}):
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = yarns_and_holes_to_add, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='lace', width = 8, height = 7, carrier = 3, gauge = 1))
    knitGraph = hole_generator.add_hole()
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()
    return knitGraph

def test_rib_with_hole(yarns_and_holes_to_add = {4: [27, 36]}):
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = yarns_and_holes_to_add, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='rib', width = 8, height = 8, rib_width = 4, carrier = 3, gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

# below are for adding hole to polygon-shaped patterns
# test polygon1: triangle
def test_triangle_with_hole(yarns_and_holes_to_add = {2:  [10, 11, 12, 20, 21, 22]}):
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = yarns_and_holes_to_add, polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (6, -6)], right_keynodes_child_fabric = [(0, 0), (6, 6)], gauge = 0.5))
    knitGraph = hole_generator.add_hole()
    return knitGraph

# test polygon2: zipper jacket pocket shaped hexagon (irregular hexagon)
def test_hexagon_with_hole(yarns_and_holes_to_add = {2: [24, 25, 19, 18]}):
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = yarns_and_holes_to_add, polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)], gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

#test polygon3: rectangle
def test_rectangle_with_hole(yarns_and_holes_to_add = {2: [24, 25]}):
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = yarns_and_holes_to_add, polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 6), (9, 6)], gauge = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

if __name__ == '__main__':
    # on rectangular shape
    # 1
    test_lace_with_hole()
    # 2
    # test_rib_with_hole()
    # 3
    # test_stst_with_hole()
    # on polygon 
    # 1 polygon: triangle
    # test_triangle_with_hole()
    # 2 polygon: irregular hexagon (zipper jacket pocket)
    # test_hexagon_with_hole()
    # 3 polygon: rectangle
    # test_rectangle_with_hole()

