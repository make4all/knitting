from debugging_tools.new_knit_graph_viz import visualize_knitGraph
from tests.test_hole_generator import *
from tests.test_pocket_generator import *
from debugging_tools.new_simple_knitgraphs import *
from knitting_machine.new_knitgraph_to_knitout import Knitout_Generator


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


def test_lace():
    knitGraph = lace(8,8)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_lace.k")


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

def lace_with_hole():     
    knitGraph, node_to_course_and_wale = test_lace_with_hole()
    generator = Knitout_Generator(knitGraph, node_to_course_and_wale)
    generator.write_instructions("test_lace_with_hole.k")

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
    knitGraph, node_to_course_and_wale = test_rectangle_pocket(spliting_nodes = [43, 44, 45, 46, 47, 48, 49, 50, 51, 52])
    generator = Knitout_Generator(knitGraph, node_to_course_and_wale)
    generator.write_instructions("test_rect_pocket.k")

if __name__ == "__main__":
    # test_stockinette()
    # test_rib()
    # test_seed()
    # test_twisted_stripes()
    # test_lace()
    # test_short_rows()
    # test_hole_by_short_row()

    # lace_with_hole()
    # cable_with_hole()
    # rib_with_hole()
    rect_pocket()