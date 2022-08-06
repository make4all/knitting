from pattern_modification.Hole_Generator import Hole_Generator
from debugging_tools.knit_graph_viz import visualize_knitGraph
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.simple_knitgraphs import *

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
    
def test_stst():
    pattern = "all rs rows k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(8, 6, pattern)
    visualize_knitGraph(knit_graph)
    return knit_graph

if __name__ == '__main__':
    # knit_graph = test_stst()
    # knit_graph = test_cable()
    knit_graph = test_short_rows()
    # knit_graph = test_lace()
    # generator = Hole_Generator(knit_graph, node_to_delete = [38, 49, 60], new_carrier = 4, unmodified = True)
    generator = Hole_Generator(knit_graph, node_to_delete = [15, 16, 17, 18, 19, 20], new_carrier = 4, unmodified = True)
    # generator = Hole_Generator(knit_graph, node_to_delete = [14, 15, 16, 17], new_carrier = 4, unmodified = True)
    knitGraph = generator.add_hole()

  
