from pattern_modification.New_Mul_Hole_Generator_on_Tube import Hole_Generator_on_Tube
# from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from debugging_tools.polygon_generator import Polygon_Generator
from debugging_tools.simple_knitgraph_generator import Simple_Knitgraph_Generator


# test hole on tube: non-decreased tube
# 2: [25, 26,  38], 4: [40, 28], 6:[51]
# 2: [26, 38], 4: [28], 6:[40]
def test_non_decrease_tube_with_hole(hole_index_to_holes = {2: [24,25,35,34,33]}):
    hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = hole_index_to_holes, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='tube', width = 6, height = 6, carrier = 3, gauge  = 1))
    knitGraph = hole_generator.add_hole()
    return knitGraph

def test_decrease_tube_with_hole(hole_index_to_holes = {2: [39, 40]}):
    hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = hole_index_to_holes, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='decreased_tube', width = 10, carrier = 3, gauge  = 0.5))
    knitGraph = hole_generator.add_hole()
    return knitGraph

# {2: [62, 63]} nodes on front bed
# {2: [68, 69]} nodes on back bed
# {2: [109, 110]} 
# {2: [37, 40]} two hole
def test_shirt_with_hole(hole_index_to_holes = {2: [62, 63]}):
    hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = hole_index_to_holes, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='shirt', body_width = 6, height_below_shoulder = 6, left_sleeve_width = 2, left_sleeve_height = 2, \
        right_sleeve_width = 2, right_sleeve_height = 2, height_above_shoulder = 2, gauge = 0.5))
    knitGraph = hole_generator.add_hole()
    return knitGraph

def test_shirt():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='shirt', body_width = 40, height_below_shoulder = 6, left_sleeve_width = 8, left_sleeve_height = 8, \
        right_sleeve_width = 8, right_sleeve_height = 8, height_above_shoulder = 10, gauge = 0.5)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'tube')
    KnitGraph_Visualizer.visualize()

if __name__ == '__main__':
    # test_non_decrease_tube_with_hole()
    test_decrease_tube_with_hole()
    # test_shirt_with_hole()
    # test_shirt()
