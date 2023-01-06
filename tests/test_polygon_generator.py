from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from debugging_tools.polygon_generator import *

# test polygon1: triangle
def test_triangle():
    polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (6, -6)], right_keynodes_child_fabric = [(0, 0), (6, 6)], gauge = 0.5)
    knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, node_on_front_or_back = polygon_generator.node_on_front_or_back, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()
    

# test polygon2: zipper jacket pocket shaped hexagon (irregular hexagon)
def test_hexagon():
    polygon_generator = Polygon_Generator(left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)], gauge = 0.5)
    knit_graph = polygon_generator.generate_polygon_from_keynodes(yarn_id = 'yarn', carrier_id = 3)
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, node_on_front_or_back = polygon_generator.node_on_front_or_back, node_to_course_and_wale = polygon_generator.node_to_course_and_wale, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()



if __name__ == '__main__':

    # 1 polygon: triangle
    # test_triangle()
    # 2 polygon: irregular hexagon (zipper jacket pocket)
    test_hexagon()
   

