from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from knitting_machine.final_knitgraph_to_knitout import Knitout_Generator

from debugging_tools.simple_knitgraph_generator import Simple_Knitgraph_Generator
from debugging_tools.polygon_generator import Polygon_Generator
from Modification_Generator.New_Mul_Hole_Generator_on_Sheet_KS import Hole_Generator_on_Sheet
from Modification_Generator.New_Mul_Hole_Generator_on_Tube_KS import Hole_Generator_on_Tube
from Modification_Generator.New_Pocket_Generator_on_Sheet_KS import Pocket_Generator_on_Sheet
from Modification_Generator.New_Pocket_Generator_on_Tube_KS import Pocket_Generator_on_Tube
from Modification_Generator.Handle_Generator_on_Sheet_KS import Handle_Generator_on_Sheet
from Modification_Generator.Handle_Generator_on_Tube_KS import Handle_Generator_on_Tube
from Modification_Generator.Strap_Generator_on_Tube_KS import Strap_Generator_on_Tube


def test_stst():
    """
    note that if the generated polygon look weird, specifically wales are not align, probably caused by the improper gauge setting used
    below.
    """
    # for sheet
    sheet_pattern = "all rs rows k. all ws rows p."
    sheet_yarn_carrier_id = 2
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    # knit_graph = compiler.compile(12, 10, object_type = 'sheet', pattern = sheet_pattern)
    knit_graph = compiler.compile(8, 7, object_type = 'sheet', pattern = sheet_pattern)
    # for tube
    # tube_pattern = "all rs rounds k. all ws rounds p."
    # tube_yarn_carrier_id = 3
    # compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    # knit_graph = compiler.compile(12, 10, object_type = 'tube', pattern = tube_pattern)
    
    # note that for gauge: 
    # if it is handle or pocket on tube, the gauge can be set by users to be any number <= 1/3; 
    # if it is handle or pocket on sheet, the gauge can be set by users to be any number <= 1/2.
    # if it is hole or tube or sheet, the gauge can be set by users to be any number <= 1/2.
    # if it is strap (which can only be on tube), the gauge can be set by users to be any number <= 1/2.
    knit_graph.gauge = 1/2
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    knit_graph.yarn_starting_direction = 'left to right'
    print(f'knit_graph.yarn_starting_direction in test_ks is {knit_graph.yarn_starting_direction}')
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()
  
    # add hole on sheet
    # below are for creating hole on rectangular shaped patterns 
    # yarns_and_holes_to_add = {6:[14, 15]}
    # {4:[19, 20, 28, 27], 2:[42, 37]}
    # {2: [29, 17, 18, 19],  4: [36, 37], 6:[45]}
    # {2: [45], 4: [36, 37], 6:[11, 12, 19, 20]} bind-off would fail in this case because a hole_start_course is 2.
    # {2: [29], 4: [35], 6:[27]} the one that tells us how to optimize code to stabilize unstable node. refer to slide pp. 203
    # {2: [20, 26, 27, 28, 34, 35, 36, 37, 38, 42, 44]} a heart-shaped hole
    # yarns_and_holes_to_add = {6:[29], 4:[20, 21, 22]}
    # yarns_and_holes_to_add = {1:[19, 20], 7:[34, 35], 4: [42]} used to replicate a figure used for the paper
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {1:[28], 7:[20], 4:[18]}, knitgraph = knit_graph)
    knitGraph = hole_generator.add_hole()
    # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    KnitGraph_Visualizer.visualize()

    # add hole on tube
    # # test hole on tube: non-decreased tube
    # hole_index_to_holes = {1: [51, 63]} tested! saved as tube_hole1 in local folder [latest_converted_knitouts] waited to be tested on machine.
    # # 2: [25, 26,  38], 4: [40, 28], 6:[51] tested! saved as tube_hole2 in local folder waited to be tested on machine.
    # # 2: [26, 38], 4: [28], 6:[40] tested! saved as tube_hole3 in local folder waited to be tested on machine.
    # hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = {2: [26, 38], 4: [28], 6:[40]}, knitgraph = knit_graph)
    # knitGraph = hole_generator.add_hole()
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add pocket on sheet
    # retangle pockect on stst
    # when gauge = 1/2: pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 3), (6, 3)], right_keynodes_child_fabric=[(3, 11), (6, 11)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 13), (6, 13)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = True, left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 13), (6, 13)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add pocket on tube
    # when gauge = 1/3: left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 7), (6, 7)], edge_connection_left_side = [True], close_top = True, edge_connection_right_side = [True]
    # when gauge = 1/3: left_keynodes_child_fabric=[(3, 4), (4, 1), (6, 1)], right_keynodes_child_fabric=[(3, 7), (4,10), (6, 10)], close_top = True, edge_connection_left_side = [True, True], edge_connection_right_side = [True, True]
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = True, left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 7), (6, 7)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # when gauge = 1/4: pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 13), (6, 13)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 13), (6, 13)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add handle on sheet
    # when gauge = 1/2: handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 3), (6, 3)], right_keynodes_child_fabric=[(3, 11), (6, 11)])
    # when gauge = 1/3: handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric = [(3, 13), (6, 13)])
    # handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 13), (6, 13)])
    # knitGraph = handle_generator.build_handle_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()
    
    # add handle on tube
    # when gauge = 1/3: left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 10), (6, 10)]
    # when gauge = 1/3: left_keynodes_child_fabric=[(3, 4), (4, 1), (6, 1)], right_keynodes_child_fabric=[(3, 7), (4,10), (6, 10)]
    # when gauge = 1/4: left_keynodes_child_fabric = [(3, 5), (4, 1), (6, 1)], right_keynodes_child_fabric = [(3, 13), (4, 17), (6, 17)]
    # handle_generator = Handle_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric = [(3, 5), (4, 1), (6, 1)], right_keynodes_child_fabric = [(3, 13), (4, 17), (6, 17)])
    # knitGraph = handle_generator.build_handle_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add strap on tube
    # tube_yarn_carrier_id is set to 9 is because 
    # when gauge = 1/2: strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1:{'front':(2, 4), 'back':(1,3)}, 2:{'front':(6, 8), 'back':(5, 7)}}, strap_height = 2)
    # strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1: {'front': (3, 6), 'back': (2, 5)}, 2: {'front': (9, 12), 'back': (8, 11)}}, strap_height = 2)
    # knitGraph = strap_generator.build_strap_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    #this convertor is for the modified knitgraph
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions(f"stst_test.k")
    
    #this convertor is for the unmodified knitgraph
    # generator = Knitout_Generator(knit_graph)
    # generator.write_instructions(f"stst_test.k")


def test_rib():
    rib_width = 1
    # sheet_pattern = f"all rs rows k rib={rib_width}, p rib. all ws rows k rib, p rib."
    # sheet_yarn_carrier_id = 3
    # compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    # knit_graph = compiler.compile(8, 8, object_type = 'sheet', pattern = sheet_pattern)

    tube_pattern = f"all rs rounds k rib={rib_width}, p rib. all ws rounds k rib, p rib."
    tube_yarn_carrier_id = 4
    compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    knit_graph = compiler.compile(9, 8, object_type = 'tube', pattern = tube_pattern)

    knit_graph.gauge = 0.5
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales()
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()


    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"rib.k")

 
def test_cable():
    sheet_pattern = r"""
        1st row k, lc2|2, k, rc2|2, [k] to end.
        all ws rows p.
        3rd row k 2, lc2|1, k, rc1|2, [k] to end.
        5th row k 3, lc1|1, k, rc1|1, [k] to end.
    """
    tube_pattern = r"""
        1st round k, lc2|2, k, rc2|2, [k] to end.
        all ws rounds p.
        3rd round k 2, lc2|1, k, rc1|2, [k] to end.
        5th round k 3, lc1|1, k, rc1|1, [k] to end.
    """
    sheet_yarn_carrier_id = 3
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    # knit_graph = compiler.compile(12, 5, object_type= 'sheet', pattern = sheet_pattern)
    knit_graph = compiler.compile(12, 5, object_type= 'tube', pattern = tube_pattern)
    knit_graph.gauge = 1/3
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()

    # yarns_and_holes_to_add = {2:[49], 7:[52, 53]} this throws an error 
    # yarns_and_holes_to_add = {2:[49], 7:[53]} this throws an error 
    # yarns_and_holes_to_add = {2:[49], 7:[41]}
    # yarns_and_holes_to_add = {2:[49], 7:[27, 26]}
    # hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {2:[49], 7:[27, 26]}, knitgraph = knit_graph)
    # knitGraph = hole_generator.add_hole()
    # # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add hole on tube
    # hole_index_to_holes = {3: [37]} this throws an error
    # hole_index_to_holes = {3: [32]} this throws an error
    # hole_index_to_holes = {3: [30]} this throws an error
    hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = {3: [44]}, knitgraph = knit_graph)
    knitGraph = hole_generator.add_hole()
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    KnitGraph_Visualizer.visualize()

    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"cable.k")

def test_lace():
    sheet_pattern = r"""
        all rs rows k, k2tog, yo 2, sk2po, yo 2, skpo, k. 
        all ws rows p 2, k, p 3, k, p 2.
    """

    tube_pattern = r"""
        all rs rounds k, k2tog, yo 2, sk2po, yo 2, skpo, k. 
        all ws rounds p 2, k, p 3, k, p 2.
    """


    # sheet_pattern = r"""
    #     all rs rows k, k2tog, yo. 
    #     all ws rows p 3, k.
    # """

    # tube_pattern = r"""
    #     all rs rounds k, k2tog, yo. 
    #     all ws rounds p 3, k.
    # """
    sheet_yarn_carrier_id = 3
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    knit_graph = compiler.compile(18, 10, object_type = 'sheet', pattern = sheet_pattern)

    # tube_yarn_carrier_id = 3
    # compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    # # knit_graph = compiler.compile(36, 10, object_type = 'tube', pattern = tube_pattern)

    # knit_graph = compiler.compile(4, 2, object_type = 'tube', pattern = tube_pattern)
    # knit_graph = compiler.compile(4, 2, object_type = 'sheet', pattern = sheet_pattern)
    # knit_graph = compiler.compile(18, 2, object_type = 'sheet', pattern = sheet_pattern)
    # knit_graph = compiler.compile(18, 10, object_type = 'tube', pattern = tube_pattern)
    knit_graph.gauge = 1/3
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales()
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()

    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {2:[49], 7:[98, 99]}, knitgraph = knit_graph)
    knitGraph = hole_generator.add_hole()
    # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    KnitGraph_Visualizer.visualize()

    # hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = {2: [58, 59], 4: [38]}, knitgraph = knit_graph)
    # knitGraph = hole_generator.add_hole()
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # left_keynodes_child_fabric=[(3, 13), (6, 13)], right_keynodes_child_fabric=[(3, 15), (6, 15)]
    # left_keynodes_child_fabric=[(3, 13), (6, 13)], right_keynodes_child_fabric=[(3, 19), (6, 19)]
    # pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = 3, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 13), (6, 13)], right_keynodes_child_fabric=[(3, 19), (6, 19)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # left_keynodes_child_fabric=[(2, 4), (5, 4)], right_keynodes_child_fabric=[(2, 13), (5, 13)] this is for [18, 10]
    # left_keynodes_child_fabric=[(2, 4), (10, 4)], right_keynodes_child_fabric=[(2, 22), (10, 22)] this is for []
    # pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 4, pocket_yarn_carrier_id=3, is_front_patch = True, left_keynodes_child_fabric=[(2, 4), (8, 4)], right_keynodes_child_fabric=[(2, 13), (8, 13)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # handle_generator = Handle_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 3, handle_yarn_carrier_id=4, is_front_patch = True, left_keynodes_child_fabric=[(2, 4), (5, 4)], right_keynodes_child_fabric=[(2, 13), (5, 13)])
    # knitGraph = handle_generator.build_handle_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    #this convertor is for the modified knitgraph
    # generator = Knitout_Generator(knitGraph)
    # generator.write_instructions(f"lace.k")

    #this convertor is for the unmodified knitgraph
    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"lace.k")

def test_write_slipped_rib():
    rib_width = 1

    # for sheet
    # sheet_pattern = f"all rs rows k rib={rib_width}, [k rib, p rib] to last rib sts, k rib. all ws rows k rib, [slip rib, k rib] to last rib sts, p rib."
    # sheet_yarn_carrier_id = 2
    # compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    # knit_graph = compiler.compile(12, 10, object_type = 'sheet', pattern = sheet_pattern)

    # for tube
    tube_pattern = f"all rs rounds k rib={rib_width}, [k rib, p rib] to last rib sts, k rib. all ws rounds k rib, [slip rib, k rib] to last rib sts, p rib."
    tube_yarn_carrier_id = 3
    compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    knit_graph = compiler.compile(12, 10, object_type = 'tube', pattern = tube_pattern)

    knit_graph.gauge = 1/3
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()

    # add hole on sheet
    # yarns_and_holes_to_add = {7:[34, 35], 4: [45]}
    # yarns_and_holes_to_add = {7:[34, 35]}
    # hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {7:[34, 35], 4: [45]}, knitgraph = knit_graph)
    # knitGraph = hole_generator.add_hole()
    # # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add pocket on sheet
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 11), (6, 11)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 11), (6, 11)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()
    
    # add pocket on tube
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric = [(3, 7), (6, 7)], right_keynodes_child_fabric = [(3, 13), (6, 13)], edge_connection_left_side = [True], close_top = True, edge_connection_right_side = [True])
    pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric = [(3, 7), (6, 7)], right_keynodes_child_fabric = [(3, 13), (6, 13)], edge_connection_left_side = [True], close_top = True, edge_connection_right_side = [True])
    knitGraph = pocket_generator.build_pocket_graph() 
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    KnitGraph_Visualizer.visualize()

    #this convertor is for the modified knitgraph
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions(f"slipped_rib.k")

    #this convertor is for the unmodified knitgraph
    # generator = Knitout_Generator(knit_graph)
    # generator.write_instructions(f"slipped_rib.k")

def test_write_slipped_rib_even():
    object_type = 'tube'
    rib_width =1
    # sheet_pattern = f" all rs rows k rib={rib_width}, p rib. all ws rows slip rib, p rib."
    tube_pattern = f"all rs rounds k rib={rib_width}, p rib. all ws rounds slip rib, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 5, tube_pattern)
    knit_graph.gauge = 0.5
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales(object_type = object_type) 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale(object_type = object_type)
    node_on_front_or_back = knit_graph.get_node_bed(object_type = object_type)
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph, object_type = object_type)
    KnitGraph_Visualizer.visualize()
    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"slipped_rib_even.k")


def test_write_short_rows():
    # for sheet
    # sheet_pattern = r"""
    #     1st row [k] to end.
    #     2nd row [p] to last 1 sts, slip 1.
    #     3rd row slip 1, [k] to last 1 sts, slip 1.
    #     4th row slip 1, [p] to last 2 sts, slip 2.
    #     5th row slip 2, [k] to last 2 sts, slip 2.
    #     6th row slip 2, [p] to end.
    #     7th row [k] to end.
    # """
    # sheet_yarn_carrier_id = 2
    # compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    # knit_graph = compiler.compile(5, 7, object_type = 'sheet', pattern = sheet_pattern)

    # for tube
    tube_pattern = r"""
        1st round [k] to end.
        2nd round [p] to last 1 sts, slip 1.
        3rd round slip 1, [k] to last 1 sts, slip 1.
        4th round slip 1, [p] to last 2 sts, slip 2.
        5th round slip 2, [k] to last 2 sts, slip 2.
        6th round slip 2, [p] to end.
        7th round [k] to end.
    """
    tube_yarn_carrier_id = 3
    compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    knit_graph = compiler.compile(8, 7, object_type = 'tube', pattern = tube_pattern)

    knit_graph.gauge = 1/3
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()

    # hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {7: [12, 15]}, knitgraph = knit_graph)
    # knitGraph = hole_generator.add_hole()
    # # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    #this convertor is for the modified knitgraph
    # generator = Knitout_Generator(knitGraph)
    # generator.write_instructions(f"short_rows.k")

    #this convertor is for the unmodified knitgraph
    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"short_rows.k")

if __name__ == "__main__":
    test_stst()
    # test_rib()
    # test_write_slipped_rib()
    # test_write_slipped_rib_even()
    # test_cable()
    # test_lace()
    # test_write_short_rows()
