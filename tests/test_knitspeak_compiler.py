from debugging_tools.knit_graph_viz import visualize_knitGraph

from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from knitting_machine.knitgraph_to_knitout import Knitout_Generator


def test_stst():
    pattern = "all rs rows k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 4, pattern)
    # visualize_knitGraph(knit_graph, "stst.html")
    # visualize_knitGraph(knit_graph)
    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"stst.k")



def test_rib():
    rib_width = 1
    pattern = f"all rs rows k rib={rib_width}, p rib. all ws rows k rib, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 4, pattern)
    # visualize_knitGraph(knit_graph, "rib.html")
    visualize_knitGraph(knit_graph)


def test_cable():
    pattern = r"""
        1st row k, lc2|2, k, rc2|2, [k] to end.
        all ws rows p.
        3rd row k 2, lc2|1, k, rc1|2, [k] to end.
        5th row k 3, lc1|1, k, rc1|1, [k] to end.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(11, 6, pattern)
    # visualize_knitGraph(knit_graph, "cables.html")
    visualize_knitGraph(knit_graph)


def test_lace():
    pattern = r"""
        all rs rows k, k2tog, yo 2, sk2po, yo 2, skpo, k. 
        all ws rows p 2, k, p 3, k, p 2.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(10, 2, pattern)
    visualize_knitGraph(knit_graph, "lace.html")


def test_write_slipped_rib():
    rib_width = 1
    pattern = f"all rs rows k rib={rib_width}, [k rib, p rib] to last rib sts, k rib. all ws rows k rib, [slip rib, k rib] to last rib sts, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(6, 3, pattern)
    visualize_knitGraph(knit_graph, "slipped_rib.html")

def test_write_slipped_rib_even():
    rib_width =1
    pattern = f" all rs rows k rib={rib_width}, p rib. all ws rows slip rib, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 5, pattern)
    visualize_knitGraph(knit_graph, "slipped_rib.html")


def test_write_short_rows():
    pattern = r"""
        1st row [k] to end.
        2nd row [p] to last 1 sts, slip 1.
        3rd row slip 1, [k] to last 1 sts, slip 1.
        4th row slip 1, [p] to last 2 sts, slip 2.
        5th row slip 2, [k] to last 2 sts, slip 2.
        6th row slip 2, [p] to end.
        7th row [k] to end.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 7, pattern)
    visualize_knitGraph(knit_graph, "short_rows.html")


if __name__ == "__main__":
    # test_stst()
    # test_rib()
#     test_write_slipped_rib()
    # test_write_slipped_rib_even()
    test_cable()
    # test_lace()
