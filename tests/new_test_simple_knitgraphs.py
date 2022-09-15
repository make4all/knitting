"""Tests that generate simple knit graph visualizations"""
from debugging_tools.new_knit_graph_viz import visualize_knitGraph
from debugging_tools.new_simple_knitgraphs import *

def test_stockinette():
    visualize_knitGraph(stockinette(8, 7)) 


def test_rib():
    visualize_knitGraph(rib(4, 4, 1))


def test_seed():
    visualize_knitGraph(seed(4, 4))

def test_twisted_stripes():
    visualize_knitGraph(twisted_stripes(4, 5))

def test_hole_by_short_row():
    # visualize_knitGraph(hole_by_short_row(hole_position = [3, 1], hole_width = 2, hole_height = 2, width = 5, height= 6))
    # visualize_knitGraph(hole_by_short_row(hole_position = [2, 2], hole_width = 1, hole_height = 2, width = 4, height= 5)) 
    visualize_knitGraph(hole_by_short_row(hole_position = [3, 2], hole_width = 2, hole_height = 2, width = 7, height= 6)) 

def test_test_parentsoffset():
    visualize_knitGraph(test_parentsoffset(4, 2))

def test_tube():
    visualize_knitGraph(tube(6, 6), object_type = 'tube')

def test_decrease_tube():
    visualize_knitGraph(decrease_tube(6), object_type = 'tube')

def test_lace():
    visualize_knitGraph(lace(4, 4))

def test_short_rows():
    knit_graph = short_rows(5, buffer_height=1)
    _, _, _, _ = knit_graph.get_courses()
    visualize_knitGraph(knit_graph)


if __name__ == "__main__":
    # test_stockinette()
    # test_rib()
    # test_seed()
    # test_twisted_stripes()
    # test_lace()
    # test_short_rows()
    # test_hole_by_short_row()
    test_tube()
    # test_decrease_tube()
    # test_add_hole_on_tube()