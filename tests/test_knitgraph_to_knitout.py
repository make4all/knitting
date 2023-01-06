from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from tests.test_hole_generator_mul_on_sheet import *
from tests.test_hole_generator_mul_on_tube import *
from pattern_modification.New_Mul_Hole_Generator_on_Sheet import Hole_Generator_on_Sheet
from pattern_modification.New_Mul_Hole_Generator_on_Tube import Hole_Generator_on_Tube
# from tests.test_pocket_generator import *
from debugging_tools.simple_knitgraph_generator import *
from knitting_machine.final_knitgraph_to_knitout import Knitout_Generator
from knit_graphs.Knit_Graph import Knit_Graph


def test_rib():   
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='rib', width = 8, height = 8, rib_width = 4, carrier = 3, gauge = 1)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()
    generator = Knitout_Generator(knit_graph, 'sheet', simple_knitgraph_generator.node_to_course_and_wale, simple_knitgraph_generator.course_and_wale_to_node, \
            simple_knitgraph_generator.node_on_front_or_back)
    generator.write_instructions("test_rib_new_kg2ko.k")


# def test_seed():
#     knitGraph = seed(20, 10)
#     generator = Knitout_Generator(knitGraph)
#     generator.write_instructions("test_seed.k")


def test_lace():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='lace', width = 8, height = 4, carrier = 3, gauge = 1)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()
    generator = Knitout_Generator(knit_graph, 'sheet', simple_knitgraph_generator.node_to_course_and_wale, simple_knitgraph_generator.course_and_wale_to_node, \
            simple_knitgraph_generator.node_on_front_or_back)
    generator.write_instructions("test_lace_new_kg2ko.k")

def lace_with_hole():     
    knitGraph, node_to_course_and_wale = test_lace_with_hole(yarns_and_holes_to_add = {2: [91, 92],  4: [75], 6:[191, 192]}) #[187, 188, 189, 190, 191, 192]
    generator = Knitout_Generator(knitGraph, node_to_course_and_wale, unmodified = False)
    generator.write_instructions("test_lace_hole.k")



def stst_with_hole(yarns_and_holes_to_add = {6:[28], 4:[33, 34, 35, 36, 37]}):
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = yarns_and_holes_to_add, simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='stockinette', width = 8, height = 7, carrier = 3, gauge = 1))
    knit_graph = hole_generator.add_hole()
    generator = Knitout_Generator(knit_graph, 'sheet', hole_generator.node_to_course_and_wale, hole_generator.course_and_wale_to_node, \
            hole_generator.node_on_front_or_back)
    generator.write_instructions("test_stst_hole_mul_new_kg2ko.k")

def cable_with_hole():     
    knitGraph, node_to_course_and_wale = test_cable_with_hole()
    generator = Knitout_Generator(knitGraph, node_to_course_and_wale)
    generator.write_instructions("test_cable_with_hole.k")

def rib_with_hole():     
    knitGraph, node_to_course_and_wale = test_rib_with_hole()
    generator = Knitout_Generator(knitGraph, node_to_course_and_wale)
    generator.write_instructions("test_rib_with_hole.k")

# now test for pockets
def rect_pocket():
    # knitGraph, node_to_course_and_wale = test_rectangle_pocket_on_stst(spliting_nodes = [43, 44, 45, 46, 47, 48, 49, 50, 51, 52])
    knitGraph, node_to_course_and_wale = test_rectangle_pocket_on_stst()
    generator = Knitout_Generator(knitGraph, node_to_course_and_wale)
    generator.write_instructions("test_rect_pocket.k")

def normal_tube():
    knitGraph = tube(width = 8, height = 4, carrier = 3) 
    loop_id_to_course, course_to_loop_ids, loop_id_to_wale, wale_to_loop_ids = knitGraph.get_courses(unmodified=True, gauge=0.5)
    node_to_course_and_wale = {}
    for node in knitGraph.graph.nodes:
        course = loop_id_to_course[node]
        wale = loop_id_to_wale[node]
        node_to_course_and_wale[node] = (course, wale)
    visualize_knitGraph(knitGraph, node_to_course_and_wale = node_to_course_and_wale, yarn_start_direction = 'left to right', object_type = 'tube', unmodified = True)
    generator = Knitout_Generator(knitGraph, object_type = 'tube', unmodified = True, node_to_course_and_wale = node_to_course_and_wale)
    generator.write_instructions("test_normal_tube.k")

def decreased_tube():
    knit_graph = decrease_tube(10, gauge = 0.5)
    loop_id_to_course, course_to_loop_ids, loop_id_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified=True, gauge=0.5)
    node_to_course_and_wale = {}
    for node in knit_graph.graph.nodes:
        course = loop_id_to_course[node]
        wale = loop_id_to_wale[node]
        node_to_course_and_wale[node] = (course, wale)
    visualize_knitGraph(knit_graph, node_to_course_and_wale = node_to_course_and_wale, yarn_start_direction = 'left to right', object_type = 'tube', unmodified = True)
    generator = Knitout_Generator(knit_graph, object_type = 'tube', unmodified = True, node_to_course_and_wale = node_to_course_and_wale)
    generator.write_instructions("test_decreased_tube.k")
    return knit_graph

def normal_tube_with_hole():
    knitGraph = tube(width = 8, height = 4, carrier = 3) 
    loop_id_to_course, course_to_loop_ids, loop_id_to_wale, wale_to_loop_ids = knitGraph.get_courses(unmodified=True, gauge=0.5)
    node_to_course_and_wale = {}
    for node in knitGraph.graph.nodes:
        course = loop_id_to_course[node]
        wale = loop_id_to_wale[node]
        node_to_course_and_wale[node] = (course, wale)
    visualize_knitGraph(knitGraph, node_to_course_and_wale = node_to_course_and_wale, yarn_start_direction = 'left to right', object_type = 'tube', unmodified = True)
    generator = Knitout_Generator(knitGraph, object_type = 'tube', unmodified = True, node_to_course_and_wale = node_to_course_and_wale)
    generator.write_instructions("test_normal_tube.k")

def decreased_tube_with_hole():
    knit_graph = decrease_tube(10, gauge = 0.5)
    # knit_graph = decrease_tube(20, gauge = 0.5)
    loop_id_to_course, course_to_loop_ids, loop_id_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified=True, gauge=0.5)
    node_to_course_and_wale = {}
    for node in knit_graph.graph.nodes:
        course = loop_id_to_course[node]
        wale = loop_id_to_wale[node]
        node_to_course_and_wale[node] = (course, wale)
    visualize_knitGraph(knit_graph, node_to_course_and_wale = node_to_course_and_wale, yarn_start_direction = 'left to right', object_type = 'tube', unmodified = True)
    # node_to_delete = [140, 141, 142, 143]
    hole_generator = Hole_Generator(knit_graph, object_type = 'tube', node_to_delete = [49, 50], new_carrier = 4, unmodified = True, gauge = 0.5)
    knit_graph = hole_generator.add_hole()
    generator = Knitout_Generator(knit_graph, object_type = 'tube', unmodified = False, node_to_course_and_wale = node_to_course_and_wale)
    generator.write_instructions("test_decreased_tube_wi_ho.k")
    return knit_graph

def test_arrow_shaped_hat():
    knit_graph = arrow_shaped_hat(width = 10, bottom_height = 5, upper_height = 3, carrier = 3, gauge = 0.5)
    visualize_knitGraph(knit_graph, object_type = 'tube')
    loop_id_to_course, course_to_loop_ids, loop_id_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified=True, gauge=0.5)
    node_to_course_and_wale = {}
    for node in knit_graph.graph.nodes:
        course = loop_id_to_course[node]
        wale = loop_id_to_wale[node]
        node_to_course_and_wale[node] = (course, wale)
    generator = Knitout_Generator(knit_graph, object_type = 'tube', unmodified = True, node_to_course_and_wale = node_to_course_and_wale)
    generator.write_instructions("test_arrow_hat.k")
    return knit_graph

def test_arrow_shaped_hat_with_hole():
    knit_graph = arrow_shaped_hat(width = 10, bottom_height = 5, upper_height = 3, carrier = 3, gauge = 0.5)
    visualize_knitGraph(knit_graph, object_type = 'tube')
    loop_id_to_course, course_to_loop_ids, loop_id_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified=True, gauge=0.5)
    node_to_course_and_wale = {}
    for node in knit_graph.graph.nodes:
        course = loop_id_to_course[node]
        wale = loop_id_to_wale[node]
        node_to_course_and_wale[node] = (course, wale)
    hole_generator = Hole_Generator(knit_graph, object_type = 'tube', node_to_delete = [80, 89, 99, 90], new_carrier = 4, unmodified = True, gauge = 0.5)
    knit_graph = hole_generator.add_hole()
    generator = Knitout_Generator(knit_graph, object_type = 'tube', unmodified = False, node_to_course_and_wale = node_to_course_and_wale)
    generator.write_instructions("test_arr_hat_wi_ho.k")
    return knit_graph

if __name__ == "__main__":
    # test_stockinette()
    # test_rib()
    # test_seed()
    # test_twisted_stripes()
    # test_lace()
    # test_short_rows()
    # test_hole_by_short_row()
    # packed
    # lace_with_hole()
    stst_with_hole()
    # cable_with_hole()
    # rib_with_hole()
    # rect_pocket()
    # normal_tube()
    #  decreased_tube()
    # decreased_tube_with_hole()
    # test_arrow_shaped_hat()
    # test_arrow_shaped_hat_with_hole()