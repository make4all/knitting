from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitting_machine.knitgraph_to_knitout import Knitout_Generator


# def test_stst():
#     carrier = 2
#     knitGraph = stockinette(20, 20, carrier=carrier)
#     generator = Knitout_Generator(knitGraph)
#     generator.write_instructions(f"stst_{carrier}.k")


def test_rib():
    knitGraph = rib(4, 4, 2)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_rib2.k")


# def test_seed():
#     knitGraph = seed(20, 10)
#     generator = Knitout_Generator(knitGraph)
#     generator.write_instructions("test_seed.k")


# def test_lace():
#     knitGraph = lace(4,4)
#     generator = Knitout_Generator(knitGraph)
#     generator.write_instructions("test_lace.k")


# def test_both_twists():
#     knitGraph = both_twists(height=3)
#     generator = Knitout_Generator(knitGraph)
#     generator.write_instructions("test_twists.k")


# def test_write_shortrows():
#     knitGraph = short_rows(20, buffer_height=5)
#     generator = Knitout_Generator(knitGraph)
#     generator.write_instructions("test_short_rows.k")

def test_hole_by_short_row():
    knitGraph = hole_by_short_row(hole_position = [3, 2], hole_width = 2, hole_height = 2, width = 7, height= 6)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_hole_by_short_row.k")

def test_round_stockinette1():
    knitGraph = round_stockinette1(width = 4, height =  2)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_round_stockinette1.k")

def test_round_stockinette2():
    knitGraph = round_stockinette2(width = 4, height =  2)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_round_stockinette2.k")

def test_test_parentsoffset():
    knitGraph = test_parentsoffset(4, 2)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_parentsoffset.k")

if __name__ == "__main__":
    # test_stockinette()
    # test_rib()
    test_test_parentsoffset()
    # test_seed()
    # test_twisted_stripes()
    # test_hole()
    # test_lace()
    # test_short_rows()
    # test_hole_by_short_row()
    # test_round_stockinette1()
    # test_round_stockinette2()

