"""Script used to create knitout instructions from a knitgraph"""
from turtle import position
from typing import Dict, List, Optional, Tuple
from debugging_tools.new_knit_graph_viz import visualize_knitGraph
from knit_graphs.Knit_Graph import Knit_Graph, Pull_Direction
from knitting_machine.Machine_State import Machine_State, Needle, Pass_Direction, Yarn_Carrier
from knitting_machine.machine_operations import outhook
from knitting_machine.new_operation_sets import Carriage_Pass, Instruction_Type, Instruction_Parameters


class Knitout_Generator:
    """
    A class that is used to generate a single yarn knit-graph
    """

    def __init__(self, knit_graph: Knit_Graph, object_type:str, node_to_course_and_wale: Dict[int, Tuple[int,int]], course_and_wale_to_node: Dict[Tuple[int,int], int], \
            node_on_front_or_back: Dict[int, str], node_to_course_and_wale_and_bed: Optional[Dict[int, Tuple[Tuple[int, int], str]]] = None, \
            course_and_wale_and_bed_to_node: Optional[Dict[Tuple[Tuple[int, int], str], int]] = None):
        """
        :param knit_graph: the knitgraph used to generate instructions 
        :param node_to_course_and_wale_and_bed: only applicable to tube 
        :param course_and_wale_and_bed_to_node: only applicable to tube 
        """
        self._knit_graph = knit_graph
        self.object_type: str = object_type
        self._carrier_set = [yarn.carrier for yarn in [*self._knit_graph.yarns.values()]]
        # print('self._carrier_set', self._carrier_set, type(self._carrier_set))
        self.yarns = [*self._knit_graph.yarns.values()]
        # 
        loop_id_to_course, courses_to_loop_ids = self._knit_graph.get_courses()
        print(f'courses_to_loop_ids in knitgraph to knitout is {courses_to_loop_ids} ')
        self._loop_id_to_courses: Dict[int, float] = loop_id_to_course
        self._courses_to_loop_ids: Dict[float, List[int]] = courses_to_loop_ids
        # below params are needed for both tube and sheet
        self.node_to_course_and_wale: Dict[int, Tuple[int, int]] = node_to_course_and_wale
        self.course_and_wale_to_node: Dict[Tuple[int,int], int] = course_and_wale_to_node
        self.node_on_front_or_back = node_on_front_or_back
        # below params are only needed for tube
        self.node_to_course_and_wale_and_bed = node_to_course_and_wale_and_bed
        print(f'self.node_to_course_and_wale_and_bed in knitout is {self.node_to_course_and_wale_and_bed}')
        self.course_and_wale_and_bed_to_node = course_and_wale_and_bed_to_node
        # get the min wale and max wale of the whole knitgraph, which is used for guiding cast-on of new yarns
        print(f'self.node_to_course_and_wale in knitout is {self.node_to_course_and_wale}')
        self.min_wale = min(self.node_to_course_and_wale.values(), key=lambda x: x[1])[1]
        self.max_wale = max(self.node_to_course_and_wale.values(), key=lambda x: x[1])[1]
        # 
        self.loop_id_to_carrier_id: Dict[int, int] = {}
        self.loop_id_to_carrier: Dict[int, Yarn_Carrier] = {}
        self.first_course_in_to_carrier: Dict[int, List[Yarn_Carrier]] = {}
        self.get_nodes_carrier_id()
        self.get_first_course_id_of_yarns_in()
        # 
        self.loop_id_to_knit_dir :Dict[int, str] = {}
        self.carrier_to_first_dir: Dict[Yarn_Carrier, str] = {}
        self.get_min_and_max_wale_id_on_course_on_bed()
        self.get_loop_id_to_knit_dir()
        self.get_carrier_to_first_dir()
        # 
        self._sorted_courses = sorted([*self._courses_to_loop_ids.keys()])
        self._machine_state: Machine_State = Machine_State()
        self._carriage_passes: List[Carriage_Pass] = []
        self._instructions: List[str] = []
        self.nodes_on_patch_side: List[int] = []
        # since node 0 and 1 are loops on the first course, and in our setting, the input knitgraphs do not allow for loops lacking on first course
        # self.wale_dist is 1/gauge
        self.wale_dist: float = node_to_course_and_wale[1][1] - node_to_course_and_wale[0][1]
            
    #get node carrier_id
    def get_nodes_carrier_id(self):
        for node in self._knit_graph.graph.nodes:
            #find carrier_id of the node
            #first identify the yarn of the node
            for yarn in self.yarns:
                if node in yarn:
                    carrier = yarn.carrier
                    carrier_id = yarn.carrier.carrier_ids
                    break
            #store node color property
            self.loop_id_to_carrier_id[node] = carrier_id
            self.loop_id_to_carrier[node] = carrier
        # print('self.loop_id_to_carrier_id', self.loop_id_to_carrier_id)
    
    def get_first_course_id_of_yarns_in(self):
        for yarn in self.yarns:
            yarn_nodes = yarn.yarn_graph.nodes
            first_yarn_node = min(yarn_nodes)
            course_id = self.node_to_course_and_wale[first_yarn_node][0]
            carrier = yarn.carrier
            if course_id not in self.first_course_in_to_carrier:
                self.first_course_in_to_carrier[course_id] = [carrier]
            else:
                self.first_course_in_to_carrier[course_id].append(carrier)
        print('self.first_course_in_to_carrier', self.first_course_in_to_carrier)

    # only needed for tube
    def get_min_and_max_wale_id_on_course_on_bed(self):
        self.courses_to_min_wale_on_front: Dict[int, int] = {}
        self.courses_to_min_wale_on_back: Dict[int, int] = {}
        self.courses_to_max_wale_on_front: Dict[int, int] = {}
        self.courses_to_max_wale_on_back: Dict[int, int] = {}
        if self.object_type == 'tube':
            for course_id, loop_ids in self._courses_to_loop_ids.items():
                max_wale_on_front = -10000
                min_wale_on_front = 10000
                max_wale_on_back = -10000
                min_wale_on_back = 10000
                for loop in loop_ids:
                    if self.node_on_front_or_back[loop] == 'f':
                        wale_id = self.node_to_course_and_wale_and_bed[loop][1]
                        if wale_id > max_wale_on_front:
                            max_wale_on_front = wale_id
                        if wale_id < min_wale_on_front:
                            min_wale_on_front = wale_id
                for loop in loop_ids:
                    if self.node_on_front_or_back[loop] == 'f':
                        wale_id = self.node_to_course_and_wale_and_bed[loop][1]
                        if wale_id > max_wale_on_back:
                            max_wale_on_back = wale_id
                        if wale_id < min_wale_on_back:
                            min_wale_on_back = wale_id
                self.courses_to_min_wale_on_front[course_id] = min_wale_on_front
                self.courses_to_max_wale_on_front[course_id] = max_wale_on_front
                self.courses_to_min_wale_on_back[course_id] = min_wale_on_back
                self.courses_to_max_wale_on_back[course_id] = max_wale_on_back

    # only needed for tube 
    def get_loop_id_to_knit_dir(self):
        if self.object_type == 'tube':
            for yarn in self.yarns:
                if len(yarn.yarn_graph.nodes) > 1: # that means this yarn will have at least one yarn edge.
                    for edges in yarn.yarn_graph.edges:
                        prior_loop = edges[0]
                        next_loop = edges[1]
                        current_bed = self.node_on_front_or_back[prior_loop]
                        current_wale_id = self.node_to_course_and_wale_and_bed[prior_loop][1]
                        next_bed = self.node_on_front_or_back[next_loop]
                        next_wale_id = self.node_to_course_and_wale_and_bed[next_loop][1]
                        prior_loop_course_id = self._loop_id_to_courses[prior_loop]
                        if next_bed == current_bed:
                            if next_wale_id - current_wale_id > 0:
                                dir = '+'
                                if prior_loop not in self.loop_id_to_knit_dir.keys():
                                    self.loop_id_to_knit_dir[prior_loop] = dir
                                self.loop_id_to_knit_dir[next_loop] = dir
                            else:
                                dir = '-'
                                if prior_loop not in self.loop_id_to_knit_dir.keys():
                                    self.loop_id_to_knit_dir[prior_loop] = dir
                                self.loop_id_to_knit_dir[next_loop] = dir
                        elif next_bed != current_bed:
                            if prior_loop in self.loop_id_to_knit_dir.keys():
                                dir = self.loop_id_to_knit_dir[prior_loop]
                                dir = '+' if dir == '-' else '-'
                                self.loop_id_to_knit_dir[next_loop] = dir
                            else: 
                                if self.node_on_front_or_back[prior_loop] == 'f' and self.node_to_course_and_wale_and_bed[prior_loop][1] == self.courses_to_max_wale_on_front[prior_loop_course_id] \
                                    or self.node_on_front_or_back[prior_loop] == 'b' and self.node_to_course_and_wale_and_bed[prior_loop][1] == self.courses_to_min_wale_on_back[prior_loop_course_id]:
                                    dir = '+'
                                    self.loop_id_to_knit_dir[prior_loop] = dir
                                    self.loop_id_to_knit_dir[next_loop] = dir
                                elif self.node_on_front_or_back[prior_loop] == 'b' and self.node_to_course_and_wale_and_bed[prior_loop][1] == self.courses_to_max_wale_on_back[prior_loop_course_id] \
                                    or self.node_on_front_or_back[prior_loop] == 'f' and self.node_to_course_and_wale_and_bed[prior_loop][1] == self.courses_to_min_wale_on_front[prior_loop_course_id]:
                                    dir = '-'
                                    self.loop_id_to_knit_dir[prior_loop] = dir
                                    self.loop_id_to_knit_dir[next_loop] = dir
            else:
                dir = '-' #(the direction that the carrier first comes in)
        elif self.object_type == 'sheet':
            for yarn in self.yarns:
                if len(yarn.yarn_graph.nodes) > 1: # that means this yarn will have at least one yarn edge.
                    for edges in yarn.yarn_graph.edges:
                        prior_loop = edges[0]
                        next_loop = edges[1]
                        current_wale_id = self.node_to_course_and_wale[prior_loop][1]
                        next_wale_id = self.node_to_course_and_wale[next_loop][1]
                        if next_wale_id - current_wale_id > 0:
                            dir = '+'
                            if prior_loop not in self.loop_id_to_knit_dir.keys():
                                self.loop_id_to_knit_dir[prior_loop] = dir
                            self.loop_id_to_knit_dir[next_loop] = dir
                
                        
                        elif next_wale_id - current_wale_id < 0:
                            dir = '-'
                            if prior_loop not in self.loop_id_to_knit_dir.keys():
                                self.loop_id_to_knit_dir[prior_loop] = dir
                            self.loop_id_to_knit_dir[next_loop] = dir
         
                        
                        elif next_wale_id - current_wale_id == 0:
                            if prior_loop in self.loop_id_to_knit_dir.keys():
                                dir = self.loop_id_to_knit_dir[prior_loop]
                                dir = '+' if dir == '-' else '-'
                                self.loop_id_to_knit_dir[next_loop] = dir
                        
                else:
                    dir = '-' #(the direction that the carrier first comes in)
        print(f'self.loop_id_to_knit_dir is {self.loop_id_to_knit_dir}')


    def get_carrier_to_first_dir(self):
        for yarn in self.yarns:
            yarn_nodes = yarn.yarn_graph.nodes
            carrier = yarn.carrier
            first_yarn_node = min(yarn_nodes)
            first_dir =  self.loop_id_to_knit_dir[first_yarn_node]
            self.carrier_to_first_dir[carrier] = first_dir
        print(f'self.carrier_to_first_dir is {self.carrier_to_first_dir}')

    def generate_instructions(self):
        """
        Generates the instructions for this knitgraph
        """
        self._add_header()
        # get carrier to use for the very first course loops
        carriers = self.first_course_in_to_carrier[0]
        for carrier in carriers:
            self._cast_on(carrier, 0)
        if self.object_type == 'sheet':
            assert self._machine_state.last_carriage_direction is Pass_Direction.Left_to_Right
        elif self.object_type == 'tube':
            assert self._machine_state.last_carriage_direction is Pass_Direction.Right_to_Left
        # change from "pass_direction = self._machine_state.last_carriage_direction.opposite()"
        prev_pass_direction = self._machine_state.last_carriage_direction
        current_direction = prev_pass_direction.opposite()
        for course in self._sorted_courses:
            # bring in new yarns in the order they are used
            if course > 0:  # not cast on
                if course in self.first_course_in_to_carrier.keys():
                    carriers = self.first_course_in_to_carrier[course]
                    # 
                    if self.object_type == 'sheet':
                        if self.node_to_course_and_wale[self._courses_to_loop_ids[course][0]][1] < self.node_to_course_and_wale[self._courses_to_loop_ids[course][-1]][1]:
                            real_direction = Pass_Direction.Left_to_Right
                        else: 
                            real_direction = Pass_Direction.Right_to_Left
                    # for tube case, we need to identify the nodes on that introduced new yarn, and also need to identify the initial walking direction of this yarn,
                    # which finally can used to guide cast-on.
                    # elif self.object_type == 'tube':

                    for carrier in carriers:
                        self._cast_on(carrier, real_direction)
                    # print(f'course number to cast on is {course}, pass direction for tuck is {real_direction}, course loops is {self._courses_to_loop_ids[course]}')
                course_loops = self._courses_to_loop_ids[course]
                current_direction = self._knit_and_split_row(course_loops, current_direction, course)
                # pass_direction = pass_direction.opposite() #move inside _knit_and_split_row()
        for carrier in self._carrier_set:
            self._instructions.append(outhook(self._machine_state, carrier))
        self._drop_loops()

    def _knit_and_split_row(self, loop_ids: List[int], direction: Pass_Direction, course_number: int):
        """
        Adds the knit instructions for the given loop ids.
        Transfers to make these loops are also executed
        :param loop_ids: the loop ids of a single course
        :param direction: the direction that the loops will be knit in
        :param course_number: the course identifier for comments only
        """
        loop_id_to_target_needle, split_offsets, bind_off_loops = self._do_xfers_for_row(loop_ids, direction)
        knit_and_split_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        knit_and_split_data_on_front: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        knit_and_split_data_on_back: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        is_bind_off = False #move inside
        if self.object_type == 'sheet':
            for loop_id, target_needle in loop_id_to_target_needle.items():
                # print(f'loop_id is {loop_id}, bind_off_loops is {bind_off_loops}, {loop_id in bind_off_loops}')
                # is_bind_off = False
                if (loop_id in bind_off_loops) == True:
                    is_bind_off = True            
                carrier = self.loop_id_to_carrier[loop_id]
                if loop_id in split_offsets:
                    offset = split_offsets[loop_id]
                    split_needle = target_needle.offset(offset).opposite()
                    knit_and_split_data[target_needle] = (Instruction_Parameters(target_needle, involved_loop=loop_id, needle_2 = split_needle, carrier=carrier), Instruction_Type.Split)
                else:
                    knit_and_split_data[target_needle] = (Instruction_Parameters(target_needle, involved_loop=loop_id, carrier=carrier), Instruction_Type.Knit)
            if is_bind_off == False:
                current_direction = direction
            else:
                current_direction = direction.opposite()
            # print(f'course number is {course_number}, loop_id_to_target_needle is {loop_id_to_target_needle}, pass direction for this knit is {current_direction}')
            carriage_pass = Carriage_Pass(current_direction, knit_and_split_data, self._machine_state)
            # print('knit_and_split_data', knit_and_split_data)
            self._add_carriage_pass(carriage_pass, f"Knit & Split course {course_number}")
            # self._add_carriage_pass(carriage_pass)
            # the param in cast_on() should be next carriage pass direction, not the current direction.
            next_direction = current_direction.opposite()
            return next_direction
        elif self.object_type == 'tube':
            is_bind_off = False
            for loop_id, target_needle in loop_id_to_target_needle.items():
                # print(f'loop_id is {loop_id}, bind_off_loops is {bind_off_loops}, {loop_id in bind_off_loops}')
                if (loop_id in bind_off_loops) == True:
                    is_bind_off = True  
                carrier = self.loop_id_to_carrier[loop_id] 
                knit_and_split_data[target_needle] = (Instruction_Parameters(target_needle, involved_loop=loop_id, carrier=carrier), Instruction_Type.Knit)
            if is_bind_off == True:
                carriage_pass = Carriage_Pass(self._machine_state.last_carriage_direction, knit_and_split_data, self._machine_state)
            else:
                carriage_pass = Carriage_Pass(None, knit_and_split_data, self._machine_state)
            self._add_carriage_pass(carriage_pass, f"Knit & Split course {course_number}")
            return None
        
    def _cast_on(self, carrier:Yarn_Carrier, pass_direction: Optional[Pass_Direction] = None):
        """
        Does a standard alternating tuck cast on then 2 stabilizing knit rows
        """
        first_course_loops = self._courses_to_loop_ids[self._sorted_courses[0]]
        first_carrier_in_use = self._carrier_set[0]
        needles_to_tuck_on: List[int] = []
        if self.object_type == 'sheet':
            reverse_knits: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
            first_knit: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
            if carrier == first_carrier_in_use:
                self._machine_state.last_carriage_direction = Pass_Direction.Left_to_Right
                for loop in first_course_loops:
                    needle_pos = self.node_to_course_and_wale[loop][1]
                    needles_to_tuck_on.append(needle_pos)
            elif carrier != first_carrier_in_use:
                # for other carriers, tuck on needles on the side to avoid messing the designed pattern, but note that tuck on which side is determined by the pass direction,
                # if ignore this, introducing a new yarn could fail
                if self.carrier_to_first_dir[carrier] == '-':
                    needles_to_tuck_on = [*range(self.max_wale, self.max_wale+15)]
                elif self.carrier_to_first_dir[carrier] == '+':
                    needles_to_tuck_on = [*range(self.min_wale-15, self.min_wale - 5)]
            first_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
            second_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
            first_tuck_needles = needles_to_tuck_on[::-2]
            second_tuck_needles = list(set(needles_to_tuck_on) - set(first_tuck_needles))
            for needle_pos in first_tuck_needles:
                needle_1 = Needle(True, needle_pos)
                first_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
            for needle_pos in second_tuck_needles:
                needle_1 = Needle(True, needle_pos)   
                second_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
            first_pass = Carriage_Pass(Pass_Direction.Right_to_Left, first_tucks_data,
                                    self._machine_state)
            self._add_carriage_pass(first_pass, f"first pass for cast-on for {carrier}")
            second_pass = Carriage_Pass(Pass_Direction.Left_to_Right, second_tucks_data,
                                    self._machine_state)
            self._add_carriage_pass(second_pass, f"second pass for cast-on for {carrier}")
            # 
            reverse_knits: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
            first_knit: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {} 
            for needle_pos, loop_id in zip(needles_to_tuck_on, first_course_loops):
                needle_1 = Needle(True, needle_pos)
                reverse_knits[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Knit)   # note, fake loop_id
                first_knit[needle_1] = (Instruction_Parameters(needle_1, involved_loop=loop_id, carrier=carrier), Instruction_Type.Knit)  
            carriage_pass = Carriage_Pass(Pass_Direction.Right_to_Left, reverse_knits, self._machine_state)
            self._add_carriage_pass(carriage_pass, f"stabilize cast-on for {carrier}")
            carriage_pass = Carriage_Pass(Pass_Direction.Left_to_Right, first_knit, self._machine_state)
            self._add_carriage_pass(carriage_pass, f"first row loops right after cast-on stabilization for {carrier}")
        elif self.object_type == 'tube':
            # first get the gauging info for first course of loops on the front bed and that on the back bed
            back_bed_needles_to_tuck_on = []
            first_course_back_loops = []
            front_bed_needles_to_tuck_on = []
            first_course_front_loops = []
            for loop_id in first_course_loops:
                needle_pos = self.node_to_course_and_wale[loop_id][1]
                bed = self.node_on_front_or_back[loop_id]
                if bed == 'b':
                    back_bed_needles_to_tuck_on.append(needle_pos)
                    first_course_back_loops.append(loop_id)
                elif bed == 'f':
                    front_bed_needles_to_tuck_on.append(needle_pos)
                    first_course_front_loops.append(loop_id)
            if carrier == first_carrier_in_use:
                self._machine_state.last_carriage_direction = Pass_Direction.Right_to_Left
                needles_to_tuck_on_front_bed_first = front_bed_needles_to_tuck_on[::2]
                needles_to_tuck_on_front_bed_second = list(set(front_bed_needles_to_tuck_on) - set(needles_to_tuck_on_front_bed_first))
                needles_to_tuck_on_back_bed_first = back_bed_needles_to_tuck_on[::2]
                needles_to_tuck_on_back_bed_second = list(set(back_bed_needles_to_tuck_on) - set(needles_to_tuck_on_back_bed_first))
                print(f'needles_to_tuck_on_front_bed_first is {needles_to_tuck_on_front_bed_first}, needles_to_tuck_on_front_bed_second is {needles_to_tuck_on_front_bed_second}\
                    , needles_to_tuck_on_back_bed_first is {needles_to_tuck_on_back_bed_first}, needles_to_tuck_on_back_bed_second is {needles_to_tuck_on_back_bed_second}')
                first_front_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                first_back_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                second_front_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                second_back_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                for needle_pos in needles_to_tuck_on_front_bed_first:
                    needle_1 = Needle(True, needle_pos)
                    first_front_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                for needle_pos in needles_to_tuck_on_back_bed_first:
                    needle_1 = Needle(False, needle_pos)
                    first_back_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                for needle_pos in needles_to_tuck_on_front_bed_second:
                    needle_1 = Needle(True, needle_pos)
                    second_front_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                for needle_pos in needles_to_tuck_on_back_bed_second:
                    needle_1 = Needle(False, needle_pos)
                    second_back_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                first_pass_front = Carriage_Pass(Pass_Direction.Left_to_Right, first_front_tucks_data, self._machine_state)
                self._add_carriage_pass(first_pass_front, f"first front cast-on for {carrier}")
                first_pass_back = Carriage_Pass(Pass_Direction.Right_to_Left, first_back_tucks_data, self._machine_state)
                self._add_carriage_pass(first_pass_back, f"first back cast-on for {carrier}")
                second_pass_front = Carriage_Pass(Pass_Direction.Left_to_Right, second_front_tucks_data, self._machine_state)
                self._add_carriage_pass(second_pass_front, f"second front cast-on for {carrier}")
                second_pass_back = Carriage_Pass(Pass_Direction.Right_to_Left, second_back_tucks_data, self._machine_state)
                self._add_carriage_pass(second_pass_back, f"second back cast-on for {carrier}")
                # 
                first_all_front: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                first_all_back: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                for needle_pos, loop_id in zip(front_bed_needles_to_tuck_on, first_course_front_loops):
                    needle_1 = Needle(True, needle_pos)
                    first_all_front[needle_1] = (Instruction_Parameters(needle_1, involved_loop=loop_id, carrier=carrier), Instruction_Type.Knit)  
                for needle_pos, loop_id in zip(back_bed_needles_to_tuck_on, first_course_back_loops):
                    needle_1 = Needle(False, needle_pos)
                    first_all_back[needle_1] = (Instruction_Parameters(needle_1, involved_loop=loop_id, carrier=carrier), Instruction_Type.Knit)  
                carriage_pass = Carriage_Pass(Pass_Direction.Left_to_Right, first_all_front, self._machine_state)
                self._add_carriage_pass(carriage_pass, f"first row loops on front bed for for {carrier}")
                carriage_pass = Carriage_Pass(Pass_Direction.Right_to_Left, first_all_back, self._machine_state)
                self._add_carriage_pass(carriage_pass, f"first row loops on back bed for {carrier}")
            elif carrier != first_carrier_in_use:
                # for other carriers, tuck on needles on the side to avoid messing the designed pattern, but note that tuck on which side is determined by the pass direction,
                # if ignore this, introducing a new yarn could fail
                # different from sheet, for tube, for a course there can be two opposite yarn walking direction, which makes pass_direction useless here, thus we introduce
                # two functions above to get the knitting direction of both each loop and each new yarn, which is 
                # stored in self.carrier_to_first_knit_dir to decide the position in "needles_to_tuck_on".
                first_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                if self.carrier_to_first_dir[carrier] == '-':
                    needles_to_tuck_on = [*range(self.max_wale, self.max_wale+15)]
                    first_tuck_needles = needles_to_tuck_on[::-2]
                    second_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                    second_tuck_needles = list(set(needles_to_tuck_on) - set(first_tuck_needles))
                    for needle_pos in first_tuck_needles:
                        needle_1 = Needle(True, needle_pos)
                        first_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                    for needle_pos in second_tuck_needles:
                        needle_1 = Needle(True, needle_pos)   
                        second_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                    first_pass = Carriage_Pass(Pass_Direction.Right_to_Left, first_tucks_data,
                                        self._machine_state)
                    self._add_carriage_pass(first_pass, f"first pass for cast-on for {carrier}")
                    second_pass = Carriage_Pass(Pass_Direction.Left_to_Right, second_tucks_data,
                                            self._machine_state)
                    self._add_carriage_pass(second_pass, f"second pass for cast-on for {carrier}")
                    reverse_knits: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                    first_knit: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {} 
                    for needle_pos, loop_id in zip(needles_to_tuck_on, first_course_loops):
                        needle_1 = Needle(True, needle_pos)
                        reverse_knits[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Knit)   # note, fake loop_id
                        first_knit[needle_1] = (Instruction_Parameters(needle_1, involved_loop=loop_id, carrier=carrier), Instruction_Type.Knit)  
                    carriage_pass = Carriage_Pass(Pass_Direction.Right_to_Left, reverse_knits, self._machine_state)
                    self._add_carriage_pass(carriage_pass, f"stabilize cast-on for {carrier}")
                    carriage_pass = Carriage_Pass(Pass_Direction.Left_to_Right, first_knit, self._machine_state)
                    self._add_carriage_pass(carriage_pass, f"first row loops right after cast-on stabilization for {carrier}")
                elif self.carrier_to_first_dir[carrier] == '+':
                    needles_to_tuck_on = [*range(self.min_wale-15, self.min_wale - 5)]
                    first_tuck_needles = needles_to_tuck_on[::2]
                    second_tucks_data: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                    second_tuck_needles = list(set(needles_to_tuck_on) - set(first_tuck_needles))
                    for needle_pos in first_tuck_needles:
                        needle_1 = Needle(True, needle_pos)
                        first_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                    for needle_pos in second_tuck_needles:
                        needle_1 = Needle(True, needle_pos)   
                        second_tucks_data[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Tuck)  # note, fake loop_id
                    first_pass = Carriage_Pass(Pass_Direction.Left_to_Right, first_tucks_data,
                                        self._machine_state)
                    self._add_carriage_pass(first_pass, f"first pass for cast-on for {carrier}")
                    second_pass = Carriage_Pass(Pass_Direction.Right_to_Left, second_tucks_data,
                                            self._machine_state)
                    self._add_carriage_pass(second_pass, f"second pass for cast-on for {carrier}")
                    reverse_knits: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
                    first_knit: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {} 
                    for needle_pos, loop_id in zip(needles_to_tuck_on, first_course_loops):
                        needle_1 = Needle(True, needle_pos)
                        reverse_knits[needle_1] = (Instruction_Parameters(needle_1, involved_loop=-1, carrier=carrier), Instruction_Type.Knit)   # note, fake loop_id
                        first_knit[needle_1] = (Instruction_Parameters(needle_1, involved_loop=loop_id, carrier=carrier), Instruction_Type.Knit)  
                    carriage_pass = Carriage_Pass(Pass_Direction.Left_to_Right, reverse_knits, self._machine_state)
                    self._add_carriage_pass(carriage_pass, f"stabilize cast-on for {carrier}")
                    carriage_pass = Carriage_Pass(Pass_Direction.Right_to_Left, first_knit, self._machine_state)
                    self._add_carriage_pass(carriage_pass, f"first row loops right after cast-on stabilization for {carrier}")

    def _drop_loops(self):
        """
        Drops all loops off the machine
        """
        drops: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        second_drops: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        # for needle_pos in range(0, self._machine_state.needle_count):
        for needle_pos in range(int(-self._machine_state.needle_count/2), int(self._machine_state.needle_count/2)):
            front_needle = Needle(is_front=True, position=needle_pos)
            back_needle = Needle(is_front=False, position=needle_pos)
            dropped_front = False
            if len(self._machine_state[front_needle]) > 0:  # drop on loops on front
                drops[front_needle] = (Instruction_Parameters(front_needle), Instruction_Type.Drop)
                dropped_front = True
            if len(self._machine_state[back_needle]) > 0:
                if dropped_front:
                    second_drops[back_needle] = (Instruction_Parameters(back_needle), Instruction_Type.Drop)
                else:
                    # drops[back_needle] = (Instruction_Parameters(front_needle), Instruction_Type.Drop)
                    drops[back_needle] = (Instruction_Parameters(back_needle), Instruction_Type.Drop)
        # print(f'drops is {drops}, second_drops is {second_drops}')
        carriage_pass = Carriage_Pass(None, drops, self._machine_state)
        self._add_carriage_pass(carriage_pass, "Drop KnitGraph")
        # self._add_carriage_pass(carriage_pass)
        carriage_pass = Carriage_Pass(None, second_drops, self._machine_state)
        self._add_carriage_pass(carriage_pass)

    def _do_xfers_for_row(self, loop_ids: List[int], direction: Pass_Direction) -> Dict[int, Needle]:
        """
        Completes all the xfers needed to prepare a row
        :param loop_ids: the loop ids of a single course
        :param direction: the direction that the loops will be knit in
        :return:
        """
        loop_id_to_target_needle, parent_loops_to_needles, lace_offsets, front_cable_offsets, back_cable_offsets, split_offsets, split_parents, bind_off_loops \
            = self._find_target_needles(loop_ids, direction)
        self._do_decrease_transfers(parent_loops_to_needles, lace_offsets)
        self._do_cable_transfers(parent_loops_to_needles, front_cable_offsets, back_cable_offsets)
        self._do_knit_purl_xfers(loop_id_to_target_needle, split_parents)
        # after performing xfers above as needed, to avoid the Error Message "with the command to pass the yarn end between yarn holding hook and yarn inserting hook [R10, 15],
        # set the racking 0.5 pitch or 1/4 pitch for left.", we need to add "rack 0;" to return the back bed to zero position.
        if self._machine_state.racking != 0:
            carriage_pass = Carriage_Pass(None, {}, self._machine_state, only_racking = True)
            self._add_carriage_pass(carriage_pass, "Rack to return back bed home")
        return loop_id_to_target_needle, split_offsets, bind_off_loops

    def _find_target_needles(self, loop_ids: List[int], direction: Pass_Direction) -> \
            Tuple[Dict[int, Needle], Dict[int, Needle], Dict[int, int], Dict[int, int], Dict[int, int], Dict[int, int], List[int], List[int]]:
        """
        Finds target needle information needed to do transfers
        :param loop_ids: the loop ids of a single course
        :param direction: the direction that the loops will be knit in
        :return: Loops mapped to target needles to be knit on,
        parent loops mapped to current needles,
        parent loops mapped to their offsets in a decrease
        parent loops mapped to their offsets in the front of cables
        parent loops mapped to their offsets in the back of cables
        """
        parent_loops_to_needles: Dict[int, Needle] = {}  # key loop_ids to the needle they are currently on
        loop_id_to_target_needle: Dict[int, Needle] = {}  # key loop_ids to the needle they need to be on to knit
        parents_to_offsets: Dict[int, int] = {}  # key parent loop_ids to their offset from their child
        # .... i.e., self._knit_graph.graph[parent_id][loop_id]["parent_offset"]
        front_cable_offsets: Dict[int, int] = {}  # key parent loop_id to the offset to their child
        # .... only include loops that cross in front. i.e., self._knit_graph.graph[parent_id][loop_id]["depth"] > 0
        back_cable_offsets: Dict[int, int] = {}  # key parent loop_id to the offset to their child
        # .... only include loops that cross in back. i.e., self._knit_graph.graph[parent_id][loop_id]["depth"] < 0
        decrease_offsets: Dict[int, int] = {}  # key parent loop_id to the offset to their child
        # .... only includes parents involved in a decrease
        split_offsets: Dict[int, int] = {}  # key parent loop_id to the offset to their child
        split_parents: List[int] = []
        # .... only includes parents involved in a split
        bind_off_loops: List[int] = []
        # .... only includes parents involved in a split
        max_needle = len(loop_ids) - 1  # last needle being used to create this swatch
        for loop_pos, loop_id in enumerate(loop_ids):  # find target needle locations of each loop in the course
            print('loop_pos', loop_pos, loop_id)
            parent_ids = [*self._knit_graph.graph.predecessors(loop_id)]
            print(type(parent_ids),parent_ids)
            for parent_id in parent_ids:  # find current needle of all parent loops
                parent_needle = self._machine_state.get_needle_of_loop(parent_id)
                assert parent_needle is not None, f"Parent loop {parent_id} is not held on a needle"
                parent_loops_to_needles[parent_id] = parent_needle
            # detect split
            for parent_id in parent_ids:
                flag_for_FtB = False
                # get parent successors
                successors = [*self._knit_graph.graph.successors(parent_id)]
                if len(successors) > 1:
                    for successor in successors:
                        if self._knit_graph.graph[parent_id][successor]["pull_direction"] == Pull_Direction.FtB:
                            flag_for_FtB  = True
                if flag_for_FtB == True and self._knit_graph.graph[parent_id][loop_id]["pull_direction"] == Pull_Direction.BtF:
                    # or len(self._knit_graph.graph.in_edges(loop_id))
                    assert len(parent_ids) == 1, f'knitgraph is wrong'
                    assert len(successors) == 2, f'split would fail'
                    pull_direction = self._knit_graph.graph[parent_id][loop_id]["pull_direction"]
                    front_bed = pull_direction is Pull_Direction.BtF
                    parent_needle = parent_loops_to_needles[parent_id]
                    parent_offset =  self._knit_graph.graph[parent_id][loop_id]["parent_offset"]
                    offset_needle = parent_needle.offset(parent_offset)
                    target_needle = Needle(is_front=front_bed, position=offset_needle.position)
                    loop_id_to_target_needle[loop_id] = target_needle
                    # 
                    the_other_successor = list(set(successors).difference(set([loop_id])))
                    # note that split_offset and parent_offset are different value
                    split_offset = self._knit_graph.graph[parent_id][the_other_successor[0]]["parent_offset"]
                    split_offsets[loop_id] = split_offset
                    # used to help detect loop id on patch side that can easily disguise as decrease stitch because has two parents too, see "detect decrease" below.
                    split_parents.append(parent_id)
            # detect yarn-over
            if len(parent_ids) == 0:  # yarn-over, yarn overs are made on front bed
                position = self.node_to_course_and_wale[loop_id][1]
                loop_id_to_target_needle[loop_id] = Needle(is_front=True, position=position)
            # detect cable
            elif len(parent_ids) == 1:  # knit, purl, may be in cable, no needle
                parent_id = [*parent_ids][0]
                # detect loop id on patch side that can easily disguise as decrease stitch because has two parents too (if we split two nodes to the same needle)
                if parent_id in split_parents or parent_id in self.nodes_on_patch_side:
                    self.nodes_on_patch_side.append(loop_id)
                parent_offset =  self._knit_graph.graph[parent_id][loop_id]["parent_offset"]
                pull_direction = self._knit_graph.graph[parent_id][loop_id]["pull_direction"]
                front_bed = pull_direction is Pull_Direction.BtF  # knit on front bed, purl on back bed
                parent_needle = parent_loops_to_needles[parent_id]
                offset_needle = parent_needle.offset(parent_offset)
                target_needle = Needle(is_front=front_bed, position=offset_needle.position)
                print('offset', parent_offset)
                print('target', target_needle)
                if parent_offset != 0 and parent_needle.is_front == target_needle.is_front:
                    cable_depth = self._knit_graph.graph[parent_id][loop_id]["depth"]
                    # update below to a warning rather than assertion, because for a decreased-tube, stitch on edge can disguise as cable stitch but the depth is 0, refer to
                    # pp. 219
                    # assert cable_depth != 0, f"cables must have a non-zero depth to cross at"
                    if cable_depth != 0:
                        if cable_depth == 1:
                            front_cable_offsets[parent_id] = parent_offset
                        else:
                            back_cable_offsets[parent_id] = parent_offset
                loop_id_to_target_needle[loop_id] = target_needle
                parents_to_offsets[parent_id] = parent_offset
            # detect decrease
            elif len(parent_ids) > 1: # decrease, the bottom parent loop in the stack  will be on the target needle
                if self.node_to_course_and_wale[parent_ids[0]][0] != self.node_to_course_and_wale[parent_ids[1]][0]:
                    bind_off_loops.append(loop_id) 
                flag_for_decrease = True
                loop = self._knit_graph.loops[loop_id]
                target_needle = None  # re-assigned on first iteration to needle of first parent
                # detect loop id on patch side that can easily disguise as decrease stitch because has two parents too
                for i, parent in enumerate(loop.parent_loops):
                    if parent.loop_id in split_parents:
                        flag_for_decrease = False 
                # for loop id on patch side 
                if flag_for_decrease == False:
                    self.nodes_on_patch_side.append(loop_id)
                    #randomly pick a parent id by parent_ids[0]
                    pull_direction = self._knit_graph.graph[parent_ids[0]][loop_id]["pull_direction"]
                    front_bed = pull_direction is Pull_Direction.BtF
                    parent_needle = parent_loops_to_needles[parent_ids[0]] 
                    parent_offset =  self._knit_graph.graph[parent_ids[0]][loop_id]["parent_offset"]
                    offset_needle = parent_needle.offset(parent_offset)
                    target_needle = Needle(is_front=front_bed, position=offset_needle.position)
                    loop_id_to_target_needle[loop_id] = target_needle
                    continue
                # for real decrease
                if flag_for_decrease == True:
                    for i, parent in enumerate(loop.parent_loops):
                        parent_needle = parent_loops_to_needles[parent.loop_id]
                        # if i == 0:  # first parent in stack
                        #     target_needle = parent_needle
                        pull_direction = self._knit_graph.graph[parent.loop_id][loop_id]["pull_direction"]
                        front_bed = pull_direction is Pull_Direction.BtF
                        offset = self._knit_graph.graph[parent.loop_id][loop_id]["parent_offset"]
                        if front_bed == True:
                            offset_needle = parent_needle.offset(offset)
                        elif front_bed == False:
                            offset_needle = parent_needle.offset(-offset)
                        target_needle = Needle(is_front=front_bed, position=offset_needle.position)
                        loop_id_to_target_needle[loop_id] = target_needle
                        break
                    for i, parent in enumerate(loop.parent_loops):
                        offset = self._knit_graph.graph[parent.loop_id][loop_id]["parent_offset"]
                        print(f'parent_offset is {offset}')
                        if offset != 0:
                            parents_to_offsets[parent.loop_id] = offset
                            if target_needle.is_front == True:
                                decrease_offsets[parent.loop_id] = offset
                            elif target_needle.is_front == False:
                                decrease_offsets[parent.loop_id] = -offset
            
        print('loop_id_to_target_needle', loop_id_to_target_needle)
        print('parent_loops_to_needles', parent_loops_to_needles)
        print('decrease_offsets', decrease_offsets)
        print('front_cable_offsets', front_cable_offsets)
        print('back_cable_offsets', back_cable_offsets)
        print('split_offsets', split_offsets)
        print('split_parents', split_parents)
        print('bind_off_loops', bind_off_loops)
        return loop_id_to_target_needle, parent_loops_to_needles, decrease_offsets, \
               front_cable_offsets, back_cable_offsets, split_offsets, split_parents, bind_off_loops
               
    def _do_cable_transfers(self, parent_loops_to_needles: Dict[int, Needle], front_cable_offsets: Dict[int, int],
                            back_cable_offsets: Dict[int, int]):
        """
        Transfer all parent loops to back bed
        For front_cables:
            in order of offsets (i.e., 1, 2, 3) transfer to front
        for back_cables
            in order of offsets transfer to back
        :param parent_loops_to_needles: the parent loops mapped to their current needles
        :param front_cable_offsets: parent loops mapped to their offsets for the front of cables
        :param back_cable_offsets: parent loops mapped to their offsets for the back of cables
        """
        xfers_to_back: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        front_cable_xfers: Dict[int, Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]]] = {}
        back_cable_xfers: Dict[int, Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]]] = {}
        for parent_loop, parent_needle in parent_loops_to_needles.items():
            front_needle = Needle(is_front=True, position=parent_needle.position)
            back_needle = parent_needle.opposite()
            if parent_needle.is_front and (parent_loop in front_cable_offsets or parent_loop in back_cable_offsets):
                xfers_to_back[front_needle] = (Instruction_Parameters(front_needle, needle_2=back_needle), Instruction_Type.Xfer)
            if parent_loop in front_cable_offsets:
                offset = front_cable_offsets[parent_loop]
                if offset not in front_cable_xfers:
                    front_cable_xfers[offset] = {}
                offset_needle = front_needle.offset(offset)
                front_cable_xfers[offset][back_needle] = (Instruction_Parameters(back_needle, needle_2=offset_needle), Instruction_Type.Xfer)
            elif parent_loop in back_cable_offsets:
                offset = back_cable_offsets[parent_loop]
                if offset not in back_cable_xfers:
                    back_cable_xfers[offset] = {}
                offset_needle = front_needle.offset(offset)
                back_cable_xfers[offset][back_needle] = (Instruction_Parameters(back_needle, needle_2=offset_needle), Instruction_Type.Xfer)
        carriage_pass = Carriage_Pass(None, xfers_to_back, self._machine_state)
        # print('xfer to back', xfers_to_back)
        self._add_carriage_pass(carriage_pass, "cables to back")
        for offset, xfer_params in front_cable_xfers.items():
            carriage_pass = Carriage_Pass(None, xfer_params, self._machine_state)
            self._add_carriage_pass(carriage_pass, f"front of cable at offset {offset} to front")
        for offset, xfer_params in back_cable_xfers.items():
            carriage_pass = Carriage_Pass(None, xfer_params, self._machine_state)
            self._add_carriage_pass(carriage_pass, f"back of cable at offset {offset} to front")

    def _do_decrease_transfers(self, parent_loops_to_needles: Dict[int, Needle], decrease_offsets: Dict[int, int]):
        """
        Based on the school bus algorithm.
         Transfer all loops in decrease to the opposite side
         Bring the loops back to their offset needle in the order of offsets from negative to positive offsets
        Note that we are restricting our decreases to be offsets of 1 or -1 due to limitations of the machine.
        This is not a completely general method and does not guarantee stacking order of our decreases
        A more advanced method can be found at:
        https://textiles-lab.github.io/posts/2018/02/07/lace-transfers/
        This would require some changes to the code structure and is not recommended for assignment 2.
        :param parent_loops_to_needles: parent loops mapped to their current needle
        :param decrease_offsets: the offsets of parent loops to create decreases
        """
        xfers_to_holding_bed: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        # key needles currently holding the loops to the opposite needle to hold them for offset-xfers
        offset_to_xfers_to_target: Dict[int, Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]]] = {}
        # key offset values (-N...0..N) to starting needles to their target needle
        for parent_id, parent_needle in parent_loops_to_needles.items():
            if parent_id in decrease_offsets:  # this loop is involved in a decrease
                offset = decrease_offsets[parent_id]
                offset_needle = parent_needle.offset(offset)
                holding_needle = parent_needle.opposite()
                xfers_to_holding_bed[parent_needle] = (Instruction_Parameters(parent_needle, needle_2=holding_needle), Instruction_Type.Xfer)
                if offset not in offset_to_xfers_to_target:
                    offset_to_xfers_to_target[offset] = {}
                offset_to_xfers_to_target[offset][holding_needle] = (Instruction_Parameters(holding_needle, needle_2=offset_needle), Instruction_Type.Xfer)

        carriage_pass = Carriage_Pass(None, xfers_to_holding_bed, self._machine_state)
        self._add_carriage_pass(carriage_pass, "send loops to decrease to back")
        # self._add_carriage_pass(carriage_pass)
        for offset in sorted(offset_to_xfers_to_target.keys()):
            offset_xfers = offset_to_xfers_to_target[offset]
            carriage_pass = Carriage_Pass(None, offset_xfers, self._machine_state)
            self._add_carriage_pass(carriage_pass, f"stack decreases with offset {offset}")
            # self._add_carriage_pass(carriage_pass)

    def _do_knit_purl_xfers(self, loop_id_to_target_needle: Dict[int, Needle], split_parents: Optional[List[int]]):
        """
        Transfers loops to bed needed for knit vs purl
        :param loop_id_to_target_needle: loops mapped to their target needles
        """
        xfers: Dict[Needle, Tuple[Instruction_Parameters, Instruction_Type]] = {}
        for loop_id, target_needle in loop_id_to_target_needle.items():
            opposite_needle = target_needle.opposite()
            loops_on_opposite = self._machine_state[opposite_needle]
            # print('loop_id', loop_id)
            # print('op_needle', opposite_needle)
            # print('loop_on_op', loops_on_opposite)
            # print('split_parents', split_parents)
            # print('self.nodes_on_patch_side', self.nodes_on_patch_side)
            flag_for_k_p_xfer = True
            if len(loops_on_opposite) > 0:
                if loop_id in self.nodes_on_patch_side or loops_on_opposite[0] in self.nodes_on_patch_side:
                    flag_for_k_p_xfer = False 
            if len(loops_on_opposite) > 0 and flag_for_k_p_xfer == True:  # something to transfer for knitting
                # print('inside kp')
                xfers[opposite_needle] = (Instruction_Parameters(opposite_needle, needle_2=target_needle), Instruction_Type.Xfer)
        carriage_pass = Carriage_Pass(None, xfers, self._machine_state)
        self._add_carriage_pass(carriage_pass, "kp-transfers")

    def _add_carriage_pass(self, carriage_pass: Carriage_Pass, first_comment="", comment=""):
        """
        Executes the carriage pass and adds it to the instructions
        :param carriage_pass: the carriage pass to be executed
        :param first_comment: a comment for the first instruction
        :param comment:  a comment for each instruction
        """
        if len(carriage_pass.needles_to_instruction_parameters_and_types) > 0 or carriage_pass.only_racking == True:
            self._carriage_passes.append(carriage_pass)
            self._instructions.extend(carriage_pass.write_instructions(first_comment, comment))

    def write_instructions(self, filename: str, generate_instructions: bool = True):
        """
        Writes the instructions from the generator to a knitout file
        :param filename: the name of the file including the suffix
        :param generate_instructions: True if the instructions still need to be generated
        """
        if generate_instructions:
            self.generate_instructions()
        with open(filename, "w") as file:
            file.writelines(self._instructions)

    def _add_header(self, position: str = "Center"):
        """
        Writes the header instructions for this knitgraph
        :param position: where to place the operations on the needle bed; Left, Center, Right,
         and Keep are standard values
        """
        self._instructions.extend([";!knitout-2\n",
                                   ";;Machine: SWG091N2\n",
                                   ";;Gauge: 5\n",
                                   ";;Width: 250\n",
                                   f";;Carriers: 1 2 3 4 5 6 7 8 9 10\n",
                                   f";;Position: {position}\n"])
