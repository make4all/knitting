"""Tests that generate simple knit graph visualizations"""
from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from debugging_tools.simple_knitgraph_generator import Simple_Knitgraph_Generator
from knit_graphs.Knit_Graph import Knit_Graph
import networkx as nx

def test_stockinette():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='stockinette', width  = 8, height = 8, carrier = 3, gauge = 1)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    # KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'sheet')
    knit_graph.graph = nx.relabel_nodes(knit_graph.graph, mapping = {0:100})
    [*knit_graph.yarns.values()][0].yarn_graph  = nx.relabel_nodes([*knit_graph.yarns.values()][0].yarn_graph, mapping = {0:100})
    print(knit_graph.graph.nodes, knit_graph.graph.edges, [*knit_graph.yarns.values()][0].yarn_graph.nodes, [*knit_graph.yarns.values()][0].yarn_graph.edges)
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()

def test_rib():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='rib', width = 8, height = 8, rib_width = 4, carrier = 3, gauge = 1)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()

def test_lace():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='lace', width = 8, height = 4, carrier = 3, gauge = 1)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'sheet')
    KnitGraph_Visualizer.visualize()

# below three knitgraphs are yet to update
def test_seed():
    visualize_knitGraph(seed(4, 4))

def test_twisted_stripes():
    visualize_knitGraph(twisted_stripes(4, 5))

def test_short_rows():
    knit_graph = short_rows(5, buffer_height=1)
    _, _, _, _ = knit_graph.get_courses()
    visualize_knitGraph(knit_graph)

def test_tube():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='tube', width = 6, height = 6, carrier = 3, gauge  = 1)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'tube')
    KnitGraph_Visualizer.visualize()

def test_decrease_tube():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='decreased_tube', width = 10, carrier = 3, gauge = 0.5)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'tube')
    KnitGraph_Visualizer.visualize()
    
def test_increased_tube():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='increased_tube', bottom_height = 1, upper_height = 3, width = 2, increase_gap = 1, increase_sts = 2, carrier = 3, gauge = 1)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'tube')
    KnitGraph_Visualizer.visualize()
    # knit_graph.get_courses()

def test_arrow_shaped_hat():
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='arrow_shaped_hat', width = 10, bottom_height = 5, upper_height = 3, carrier = 3, gauge = 0.5)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'tube')
    KnitGraph_Visualizer.visualize()

def test_shirt():
    # pattern='shirt', body_width = 12, height_below_shoulder = 6, left_sleeve_width = 3, left_sleeve_height = 6, \
    #     right_sleeve_width = 3, right_sleeve_height = 6, height_above_shoulder = 6, gauge = 0.5
    simple_knitgraph_generator = Simple_Knitgraph_Generator(pattern='shirt', body_width = 6, height_below_shoulder = 5, left_sleeve_width = 2, left_sleeve_height = 2, \
        right_sleeve_width = 2, right_sleeve_height = 2, height_above_shoulder = 2, gauge = 0.5)
    knit_graph = simple_knitgraph_generator.generate_knitgraph()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, simple_knitgraph_generator.node_on_front_or_back, simple_knitgraph_generator.node_to_course_and_wale, object_type = 'tube')
    KnitGraph_Visualizer.visualize()
    
if __name__ == "__main__":
    ## Test sheet below
    test_stockinette()
    # test_rib()
    # test_lace()

    # test_seed()
    # test_twisted_stripes()
    # test_short_rows()


    ## Test tube below
    # test_tube()
    # test_decrease_tube()
    # test_increased_tube()
    # test_arrow_shaped_hat()
    # test_shirt()
