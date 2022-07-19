"""Tests that generate simple knit graph visualizations"""
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *

def test_round_stockinette1():
    visualize_knitGraph(round_stockinette1(4, 2)) 

def test_round_stockinette2():
    visualize_knitGraph(round_stockinette2(4, 2)) 

def test_stockinette():
    visualize_knitGraph(stockinette(4, 4)) 


def test_rib():
    visualize_knitGraph(rib(4, 4, 1))


def test_seed():
    visualize_knitGraph(seed(4, 4))


def test_twisted_stripes():
    visualize_knitGraph(twisted_stripes(4, 5))

def test_hole():
    visualize_knitGraph(stockinette_with_hole(hole_position=[2, 2], hole_width=1, width = 6, height=5))

def test_hole_by_short_row():
    # visualize_knitGraph(hole_by_short_row(hole_position = [3, 1], hole_width = 2, hole_height = 2, width = 5, height= 6))
    # visualize_knitGraph(hole_by_short_row(hole_position = [2, 2], hole_width = 1, hole_height = 2, width = 4, height= 5)) 
    visualize_knitGraph(hole_by_short_row(hole_position = [3, 2], hole_width = 2, hole_height = 2, width = 7, height= 6)) 

def test_test_parentsoffset():
    visualize_knitGraph(test_parentsoffset(4, 2))

def test_tube():
    visualize_knitGraph(tube(3, 3)[0], is_tube = True)

def test_lace():
    visualize_knitGraph(lace(4, 4))

def test_short_rows():
    knit_graph = short_rows(5, buffer_height=1)
    _, __ = knit_graph.get_courses()
    visualize_knitGraph(knit_graph)

def test_add_hole_on_tube():
    knit_graph, indicator, hole_end_wale = add_hole_on_tube(tube_width=3, tube_height=8, hole_start_course=3, hole_start_wale=2, hole_width=1, hole_height=2, carrier=3, new_carrier = 4)
    print('indicator', indicator)
    visualize_knitGraph(knit_graph, is_tube = True, indicator = indicator, hole_end_wale = hole_end_wale)

if __name__ == "__main__":
    # test_stockinette()
    # test_round_stockinette1()
    # test_round_stockinette2()
    # test_rib()
    # test_seed()
    # test_twisted_stripes()
    # test_hole()
    # test_lace()
    # test_short_rows()
    # test_hole_by_short_row()
    # test_test_parentsoffset()
    # test_tube()
    test_add_hole_on_tube()