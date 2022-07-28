"""Compiler code for converting knitspeak AST to knitgraph"""
from typing import List, Dict, Union, Tuple, Optional, Set
import xxlimited

from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn
from knitspeak_compiler.knitspeak_interpreter.knitspeak_interpreter import KnitSpeak_Interpreter
from knitspeak_compiler.knitspeak_interpreter.cable_definitions import Cable_Definition
from knitspeak_compiler.knitspeak_interpreter.closures import Num_Closure, Iterator_Closure
from knitspeak_compiler.knitspeak_interpreter.stitch_definitions import Stitch_Definition


class Knitspeak_Compiler:
    """
    A class used to compile knit graphs from knitspeak
    """

    def __init__(self):
        # self._parser = KnitSpeak_Interpreter(True, True, True)
        self._parser = KnitSpeak_Interpreter()
        self.parse_results: List[Dict[str, Union[List[int, Num_Closure, Iterator_Closure], List[tuple]]]] = []
        self.course_ids_to_operations: Dict[int, List[tuple]] = {}
        self.knit_graph = Knit_Graph()
        self.yarn = Yarn("yarn", self.knit_graph, carrier_id = 3)
        self.knit_graph.add_yarn(self.yarn)
        self.last_course_loop_ids: List[int] = []
        self.last_course_loop_ids_left: List[int] = []
        self.last_course_loop_ids_right: List[int] = []
        self.cur_course_loop_ids: List[int] = []
        self.current_row = 0
        self.loop_ids_consumed_by_current_course: Set[int] = set()

    def _increment_current_row(self):
        """
        Increments the current row by 1 and manages its state in the symbol table
        """
        self.current_row += 1
        self._parser.parser.symbolTable["current_row"] = self.current_row

    @property
    def _working_ws(self) -> bool:
        """
        :return: true if currently compiling a wrong-side row
        """
        return self.current_row % 2 == 0

    def compile(self, starting_width: int, row_count: int, pattern: str, patternIsFile: bool = False) -> Knit_Graph:
        """
        Populates the knit_graph based on the compiled instructions. May throw errors from compilation
        :param row_count: the number of rows to knit before completing, pattern may repeat or be incomplete
        :param starting_width: the number of loops used to create the 0th course
        :param pattern: the pattern as a string or in a file
        :param patternIsFile: True if pattern is provided in a file
        :return: the resulting compiled knit graph
        """
        self.parse_results = self._parser.interpret(pattern, patternIsFile)
        self._organize_courses()
        self.populate_0th_course(starting_width)
        num_operation_courses = len(self.course_ids_to_operations)
        # self.course_to_action_queues(starting_width)
        while self.current_row < row_count:
            for course_id in sorted(self.course_ids_to_operations):
                self._increment_current_row()
                if self.current_row > num_operation_courses:
                    count = int((self.current_row-1)/num_operation_courses)
                    assert self.current_row % (course_id + count * num_operation_courses) == 0
                else: 
                    assert self.current_row % course_id  == 0
                course_instructions = self.course_ids_to_operations[course_id]
                while len(self.loop_ids_consumed_by_current_course) < len(self.last_course_loop_ids):
                    for instruction in course_instructions:
                        self._process_instruction(instruction)
                        if len(self.loop_ids_consumed_by_current_course) == len(self.last_course_loop_ids):
                            break
                self.last_course_loop_ids = self.cur_course_loop_ids
                self.cur_course_loop_ids = []
                self.loop_ids_consumed_by_current_course = set()
                if self.current_row == row_count:
                    break
        return self.knit_graph

    def compile_with_hole(self, starting_width: int, row_count: int, pattern: str, patternIsFile: bool = False, hole_start_wale: Optional[int] = None, hole_start_row: Optional[int] = None, hole_width: Optional[int] = None, hole_height: Optional[int] = None) -> Knit_Graph: #side: Optional[str] = ''
        """
        Populates the knit_graph based on the compiled instructions. May throw errors from compilation
        :param row_count: the number of rows to knit before completing, pattern may repeat or be incomplete
        :param starting_width: the number of loops used to create the 0th course
        :param pattern: the pattern as a string or in a file
        :param patternIsFile: True if pattern is provided in a file
        :return: the resulting compiled knit graph
        """
        # yarn = self.yarn
        self.parse_results = self._parser.interpret(pattern, patternIsFile)
        self._organize_courses()
        self.populate_0th_course(starting_width)
        num_operation_courses = len(self.course_ids_to_operations)
        course_id_to_nodes_consumed_by_action = self.course_to_action_queues(starting_width)
        def row_growth(row_num, num_operation_courses):
            while self.current_row < row_num:
                for course_id in sorted(self.course_ids_to_operations):
                    self._increment_current_row()
                    if self.current_row > num_operation_courses:
                        count = int((self.current_row-1)/num_operation_courses)
                        assert self.current_row % (course_id + count * num_operation_courses) == 0
                    else: 
                        assert self.current_row % course_id  == 0
                    course_instructions = self.course_ids_to_operations[course_id]
                    while len(self.loop_ids_consumed_by_current_course) < len(self.last_course_loop_ids):
                        for instruction in course_instructions:
                            self._process_instruction(self.yarn, instruction)
                            if len(self.loop_ids_consumed_by_current_course) == len(self.last_course_loop_ids):
                                break
                    self.last_course_loop_ids = self.cur_course_loop_ids
                    self.cur_course_loop_ids = []
                    self.loop_ids_consumed_by_current_course = set()
                    if self.current_row == row_num:
                        break

        #grow bottom rows before hole first
        assert 1<hole_start_row < row_count, f'hole_start_row should be less than row_count'
        row_growth(hole_start_row - 1, num_operation_courses)

        if hole_start_row % 2 == 0:
            grow_first_operations = {}
            grow_second_operations = {}
            course_id = start_row = hole_start_row % num_operation_courses
            left_growth_range =  hole_start_wale
            right_growth_range =  starting_width - (hole_start_wale + hole_width)
            for i in range(hole_start_row, hole_start_row+hole_height):
                if i > num_operation_courses:
                    course_id = i % num_operation_courses
                else:
                    course_id = i
                course_operation_for_right = course_operation_for_left = course_id_to_nodes_consumed_by_action[course_id]
                if course_id % 2 == 1:
                    course_operation_for_left = [*reversed(course_id_to_nodes_consumed_by_action[course_id])]
                elif course_id % 2 == 0:
                    course_operation_for_right = [*reversed(course_id_to_nodes_consumed_by_action[course_id])]
                course_operation_to_load_for_left = []
                course_operation_to_load_for_right = []
                total1 = 0
                total2 = 0
                if len(course_operation_for_left) == 1:
                    action = course_operation_for_left[0][0]
                    grow_first_operations[course_id] = [(action, left_growth_range)]
                    grow_second_operations[course_id] = [(action, right_growth_range)]
                else:
                    while total1 < left_growth_range:
                        for instruction in course_operation_for_left:
                            total1 += instruction[1]
                            if course_id%2 == 1:
                                course_operation_to_load_for_left.insert(0, instruction)
                            else:
                                course_operation_to_load_for_left.append(instruction)
                            if total1 == left_growth_range:
                                break
                    grow_first_operations[course_id] = course_operation_to_load_for_left
                
                    while total2 < right_growth_range:
                        for instruction in course_operation_for_right:
                            total2 += instruction[1]
                            if course_id%2 ==0:
                                course_operation_to_load_for_right.insert(0, instruction)
                            else:
                                course_operation_to_load_for_right.append(instruction)
                            if total2 == right_growth_range:
                                break
                    grow_second_operations[course_id] = course_operation_to_load_for_right

            #add instructions for remaining rows following hole to grow_first_operations
            if hole_height % 2 == 0:
                for i in range(hole_start_row+hole_height, row_count+1):
                    course_id = i
                    grow_first_operations[course_id] = course_id_to_nodes_consumed_by_action[course_id]
            
            if len(grow_second_operations) != 0:
                    # todo: assertion regarding carrier id 
                    new_yarn = Yarn("new_yarn", self.knit_graph, carrier_id=4)
                    self.knit_graph.add_yarn(new_yarn) 

            def execute_instructions1(action, yarn, side):
                """
                Executes the action according to its type
                """
                is_stitch = isinstance(action, Stitch_Definition)
                is_cable = isinstance(action, Cable_Definition)
                is_list = type(action) is list
                if is_stitch:
                    self._process_stitch(yarn, action, side = side)
                elif is_cable:
                    self._process_cable(yarn, action, side = side)
                elif is_list:
                    self._process_list(yarn, action)
                else:
                    self._process_instruction(yarn, action)

            self.last_course_loop_ids_left = self.last_course_loop_ids[-left_growth_range:]
            self.last_course_loop_ids_right = self.last_course_loop_ids[:right_growth_range]
            for i in range(hole_height):
                while self.current_row < hole_start_row + hole_height - 1:
                    for course_id in sorted(grow_first_operations):
                        self._increment_current_row()
                        course_instructions_left = grow_first_operations[course_id]
                        course_instructions_right = grow_second_operations[course_id]
                        while len(self.loop_ids_consumed_by_current_course) < len(self.last_course_loop_ids_left): #bian
                            for instruction in course_instructions_left:
                                if isinstance(instruction[0], Stitch_Definition) and instruction[1] > 1:
                                    times = instruction[1]
                                    for i in range(times):
                                        execute_instructions1(instruction[0], yarn = self.yarn, side = 'left')
                                else:
                                    execute_instructions1(instruction[0], yarn = self.yarn, side = 'left')
                                if len(self.loop_ids_consumed_by_current_course) == len(self.last_course_loop_ids_left):
                                    break
                        self.last_course_loop_ids_left = self.cur_course_loop_ids #bian
                        self.cur_course_loop_ids = []
                        self.loop_ids_consumed_by_current_course = set()

                        while len(self.loop_ids_consumed_by_current_course) < len(self.last_course_loop_ids_right): 
                            for instruction in course_instructions_right:
                                if isinstance(instruction[0], Stitch_Definition) and instruction[1] > 1:
                                    times = instruction[1]
                                    for i in range(times):
                                        execute_instructions1(instruction[0], yarn = new_yarn, side = 'right')
                                else:
                                    execute_instructions1(instruction[0], yarn = new_yarn, side = 'right')
                                if len(self.loop_ids_consumed_by_current_course) == len(self.last_course_loop_ids_right):
                                    break
                        self.last_course_loop_ids_right = self.cur_course_loop_ids 
                        self.cur_course_loop_ids = []
                        self.loop_ids_consumed_by_current_course = set()
                        if self.current_row == hole_start_row + hole_height - 1:
                            break
            '''add dummy nodes to this special row immediately above hole, so that when len(self.cur_course_loop_ids) below increase as 
            we add node with yarn, prior_course_index will be updated as desired, otherwise cause node index bug
            # course_index = len(self.cur_course_loop_ids)
            # prior_course_index = (len(last_course_loop_ids) - 1) - course_index'''
            for i in range(hole_width):
                self.last_course_loop_ids_right.append('dummy_node'+str(i+1))
            #mind the order of list concatenation
            self.last_course_loop_ids = self.last_course_loop_ids_right + self.last_course_loop_ids_left
            special_row_nodes_num = starting_width - hole_width
            for course_id in range(hole_start_row+hole_height, row_count+1):
                # for course_id in sorted(grow_first_operations):
                self._increment_current_row()
                course_instructions_left = grow_first_operations[course_id]
                while len(self.loop_ids_consumed_by_current_course) < len(self.last_course_loop_ids): 
                    for instruction in course_instructions_left:
                        if isinstance(instruction[0], Stitch_Definition) and instruction[1] > 1:
                            times = instruction[1]
                            for i in range(times):
                                execute_instructions1(instruction[0], yarn = self.yarn, side = '')
                        else:
                            execute_instructions1(instruction[0], yarn = self.yarn, side = '')
                        if len(self.loop_ids_consumed_by_current_course) == len(self.last_course_loop_ids):
                            break
                self.last_course_loop_ids = self.cur_course_loop_ids 
                self.cur_course_loop_ids = []
                self.loop_ids_consumed_by_current_course = set()
                if self.current_row == row_count:
                    break

        return self.knit_graph

    def populate_0th_course(self, starting_width: int):
        """
        Populates the first course of the knitgraph with starting_width loops.
        Adds loop_ids in yarn-wise order to self.last_course_loop_ids
        :param starting_width: the number of loops to create
        """
        for i in range(0, starting_width):
            loop_id, loop = self.yarn.add_loop_to_end()
            self.knit_graph.add_loop(loop)
            self.last_course_loop_ids.append(loop_id)

    def _organize_courses(self):
        """
        takes the parser results and organizes the course instructions by their course ids.
        raises two possible errors
         If a course is defined more than once, raise an error documenting the course_id
         If a course between 1 and the maximum course is not defined, raise an error documenting the course_id
        Note that all closures in these ids are executed before the row operations (may cause implementation confusion)
        """
        for instructions in self.parse_results:
            course_ids = instructions["courseIds"]
            course_instructions = instructions["stitch-operations"]
            for course_id in course_ids:
                if isinstance(course_id, Num_Closure):
                    course_id = course_id.to_int()  # converts any variable numbers to their current state
                    assert course_id not in self.course_ids_to_operations, f"KnitSpeak Error: Course {course_id} is defined more than once"
                    self.course_ids_to_operations[course_id] = course_instructions
                elif isinstance(course_id, Iterator_Closure):  # closes iteration over variable numbers
                    sub_courses = course_id.to_int_list()
                    for sub_id in sub_courses:
                        assert sub_id not in self.course_ids_to_operations, f"KnitSpeak Error: Course {sub_id} is defined more than once"
                        self.course_ids_to_operations[sub_id] = course_instructions
                else:  # course_id is integer
                    assert course_id not in self.course_ids_to_operations, f"KnitSpeak Error: Course {course_id} is defined more than once"
                    self.course_ids_to_operations[course_id] = course_instructions

        max_course = max(*self.course_ids_to_operations)
        if "all_rs" in self._parser.parser.symbolTable:
            course_instructions = self.course_ids_to_operations[1] #since in hand-knitting language, course start from 1st not 0.
            for course_id in range(3, max_course + 1, 2):
                if course_id not in self.course_ids_to_operations:
                    self.course_ids_to_operations[course_id] = course_instructions
                else:
                    print(f"KnitSpeak Warning: course {course_id} overrides rs-instructions")
        if "all_ws" in self._parser.parser.symbolTable:
            course_instructions = self.course_ids_to_operations[2]
            for course_id in range(4, max_course + 1, 2):
                if course_id not in self.course_ids_to_operations:
                    self.course_ids_to_operations[course_id] = course_instructions
                else:
                    print(f"KnitSpeak Warning: course {course_id} overrides ws-instructions")

        for course_id in range(1, max_course + 1):
            assert course_id in self.course_ids_to_operations, f"KnitSpeak Error: Course {course_id} is undefined"

        if max_course % 2 == 1 and "all_ws" in self._parser.parser.symbolTable:  # ends on rs row
            self.course_ids_to_operations[max_course + 1] = self.course_ids_to_operations[2]

    def _process_instruction(self, yarn, instruction: Tuple[Union[tuple, Stitch_Definition, Cable_Definition, list],
                                                      Tuple[bool, int]], side: Optional[str]= ''):
        """
        :param instruction: A tuple with the knitting instructions and information about how to repeat them
        instruction[0] can be a stitch definition, cable definition, or a list of instruction tuples
        instruction[1] is a tuple with a boolean and an int.
         If the boolean is true, then the integer represents the number of times to repeat the instructions
         If the boolean is false, then the integer represents the number of loops left after executing the instructions
        :return:
        """
        # ([(1-BtF-c0->1, (True, 1))], (False, 0))
        action = instruction[0]
        is_stitch = isinstance(action, Stitch_Definition)
        is_cable = isinstance(action, Cable_Definition)
        is_list = type(action) is list
        static_repeats = instruction[1][0]
        repeats = 1
        if static_repeats:
            repeats = instruction[1][1]
            if isinstance(repeats, Num_Closure):
                repeats = repeats.to_int()
        remaining_loops = 0
        if not static_repeats:
            remaining_loops = instruction[1][1]
            if isinstance(remaining_loops, Num_Closure):
                remaining_loops = remaining_loops.to_int()

        def execute_instructions(yarn, action, side = side):
            """
            Executes the action according to its type
            """
            if is_stitch:
                self._process_stitch(yarn, action, side = side)
            elif is_cable:
                self._process_cable(yarn, action, side = side)
            elif is_list:
                self._process_list(yarn, action)
            else:
                self._process_instruction(yarn, action)

        if not static_repeats:  # need to iterate until remaining loops is left
            while (len(self.last_course_loop_ids) - len(self.loop_ids_consumed_by_current_course)) > remaining_loops:
                execute_instructions(yarn, action, side = side)
            assert remaining_loops == (len(self.last_course_loop_ids) - len(self.loop_ids_consumed_by_current_course))
        else:
            for _ in range(0, repeats):
                execute_instructions(yarn, action, side = side)
    
    def course_to_action_queues(self, starting_width):
        course_id_to_nodes_consumed_by_action = {}
        repeats = 1 
        for course_id in sorted(self.course_ids_to_operations):
            count = 0
            course_id_to_nodes_consumed_by_action[course_id] = []
            course_instructions = self.course_ids_to_operations[course_id]
            if len(course_instructions) == 1 and course_instructions[0][1][0] == True:
                repeats = starting_width
                course_id_to_nodes_consumed_by_action[course_id].append((course_instructions[0][0], repeats))
            else:
                for instruction in course_instructions:
                    action = instruction[0]
                    static_repeats = instruction[1][0]
                    repeats = 1
                    if static_repeats:
                        repeats = instruction[1][1]
                        if isinstance(repeats, Num_Closure):
                            repeats = repeats.to_int()
    
                    if isinstance(action, Stitch_Definition):
                        nodes_consumed_num = len(action)
                    elif isinstance(action, Cable_Definition):
                        nodes_consumed_num = len(action.stitch_definitions())
                    elif type(action) is list and instruction[1][0] == False:
                        nodes_consumed_num = starting_width - count
                        action = action[0][0]
                    course_id_to_nodes_consumed_by_action[course_id].append((action, repeats*nodes_consumed_num))
                    count+=repeats*nodes_consumed_num
        return course_id_to_nodes_consumed_by_action


    def _process_stitch(self, yarn, stitch_def: Stitch_Definition, flipped_by_cable=False, side: Optional[str] = ''):
        """
        Uses a stitch definition and compiler state to generate a new loop and connect it to the prior course.
        May throw two compiler errors.
         if there is no loop at the parent offsets of the stitch, then throw an error reporting the missing index
         if a parent loop has already been consumed, then throw an error reporting the misused parent loop
        :param flipped_by_cable: if True, implies that this stitch came from a cable and has been flipped appropriately
        :param stitch_def: the stitch definition used to connect the new loop
        """
        if side == 'left':
            last_course_loop_ids = self.last_course_loop_ids_left
        elif side == 'right':
            last_course_loop_ids = self.last_course_loop_ids_right
        else:
            last_course_loop_ids  = self.last_course_loop_ids
        if self._working_ws and not flipped_by_cable:  # flips stitches following hand-knitting conventions
            stitch_def = stitch_def.copy_and_flip()
        course_index = len(self.cur_course_loop_ids)
        prior_course_index = (len(last_course_loop_ids) - 1) - course_index
        if stitch_def.child_loops == 1:
            # Todo: Implement processing the stitch into the knitgraph
            #  add a new loop to the end of  self.yarn and add it to the self.knitgraph
            #  iterate over the stitch's parent offsets in their stack order
            #   the index of the parent_loop in self.last_course_loop_ids will be the prior_course_index plus the offset
            #   mark the parent_loop as "consumed" by putting it in the loop_ids_consumed_by_current_course set
            #   then connect that parent loop to the new child_loop given the stitch information in the stitch_def
            #  add the newly created loop to the end of self.cur_course_loop_ids
            loop_id, loop = yarn.add_loop_to_end()
            self.knit_graph.add_loop(loop)
            for stack_position, parent_offset in enumerate(stitch_def.offset_to_parent_loops):
                parent_index = prior_course_index + parent_offset
                assert 0 <= parent_index < len(last_course_loop_ids), f"Knitspeak Error: Cannot find a loop at index {parent_index}"
                parent_loop_id = last_course_loop_ids[parent_index]
                assert parent_loop_id not in self.loop_ids_consumed_by_current_course, \
                    f"Knitspeak Error: Loop {parent_loop_id} has already been used"
                self.loop_ids_consumed_by_current_course.add(parent_loop_id)
                if 'dummy_node' not in str(parent_loop_id):
                    self.knit_graph.connect_loops(parent_loop_id, loop_id, stitch_def.pull_direction,
                                                stack_position, stitch_def.cabling_depth, parent_offset)
            self.cur_course_loop_ids.append(loop_id)
        else:  # slip statement
            assert len(stitch_def.offset_to_parent_loops) == 1, "Cannot slip multiple loops"
            for stack_position, parent_offset in enumerate(stitch_def.offset_to_parent_loops):
                parent_index = (len(last_course_loop_ids) - 1) - course_index + parent_offset
                assert 0 <= parent_index < len(last_course_loop_ids), f"Knitspeak Error: Cannot find a loop at index {parent_index}"
                parent_loop_id = last_course_loop_ids[parent_index]
                assert parent_loop_id not in self.loop_ids_consumed_by_current_course, \
                    f"Knitspeak Error: Loop {parent_loop_id} has already been used"
                self.loop_ids_consumed_by_current_course.add(parent_loop_id)
                self.cur_course_loop_ids.append(parent_loop_id)

    def _process_cable(self, yarn, cable_def: Cable_Definition, side: Optional[str] = ''):
        """
        Uses a cable definition and compiler state to generate and connect a cable
        :param cable_def: the cable definition used to connect the cable into the knitgraph
        """
        if self._working_ws:  # flips cable by hand-knitting convention
            cable_def = cable_def.copy_and_flip()
        stitch_definitions = cable_def.stitch_definitions()
        for stitch_definition in stitch_definitions:
            self._process_stitch(yarn, stitch_definition, flipped_by_cable=True, side = side)

    def _process_list(self, yarn, action: List[tuple]):
        """
        Processes actions in a list of actions
        :param action: the list of actions
        """
        for sub_action in action:
            self._process_instruction(yarn, sub_action)
