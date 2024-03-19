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
from Modification_Generator.New_Strap_Without_Hole_Generator_on_Sheet_KS import *
from Modification_Generator.New_Strap_With_Hole_Generator_on_Sheet_KS import *
from Modification_Generator.New_Strap_Without_Hole_Generator_on_Tube_KS import Strap_Without_Hole_Generator_on_Tube
from Modification_Generator.New_Strap_With_Hole_Generator_on_Tube_KS import Strap_With_Hole_Generator_on_Tube
from debugging_tools.exceptions import ErrorException


def test_stst():
    """
    note that if the generated polygon look weird, specifically wales are not align, probably caused by the improper gauge setting used
    below.
    """
    # # for sheet
    sheet_pattern = r'''
        1st row k, k, k, k.
        2nd row k, k, yo, k, k.
        3rd row k, k, slip, k, k.
    ''' #[4, 3]
    sheet_pattern = r'''
        1st row [k] to end.
        2nd row k, k, yo, k, k.
        3rd row k, k, slip, k, k.
    ''' #[4, 3]
    # sheet_pattern =  "1st row k, slip, k." #[3,1]
    # # sheet_pattern =  r"""1st row k, slip, k.
    # #                     2nd row k 3."""
    sheet_pattern = r'''
        1st row yo, k, k, k, k.
    ''' #[4, 1]
    sheet_pattern = r'''
        1st row k, lc2|2, [k] to end. 2nd row k, lc2|2, [k] to end. 3rd row k, lc2|2, [k] to end.
    ''' #[6, 3]
    sheet_pattern = r'''
        all rs rows k 6. 
        all ws rows k 6.
    ''' #[6, 3]
    sheet_pattern = r'''
        From 1st to 3rd row k 4. 
    ''' #[6, 3]
    # sheet_pattern = r'''
    #     1st row [k] to end.
    #     2nd row k 2, [yo, k2tog, k 2] 2.
    #     3rd row k 2, [k2tog, yo, k 2] to end.
    #     4th row k 2, [yo, k2tog, k 2] 2.
    # ''' #[10, 4]
    # sheet_pattern = r'''
    #     From 1st to 2nd row [k] to end.
    #     From 3rd to 249th row k 4, [yo, k2tog, k 2] 5.
    #     250th row [k] to end.
    # ''' #[24, 250]
    # sheet_pattern =  "1st row k, slip, yo, k 3." #this one showcase the limitation of our current wale computation method: we need to have a variable storing the number of 
    #slip node between the yarn over node and the preceding node that is not slip
    
    # sheet_pattern = r'''
    #     1st row k 4.
    #     from ws 2nd to 4th row p 4.
    #     3rd row k 4.
    # ''' # size = [4, 4]
    # sheet_pattern = "all rs rows k 8. all ws rows p 8."  #for stockinette, most example hole nodes input are based on [8, 7]
    # sheet_pattern = "all rs rows k." #for garter
    # # sheet_pattern = "1st row p, k." #used to verify whether the result of compiler match the real hand-knitting rule.
    # sheet_pattern = "1st row k2tog, yo, k."  #get decrease and yarn-over figure to show. one [3, 1], one [12, 1]
    # # sheet_pattern = "1st row skpo, yo, k."  #get decrease and yarn-over figure to show. one [12, 1]
    # # sheet_pattern = "1st row k, yo, skpo."  #get decrease and yarn-over figure in symmetry to the above figure to show [3,1] or [12,1]
    # # sheet_pattern = "1st row k 6, lc2|2, k 2." #get cable figure to show, [12, 1]
    # # sheet_pattern = "1st row k 6, rc2|2, k 2." #get cable figure to show, [12, 1]
    # # sheet_pattern = "1st row k, lc2|2, k 7." #get cable figure to show, [12, 1]
    # # # sheet_pattern = "1st row k, lc2|2, k." #get cable figure to show, [6, 1]
    # # sheet_pattern = "1st row k, rc2|2, k." #get cable figure to show, [6, 1]
    # # sheet_pattern = "1st row lc2|2, k." # [5, 1]
    # # sheet_pattern = r"""1st row RCO, k 2, LCO.
    # #                     2nd row RCO, k 4, LCO.
    # #                 """ #[4, 1]
    # # sheet_pattern = r"""1st row slip, skpo, k, k, k2tog, slip. 
    # #                     2nd row k.
    # #                 """ #get edge decrease to figure show [6, 1] #wrong pattern
    # # sheet_pattern = "1st row slip, skpo, k2tog, slip." #get edge decrease to figure show [4, 1]
    # # sheet_pattern = "1st row skpo, k2tog." #get edge decrease to figure show [4, 1] #wrong pattern
    # # sheet_pattern = r"""1st row slip, skpo, k, k, k2tog, slip.
    # #                     2nd row slip, k2tog, skpo, slip.
    # #                 """ #get edge decrease to figure show [6, 2]
    # sheet_pattern = r"""
    #     1st row [k 3, p] to end.
    #     2nd row p 3, [k 1, slip 1] to last 3 sts, k 3.
    #     3rd row k 3, [p] to end.
    # # """#[32, 3]
    # sheet_yarn_carrier_id = 1
    # compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    # knit_graph = compiler.compile(starting_width = 4, row_count = 3
    #                               , object_type = 'sheet', pattern = sheet_pattern) #8 6; 8 10; [30, 50]
   
    # for tube
    # tube_pattern = r'''
    #     From 1st to 20th round [k, p] to end.
    #     21th round [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog.
    #     '''
    tube_pattern = r'''
            From 1st to 6th round [k] to end. 
            '''
# 64th round [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k.
# 65th round [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog.
# 66th round [p, k] to end.

    # tube_pattern = r'''
    #     From 1st to 62th round [k, p] to end.
    #     63th round [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog.
    #     64th round [p, k] 6, p, [p, k] 6, p, [p, k] 6, p, [p, k] 6, p, [p, k] 6, p, [p, k] 6, p.
    #     65th round [p, k] 5, p, k2tog, [p, k] 5, p, k2tog, [p, k] 5, p, k2tog, [p, k] 5, p, k2tog, [p, k] 5, p, k2tog, [p, k] 5, p, k2tog.
    #     66th round [p, k] to end.
    # ''' #[56, 21]
    
    # 67th round [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog.
    # 68th round [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k.
    # 69th round [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog.
    # 70th round [p, k] to end.

    # 71st round [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog.
    # 72nd round [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k.
    # 73rd round [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog.
    # 74th round [p, k] to end.

    # 75th round [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog.
    # 76th round [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k.
    # 77th round [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog.
    # 78th round [p, k] to end.

    # 79th round [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog, [p, k] 6, k2tog.
    # 80th round [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k, [p, k] 6, p, k.
    # 81st round [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog, [p, k] 5, p, k, k2tog.
    # 82nd round [p, k] to end.

    # tube_pattern = 
    # r'''
    #     1st round p, [p, k] to end.
    # ''' 
    #for stockinette
    
    tube_pattern = "all rs rounds k 12. all ws rounds k 12." #for garter [10, 6]
    # tube_pattern = "1st round slip, k2tog, k 2, skpo, slip 2, k2tog, k 2, skpo, slip." # latest compiler version [12, 1]
    # tube_pattern = "1st round k2tog, yo, k."  #get decrease and yarn-over figure to show. [12, 1]
    # tube_pattern = "1st round skpo, yo, k."  #get decrease and yarn-over figure to show. [12, 1]
    # tube_pattern = "1st round k, yo, skpo."  #get decrease and yarn-over figure show [12,1]
    # tube_pattern = "1st round k, yo, k."  #get decrease and yarn-over figure show [12,1]
    # tube_pattern = "1st round k 2, lc2|2, k 2." #get unknittable cable figure to show, [8, 1]
    # tube_pattern = "1st round k 6, lc2|2, k 2." #get left lean cable on back part of tube figure to show, [12, 1]
    # tube_pattern = "1st round k 6, rc2|2, k 2." #get right lean cable on back part of tube figure to show, [12, 1]
    # tube_pattern = "1st round k, lc2|2, k 7." #get left lean cable on front part of tube to show, [12, 1]
    # tube_pattern = "1st round LCO, RCO, LCO, RCO." #[4, 1]
    # tube_pattern = r"""1st round slip, skpo, k 4, k2tog, slip, slip, skpo, k 4, k2tog, slip.
    #                     2nd round slip, slip, skpo, k 2, k2tog, slip, slip, slip, slip, skpo, k 2, k2tog, slip, slip.
    #                     3rd round slip, slip, slip, skpo, k2tog, slip, slip, slip, slip, slip, slip, skpo, k2tog, slip, slip, slip.
    #                 """ #get edge decrease with hole added figure show [16, 3]  #    
    
    # tube_pattern = r"""1st round slip, skpo, k 2, k2tog, slip, slip, skpo, k 2, k2tog, slip.
    #                    2nd round slip, slip, skpo, k2tog, slip, slip, slip, slip, skpo, k2tog, slip, slip.
    #                 """ #get edge decrease figure show [12, 2]  

    # knit_graph = compiler.compile(starting_width=width, row_count=height, object_type=knit_speak_procedure.lower(),
    #                                   pattern=pattern_used)
    #---
    # hat_width = 24
    # rib_width = 1
    # tube_pattern = f""" 1st round k rib={rib_width}, p rib.
    #                     2nd round k num={hat_width}.
    #                     3rd round slip, skpo, [k] to last {int(hat_width/2+2)} sts, k2tog, slip 2, skpo, [k] to last 2 sts, k2tog, slip.
    #                     4th round slip 2, skpo, [k] to last {int(hat_width/2+3)} sts, k2tog, slip 4, skpo, [k] to last 3 sts, k2tog, slip 2.""" #old compiler version 
    #---[24, 4]
    # tube_pattern = """ 1st round k rib=1, p rib. 
    #                    2nd round k num=24. 
    #                    3rd round slip, k2tog, [k] to last 14 sts, skpo, slip 2, k2tog, [k] to last 2 sts, skpo, slip. 
    #                    4th round slip 2, k2tog, [k] to last 15 sts, skpo, slip 4, k2tog, [k] to last 3 sts, skpo, slip 2."""  #latest compiler version ---[24, 4]
    # # r"""1st round k 12.
    # #     2nd round slip, skpo, k, k, k2tog, slip, slip, skpo, k, k, k2tog, slip."""

    # tube_pattern = r'''
    #         From rs 1st to 9th round p 6, k 6.
    #         From ws 2nd to 10th round k 6, k 6.
    # ''' #[10, 12] [w, h]

    # tube_yarn_carrier_id = 1
    # compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    # knit_graph = compiler.compile(12, 4, object_type = 'tube', pattern = tube_pattern) #[12, 10]; for tube [12, 5]; [48, 30]
    
    # tube_pattern = r'''
    #         1st round k 6, yo, k 12, yo, k 6.
    #         2nd round k 6, yo, k 12, yo, k 8.
    #     ''' #[24, 2]
    
    # tube_pattern = r'''
    #         1st round k 2, p 2.
    #         2nd round [k] to end.
    #         3rd round k 2, yo, yo, k 2.
    #     ''' #[4, 3]
    # tube_pattern = r'''
    #     1st round k 12, p 12.
    #     2nd round [k] to end.
    #     3rd round k 7, yo, k 7, yo, k 7, yo, k 3.
    #     4th round k 8, yo, k 19.
    # ''' # [24, 3]
    # tube_pattern = r'''
    #     1st round [k, p] to end.
    #     2nd round [k] to end.
    #     3rd round k 6, k2tog, k 6, k2tog, k 8, k 6, k2tog, k 6, k2tog, k 14.  
    # ''' # [56, 3] for warm one
    # tube_pattern = "1st round [k 2, p 3] to end." #test [stitch1 n, stitch2 m] syntax
    # tube_pattern = r'''
    #     1st round [k] to end.
    #     2nd round [k, p] to end.
    #     3rd round [k, skpo, k 14, k2tog, k] to end.
    # ''' #[20, 3] for skyping beanie
    # tube_pattern = r'''
    #     1st round [k 2, p 2] to end.
    #     2nd round [p 1, k 4, k2tog, k 2, yo, p 1, yo, k 2, skpo, k 4] to end. 
    #     3rd round [p 1, k 8, p 1, k 8] to end.
    #     4th round [p 1, k 3, k2tog, k 2, yo, k 1, p 1, k 1, yo, k 2, skpo, k 3] to end.
    # ''' #[72, 4] for giftie slouchie beanie
    # tube_pattern = r'''
    #     1st round k 4.
    #     from ws 2nd to 4th round k 4.
    #     3rd round k 4.
    # ''' # size = [4, 4]
    # tube_pattern = r'''
    #     1st round [k 2, skpo, k] to end.
    # '''
    # tube_pattern = r'''
    #     From 1st to 4th round [k 3, p 3] to end.
    #     5th round [k 3, p 3] 7, k 1, k 2, p 3, [k 3, p 3] 2, k 3, p 3, [k 3, p 3] to end.
    # ''' #smiths' hat, size = [132, 5]
    # tube_pattern = r'''
    #     1st round slip, k 2, slip 5.
    #     2nd row slip 5, k 2, slip.
    #     3rd row k 8.
    #     4th round k 8.
    # ''' # [8, 4]
    # tube_pattern = r'''
    #     1st round slip, k 9, slip 12.
    #     2nd row slip 12, k 9, slip.
    #     3rd row k 22.
    #     4th round k 22.
    # ''' # [22, 4]
    # tube_pattern = r'''
    #     1st round slip, k 9, slip 12.
    #     2nd round k 22.
    #     3rd row slip 12, k 9, slip.
    #     4th row k 22.
    # ''' # [22, 4] pattern haha
    # tube_pattern = r'''
    #     From 1st to 4th round k 22. 
    #     5th round slip, k 9, slip 12.
    #     6th row slip 12, k 9, slip.
    #     7th row k 22. 
    #     8th round k 22.
    # '''
    # tube_pattern = r'''
    #     1st round slip, k 2, slip 5.
    #     2nd row slip 5, k 2, slip.
    #     3rd round k 8.
    #     4th round k 8.
    # ''' # [8, 4]    
    # tube_pattern = r'''
    #         1st round [k2tog, yo] to end.
    # ''' #[4, 1]
    # tube_pattern=r'''
    #         From 1st to 4th round [k, p] to end.    
    #         5th round [k2tog, yo] to end.
    # '''#[36, 5]
    tube_yarn_carrier_id = 1
    compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    knit_graph = compiler.compile(10, 6, object_type = 'tube', pattern = tube_pattern) #[12, 10]; for tube [12, 5]; [48, 30]

    # note that for gauge: 
    # if it is handle or pocket on tube, the gauge can be set by users to be any number <= 1/3; 
    # if it is handle or pocket on sheet, the gauge can be set by users to be any number <= 1/2.
    # if it is hole or tube or sheet, the gauge can be set by users to be any number <= 1/2.
    # if it is strap (which can only be on tube), the gauge can be set by users to be any number <= 1/2.    
    knit_graph.gauge = 1/2
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_to_loops_on_front_part_of_the_tube, course_to_loops_on_back_part_of_the_tube = knit_graph.get_node_bed_for_courses()
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    #----
    max_wale_id_front_and_back = knit_graph.get_min_and_max_wale_id_on_course_on_bed()
    knit_graph.update_wales_to_reduce_float()
    knit_graph.adjust_overall_slanting()
    #----
    knit_graph.update_parent_offsets()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph=knit_graph)
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
    # yarns_and_holes_to_add = {1:[4]} needs to debug when starting_width = 3, row_count = 2
    # yarns_and_holes_to_add = {1:[19, 20], 7:[34, 35], 4: [42]} used to replicate a figure used for the paper
    # yarns_and_holes_to_add = {1: [20], 3: [28]}
    # yarns_and_holes_to_add = {1: [20], 3: [28], 5: [18]}
    # yarns_and_holes_to_add = {3: [20, 26, 27, 28, 34, 35, 36, 37, 38, 42, 44]} heart shape
    # yarns_and_holes_to_add = {3:[19, 20], 1:[34, 35], 4: [42]}  used to replicate another figures used for the paper
    # yarns_and_holes_to_add = {1:[29], 3:[35], 7:[27]} used for 
    # hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {1:[13]}, knitgraph = knit_graph) 
    #for size = [30, 20], gauge = 1, hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {1:[226,225,224,223,222,221,258,257,256,255,254,253, 286,285,284,283,282,281,318,317,316,315,314,313,346,345,344,343,342,341]}, knitgraph = knit_graph)  
    #for size = [30, 50], gauge = 1, hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {1:[346,345,344,343,342,341,378,377, 376, 375, 374,373, 406, 405, 404, 403, 402, 401]}, knitgraph = knit_graph)  
    # yarns_and_holes_to_add = {1: [20, 28], 4: [18]}
    # yarns_and_holes_to_add = {1: [35, 27], 4: [29]}
    # yarns_and_holes_to_add = {1: [29], 4: [35, 27]} #compared to the above and u will understand why we want to organize the hole by hole_start_course and hole_end_course.
    # yarns_and_holes_to_add = {1: [27, 36], 4: [29]} , 4:[29]
    # hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {1: [37], 4:[20]}, knitgraph = knit_graph)  
    # hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = { 4:[16]}, knitgraph = knit_graph)  
    # knitGraph = hole_generator.add_hole()
    # # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    #add strap without hole on sheet 
    #a vertical one
    # strap_without_hole_generator = Strap_Without_Hole_Generator_on_Sheet(knit_graph, sheet_yarn_carrier_id=1, strap_yarn_carrier_id = 2, is_front_patch=False, keynode_child_fabric = [(4, 5), (4, 9)], strap_length = 12)  
    #a horizontal one
    # strap_without_hole_generator = Strap_Without_Hole_Generator_on_Sheet(knit_graph, sheet_yarn_carrier_id=1, strap_yarn_carrier_id = 2, is_front_patch=False, keynode_child_fabric = [(6,5), (9,5)], strap_length = 12)  
    # knitGraph, updated_child_knitgraph, updated_parent_knitgraph = strap_without_hole_generator.build_strap_without_hole_graph()
    # # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()
    # #
    # strap_with_hole_generator = Strap_With_Hole_Generator_on_Sheet(knitGraph, updated_parent_knitgraph, updated_child_knitgraph, yarns_and_holes_to_add={4: [89]})
    # strap_with_hole_graph = strap_with_hole_generator.build_strap_with_hole_graph()
    # KnitGraph_Visualizer = knitGraph_visualizer(strap_with_hole_graph)
    # KnitGraph_Visualizer.visualize()

    #add strap without hole on tube
    #a vertical one
    # strap_without_hole_generator = Strap_Without_Hole_Generator_on_Tube(knit_graph, tube_yarn_carrier_id=1, strap_yarn_carrier_id = 2, is_front_patch=False, keynode_child_fabric = [(4, 1), (4, 7)], strap_length = 12)  
    #a horizontal one
    # strap_without_hole_generator = Strap_Without_Hole_Generator_on_Tube(knit_graph, tube_yarn_carrier_id=1, strap_yarn_carrier_id = 2, is_front_patch=False, keynode_child_fabric = [ (4,1), (8,1)], strap_length = 18)
    # knitGraph, updated_child_knitgraph, updated_parent_knitgraph = strap_without_hole_generator.build_strap_without_hole_graph()
    # # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()
    # #
    # strap_with_hole_generator = Strap_With_Hole_Generator_on_Tube(knitGraph, updated_parent_knitgraph, updated_child_knitgraph, yarns_and_holes_to_add = {6: [87, 88]})
    # strap_with_hole_graph = strap_with_hole_generator.build_strap_with_hole_graph()
    # KnitGraph_Visualizer = knitGraph_visualizer(strap_with_hole_graph)
    # KnitGraph_Visualizer.visualize()
    
    

    # add hole on tube
    # # test hole on tube: non-decreased tube
    # hole_index_to_holes = {1: [51, 63]} tested! saved as tube_hole1 in local folder [latest_converted_knitouts] waited to be tested on machine.
    # 2: [25, 26,  38], 4: [40, 28], 6:[51] tested! saved as tube_hole2 in local folder waited to be tested on machine.
    # 2: [26, 38], 4: [28], 6:[40] tested! saved as tube_hole3 in local folder waited to be tested on machine.
    # hole_index_to_holes = {2: [50, 51]}
    # hole_index_to_holes = {1: [41]} #get figure for paper
    # hole_index_to_holes = {1: [25], 2:[27], 3:[49]} #get figure for paper
    # hole_index_to_holes = {1: [24]} #get figure in the slide
    # hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = {1: [24]}, knitgraph = knit_graph)
    # list_of_holes = [[26, 38], [28], [40]]
    # list_of_holes = [[51,63]]
    # # for size = [48, 30], hole_generator = Hole_Generator_on_Tube(list_of_holes = [[585, 586, 587, 588, 589, 590, 633, 634, 635, 636, 637, 638, 681, 682, 683, 684, 685, 686, 729, 730, 731, 732, 733, 734]], knitgraph = knit_graph)
    # hole_generator = Hole_Generator_on_Tube(list_of_holes = [[24, 35, 25, 34, 36,47]], knitgraph = knit_graph)
    hole_generator = Hole_Generator_on_Tube(list_of_holes = [[22,21,31,32,42,41,51,52]], knitgraph = knit_graph)
    knitGraph = hole_generator.add_hole()
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    KnitGraph_Visualizer.visualize()

    # add pocket on sheet
    # when gauge = 1/2: a square pocket -- pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 3), (6, 3)], right_keynodes_child_fabric=[(3, 11), (6, 11)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # when gauge = 1/2: a hexagonal pocket -- pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (4, 3), (6, 3), (7, 5)], right_keynodes_child_fabric=[(3, 9), (7, 9)], close_top = False, edge_connection_left_side = [True, False, False], edge_connection_right_side = [True])
    # when gauge = 1/2: a trapezoid pocket -- pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (5, 1)], right_keynodes_child_fabric=[(3, 9), (5, 13)], close_top = True, edge_connection_left_side = [False], edge_connection_right_side = [False])
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 13), (6, 13)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = True, left_keynodes_child_fabric=[(3, 3), (6, 3)], right_keynodes_child_fabric=[(3, 11), (6, 11)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # for size = [30, 40], gauge = 1/2, pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(10, 9), (30, 9)], right_keynodes_child_fabric=[(10, 41), (30, 41)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(2,1), (3,1), (4,3)], right_keynodes_child_fabric=[(2,7), (4,7)], close_top = False, edge_connection_left_side = [True, False], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add pocket on tube
    # when gauge = 1/3: left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 7), (6, 7)], edge_connection_left_side = [True], close_top = False, edge_connection_right_side = [True]
    # when gauge = 1/3: hexagon left_keynodes_child_fabric=[(3, 4), (4, 1), (6, 1)], right_keynodes_child_fabric=[(3, 7), (4,10), (6, 10)], close_top = True, edge_connection_left_side = [True, True], edge_connection_right_side = [True, True]
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = True, left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 7), (6, 7)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # when gauge = 1/4: pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 13), (6, 13)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # (5,10), (8,10) and (5,22) and (8,22)
    # pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(5,10), (8,10)], right_keynodes_child_fabric=[(5,22), (8,22)], close_top = True, edge_connection_left_side = [False], edge_connection_right_side = [False])
    # for size = [48, 30], kangaroo pocket, pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(5, 10), (15, 10)], right_keynodes_child_fabric=[(5, 40), (15, 40)], close_top = True, edge_connection_left_side = [False], edge_connection_right_side = [False])
    # pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(2,1), (3,1)], right_keynodes_child_fabric=[(2,4), (3,4)], edge_connection_left_side = [True], close_top = False, edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add handle on sheet
    # when gauge = 1/2: handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 3), (6, 3)], right_keynodes_child_fabric=[(3, 11), (6, 11)])
    # when gauge = 1/3: handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric = [(3, 13), (6, 13)])
    # when gauge = 1/2: trapezoid handle - left_keynodes_child_fabric = [(3, 5), (4, 1), (6, 1)], right_keynodes_child_fabric = [(3, 13), (4, 17), (6, 17)]
    # handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = True, left_keynodes_child_fabric = [(3, 5), (4, 1), (6, 1)], right_keynodes_child_fabric = [(3, 9), (4, 13), (6, 13)])
    # handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric = [(4,5), (6,5)], right_keynodes_child_fabric = [(4, 11), (6, 11)])
    # for size = [30, 40], gauge = 1/2-- this handle can be a bit shorter: handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(10, 9), (30, 9)], right_keynodes_child_fabric=[(10, 41), (30, 41)])
    # for size = [30, 40], handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(10, 9), (20, 9)], right_keynodes_child_fabric=[(10, 41), (20, 41)])
    # handle_generator = Handle_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(2,1), (3,1)], right_keynodes_child_fabric=[(2, 5), (3, 5)])
    # knitGraph = handle_generator.build_handle_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()
    
    # add handle on tube
    # when gauge = 1/3: left_keynodes_child_fabric=[(3, 4), (6, 4)], right_keynodes_child_fabric=[(3, 10), (6, 10)]
    # when gauge = 1/3: trapezoid handle - left_keynodes_child_fabric=[(3, 4), (4, 1), (6, 1)], right_keynodes_child_fabric=[(3, 7), (4,10), (6, 10)]
    # when gauge = 1/4: left_keynodes_child_fabric = [(3, 5), (4, 1), (6, 1)], right_keynodes_child_fabric = [(3, 13), (4, 17), (6, 17)]
    # handle_generator = Handle_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, handle_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(3, 4), (4, 1), (6, 1)], right_keynodes_child_fabric=[(3, 16), (4, 19), (6, 19)])
    # for size = [48, 30], handle_generator = Handle_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, handle_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(5,10), (8,10)], right_keynodes_child_fabric=[(5,22), (8,22)])
    # handle_generator = Handle_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, handle_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(2,1), (3,1)], right_keynodes_child_fabric=[(2,10), (3,13)])
    # knitGraph = handle_generator.build_handle_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add strap on tube
    # tube_yarn_carrier_id is set to 9 is because 
    # when gauge = 1/2: strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1:{'front':(2, 4), 'back':(1,3)}, 2:{'front':(6, 8), 'back':(5, 7)}}, strap_height = 2)
    # when gauge = 1/3: strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1: {'front': (3, 6), 'back': (2, 5)}, 2: {'front': (9, 12), 'back': (8, 11)}}, strap_height = 6)
    # below are the updated input for straps
    # strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1:{'front':[(2, 6), 2], 'back':[(1, 5), 3]}, 2:{'front':[(8, 12), 4], 'back':[(7, 11), 5]}}, strap_height = 5)
    # strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 6, straps_coor_info = {1:{'front':[(2, 4), 2], 'back':[(1,3), 3]}, 2:{'front':[(6, 8), 4], 'back':[(5, 7), 5]}}, strap_height = 2)
    # for size = [48, 30], gauge = 1/2, strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1:{'front':[(30, 40), 2], 'back':[(29, 39), 3]}, 2:{'front':[(8, 18), 4], 'back':[(7, 17), 5]}}, strap_height = 18)
    # strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 6, straps_coor_info = {1:{'front':[(2, 4), 2], 'back':[(1,3), 3]}, 2:{'front':[(6, 8), 4], 'back':[(5, 7), 5]}}, strap_height = 2)
    # for size = [70, 30], gauge = 1/2, strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1:{'front':[(42, 62), 2], 'back':[(41, 61), 3]}, 2:{'front':[(8, 28), 4], 'back':[(7, 27), 5]}}, strap_height = 25)
    # strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1:{'front':[(30, 40), 2], 'back':[(29, 39), 3]}, 2:{'front':[(8, 18), 4], 'back':[(7, 17), 5]}}, strap_height = 20)
    # strap_generator = Strap_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 10, straps_coor_info={1:{'front':[(8, 28), 4], 'back':[(7, 27), 5]}, 2:{'front':[(42, 62), 2], 'back':[(41, 61), 3]}}, strap_height = 25)
    # knitGraph = strap_generator.build_strap_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # this convertor is for the modified knitgraph
    # generator = Knitout_Generator(strap_with_hole_graph)
    # generator = Knitout_Generator(knitGraph)
    # generator.write_instructions(f"stst_test.k")
    
    #this convertor is for the unmodified knitgraph
    generator = Knitout_Generator(knit_graph) 
    generator.write_instructions(f"stst_test.k")


def test_rib():
    rib_width = 1
    sheet_pattern = f"all rs rows k rib={rib_width}, p rib. all ws rows k rib, p rib."
    sheet_yarn_carrier_id = 3
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    knit_graph = compiler.compile(8, 8, object_type = 'sheet', pattern = sheet_pattern)

    # tube_pattern = f"all rs rounds k rib={rib_width}, p rib. all ws rounds k rib, p rib."
    # tube_yarn_carrier_id = 4
    # compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    # knit_graph = compiler.compile(9, 8, object_type = 'tube', pattern = tube_pattern)

    knit_graph.gauge = 0.5
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales()
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    knit_graph.update_parent_offsets()
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
    """#[12, 5]
    sheet_pattern = r""" 
        1st row k, lc2|2, k, rc2|2, [k] to end.
    """
    # tube_pattern = r"""
    #     1st round k, lc2|2, k, rc2|2, [k] to end.
    #     all ws rounds p.
    #     3rd round k 2, lc2|1, k, rc1|2, [k] to end.
    #     5th round k 3, lc1|1, k, rc1|1, [k] to end.
    # """
    sheet_yarn_carrier_id = 3
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    knit_graph = compiler.compile(6, 1, object_type= 'sheet', pattern = sheet_pattern)
    # knit_graph = compiler.compile(12, 8, object_type= 'tube', pattern = tube_pattern)
    knit_graph.gauge = 1/2
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    knit_graph.update_parent_offsets()
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
    # hole_generator = Hole_Generator_on_Tube(hole_index_to_holes = {3: [44]}, knitgraph = knit_graph)
    # knitGraph = hole_generator.add_hole()
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add pocket on sheet
    # when gauge = 1/2, pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = 3, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(2, 3), (4, 3)], right_keynodes_child_fabric=[(2, 11), (4, 11)], close_top = True, edge_connection_left_side = [False], edge_connection_right_side = [False])
    # when gauge = 1/2, pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = 3, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(1, 3), (3, 3)], right_keynodes_child_fabric=[(1, 17), (3, 17)], close_top = True, edge_connection_left_side = [False], edge_connection_right_side = [False])
    # pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = 3, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(1, 3), (3, 3)], right_keynodes_child_fabric=[(1, 17), (3, 17)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # add pocket on tube
    # since we set the racking bound to 4 in our pipeline, so 1/3 gauge for pk on tube will always exceed the limit, making this pattern no suitable to get a figure.
    # pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 4, pocket_yarn_carrier_id = 3, is_front_patch = True, left_keynodes_child_fabric=[(2, 4), (6, 4)], right_keynodes_child_fabric=[(2, 13), (6, 13)], close_top = True, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    #this convertor is for the modified knitgraph
    # generator = Knitout_Generator(knitGraph)
    # generator.write_instructions(f"cable.k")

    #this convertor is for the unmodified knitgraph
    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"cable.k")

def test_lace():
    # sheet_pattern = r"""
    #     all rs rows k, k2tog, yo 2, sk2po, yo 2, skpo, k. 
    #     all ws rows p 2, k, p 3, k, p 2.
    # """

    tube_pattern = r"""
        all rs rounds k, k2tog, yo 2, sk2po, yo 2, skpo, k. 
        all ws rounds p 2, k, p 3, k, p 2.
    """


    sheet_pattern = r"""
        1st row [k] to end.
        2nd row k, yo, k2tog, [k] to end. 
    """ #[2, 10]

    sheet_pattern = r"""
        1st row [k] to end.         
        From 2nd to 5th row k, yo, k2tog, [k] to end. 6th row [k] to end.
    """ #[6, 10] [h, w]
    # 2nd row p, skpo, yo, k.
    # 3rd row p 2, k 2.
    # from 4th to 6th row k 4.

    # tube_pattern = r"""
    #     all rs rounds k, k2tog, yo. 
    #     all ws rounds p 2, k.
    # """

    # for sheet 
    sheet_yarn_carrier_id = 3
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    knit_graph = compiler.compile(10, 6, object_type = 'sheet', pattern = sheet_pattern)

    # for tube
    # tube_yarn_carrier_id = 3
    # compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    # knit_graph = compiler.compile(18, 10, object_type = 'tube', pattern = tube_pattern)
    # knit_graph = compiler.compile(4, 2, object_type = 'tube', pattern = tube_pattern)
    # knit_graph = compiler.compile(4, 2, object_type = 'sheet', pattern = sheet_pattern)
    # knit_graph = compiler.compile(18, 2, object_type = 'sheet', pattern = sheet_pattern)

    knit_graph.gauge = 1/3
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales()
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    knit_graph.update_parent_offsets()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()

    # yarns_and_holes_to_add = {2:[49], 7:[98, 99]} for [18, 10]
    hole_generator = Hole_Generator_on_Sheet(yarns_and_holes_to_add = {2:[32, 33]}, knitgraph = knit_graph)
    knitGraph = hole_generator.add_hole()
    # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self.node_on_front_or_back and self.node_to_course_and_wale)
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    KnitGraph_Visualizer.visualize()

    # list_of_holes = [[58, 59], [38]]
    # list_of_holes = [[58, 59, 60]]
    # hole_generator = Hole_Generator_on_Tube(list_of_holes = [[57]], knitgraph = knit_graph)
    # knitGraph = hole_generator.add_hole(bind_off=False)
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # left_keynodes_child_fabric=[(3, 13), (6, 13)], right_keynodes_child_fabric=[(3, 15), (6, 15)]
    # when gauge = 1/2, left_keynodes_child_fabric=[(3, 13), (6, 13)], right_keynodes_child_fabric=[(3, 19), (6, 19)]
    # pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = 3, pocket_yarn_carrier_id = 4, is_front_patch = True, left_keynodes_child_fabric=[(2, 3), (5, 3)], right_keynodes_child_fabric=[(2, 11), (5, 11)], close_top = True, edge_connection_left_side = [False], edge_connection_right_side = [False])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # [18, 10] - pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 3, pocket_yarn_carrier_id = 4, is_front_patch = True, left_keynodes_child_fabric=[(2, 1), (5, 1)], right_keynodes_child_fabric=[(2, 10), (5, 10)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # left_keynodes_child_fabric=[(2, 4), (10, 4)], right_keynodes_child_fabric=[(2, 22), (10, 22)] this is for []
    # pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 3, pocket_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric=[(2, 1), (5, 1)], right_keynodes_child_fabric=[(2, 10), (5, 10)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # handle_generator = Handle_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = 3, handle_yarn_carrier_id = 4, is_front_patch = True, left_keynodes_child_fabric=[(2, 4), (5, 4)], right_keynodes_child_fabric=[(2, 13), (5, 13)])
    # knitGraph = handle_generator.build_handle_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    # this convertor is for the modified knitgraph
    # generator = Knitout_Generator(knitGraph)
    # generator.write_instructions(f"lace.k")

    #this convertor is for the unmodified knitgraph
    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"lace.k")

def test_write_slipped_rib():
    rib_width = 1

    # for sheet
    sheet_pattern = f"all rs rows k rib={rib_width}, [k rib, p rib] to last rib sts, k rib. all ws rows k rib, [slip rib, k rib] to last rib sts, p rib."
    # sheet_pattern = f"all rs rows k. all ws rows k rib={rib_width}, [slip rib, k rib]." #get the slip figure, [4, 2]
    sheet_yarn_carrier_id = 2
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    knit_graph = compiler.compile(12, 10, object_type = 'sheet', pattern = sheet_pattern)

    # for tube
    # tube_pattern = f"all rs rounds k rib={rib_width}, [k rib, p rib] to last rib sts, k rib. all ws rounds k rib, [slip rib, k rib] to last rib sts, p rib."
    # tube_yarn_carrier_id = 3
    # compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    # knit_graph = compiler.compile(12, 10, object_type = 'tube', pattern = tube_pattern)

    knit_graph.gauge = 1/3
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    knit_graph.update_parent_offsets()
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
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 23), (6, 23)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 11), (6, 11)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 23), (6, 23)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    knitGraph = pocket_generator.build_pocket_graph() 
    KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    KnitGraph_Visualizer.visualize()
    
    # add pocket on tube
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric = [(3, 7), (6, 7)], right_keynodes_child_fabric = [(3, 13), (6, 13)], edge_connection_left_side = [True], close_top = True, edge_connection_right_side = [True])
    # when gauge = 1/3: pocket_generator = Pocket_Generator_on_Sheet(parent_knitgraph = knit_graph, sheet_yarn_carrier_id = sheet_yarn_carrier_id, pocket_yarn_carrier_id=4, is_front_patch = False, left_keynodes_child_fabric=[(3, 5), (6, 5)], right_keynodes_child_fabric=[(3, 23), (6, 23)], close_top = False, edge_connection_left_side = [True], edge_connection_right_side = [True])
    # pocket_generator = Pocket_Generator_on_Tube(parent_knitgraph = knit_graph, tube_yarn_carrier_id = tube_yarn_carrier_id, pocket_yarn_carrier_id = 4, is_front_patch = False, left_keynodes_child_fabric = [(3, 7), (6, 7)], right_keynodes_child_fabric = [(3, 13), (6, 13)], edge_connection_left_side = [True], close_top = False, edge_connection_right_side = [True])
    # knitGraph = pocket_generator.build_pocket_graph() 
    # KnitGraph_Visualizer = knitGraph_visualizer(knitGraph)
    # KnitGraph_Visualizer.visualize()

    #this convertor is for the modified knitgraph
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions(f"slipped_rib.k")

    #this convertor is for the unmodified knitgraph
    # generator = Knitout_Generator(knit_graph)
    # generator.write_instructions(f"slipped_rib.k")

def test_write_slipped_rib_even():
    rib_width =1
    # for sheet
    # sheet_yarn_carrier_id = 2
    # sheet_pattern = f"all rs rows k rib={rib_width}, p rib. all ws rows slip rib, p rib."
    # compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    # knit_graph = compiler.compile(4, 5, object_type = 'sheet', pattern = sheet_pattern)
    
    # for tube
    tube_yarn_carrier_id = 2
    tube_pattern = f"all rs rounds k rib={rib_width}, p rib. all ws rounds slip rib, p rib."
    compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    knit_graph = compiler.compile(4, 5, object_type = 'tube', pattern = tube_pattern)

    knit_graph.gauge = 0.5
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    knit_graph.update_parent_offsets()
    KnitGraph_Visualizer = knitGraph_visualizer(knit_graph)
    KnitGraph_Visualizer.visualize()

    generator = Knitout_Generator(knit_graph)
    generator.write_instructions(f"slipped_rib_even.k")


def test_write_short_rows():
    # for sheet
    sheet_pattern = r"""
        1st row [k] to end.
        2nd row [p] to last 1 sts, slip 1.
        3rd row slip 1, [k] to last 1 sts, slip 1.
        4th row slip 1, [p] to last 2 sts, slip 2.
        5th row slip 2, [k] to last 2 sts, slip 2.
        6th row slip 2, [p] to end.
        7th row [k] to end.
    """ #[5, 7] or [8, 7]

    # sheet_pattern = r"""
    #     1st row [k] to end.
    #     2nd row [p] to last 1 sts, slip 1.
    #     3rd row slip 1, [k] to end.
    #     4th row [p] to end.
    # """ #get short row figure for paper, [3, 4].

    # sheet_pattern = r"""
    #     1st row [k] to end.
    #     2nd row [p] to last 1 sts, slip 1.
    # """ # size = [3,2]

    sheet_yarn_carrier_id = 4
    compiler = Knitspeak_Compiler(carrier_id = sheet_yarn_carrier_id)
    knit_graph = compiler.compile(5, 7, object_type = 'sheet', pattern = sheet_pattern)

    # for tube
    # tube_pattern = r"""
    #     1st round [k] to end.
    #     2nd round [p] to last 1 sts, slip 1.
    #     3rd round slip 1, [k] to last 1 sts, slip 1.
    #     4th round slip 1, [p] to last 2 sts, slip 2.
    #     5th round slip 2, [k] to last 2 sts, slip 2.
    #     6th round slip 2, [p] to end.
    #     7th round [k] to end.
    # """
    # tube_yarn_carrier_id = 3
    # compiler = Knitspeak_Compiler(carrier_id = tube_yarn_carrier_id)
    # knit_graph = compiler.compile(8, 7, object_type = 'tube', pattern = tube_pattern)

    knit_graph.gauge = 1/3
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_wales() 
    node_to_course_and_wale = knit_graph.get_node_course_and_wale()
    node_on_front_or_back = knit_graph.get_node_bed()
    course_and_wale_and_bed_to_node = knit_graph.get_course_and_wale_and_bed_to_node()
    knit_graph.update_parent_offsets()
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
