"""The graph structure used to represent knitted objects"""
from enum import Enum
from typing import Dict, Optional, List, Tuple, Union, Set

import networkx

from knit_graphs.Loop import Loop
from knit_graphs.Yarn import Yarn
from knitting_machine.Machine_State import Yarn_Carrier


class Pull_Direction(Enum):
    """An enumerator of the two pull directions of a loop"""
    BtF = "BtF"
    FtB = "FtB"

    def opposite(self):
        """
        :return: returns the opposite pull direction of self
        """
        if self is Pull_Direction.BtF:
            return Pull_Direction.FtB
        else:
            return Pull_Direction.BtF

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

class Knit_Graph:
    """
    A class to knitted structures
    ...

    Attributes
    ----------
    graph : networkx.DiGraph
        the directed-graph structure of loops pulled through other loops
    loops: Dict[int, Loop]
        A map of each unique loop id to its loop
    yarns: Dict[str, Yarn]
         A list of Yarns used in the graph
    """

    def __init__(self, yarn_start_direction: Optional[str] = 'right to left', gauge: Optional[int] = 1): 
        self.graph: networkx.DiGraph = networkx.DiGraph()
        self.loops: Dict[int, Loop] = {}
        self.last_loop_id: int = -1
        self.yarns: Dict[str, Yarn] = {}
        self.gauge: float = gauge
        self.wale_dist: int = int(1/self.gauge)
        self.object_type: str
        self.loop_ids_to_course: Dict[int, int] = {}
        self.course_to_loop_ids: Dict[int, List[int]] = {}
        self.loop_ids_to_wale: Dict[int, int] = {}
        self.wale_to_loop_ids: Dict[int, List[int]] = {}
        self.node_to_course_and_wale: Dict[int, Tuple[int, int]] = {}
        self.node_on_front_or_back: Dict[int, str] = {}
        self.course_and_wale_and_bed_to_node: Dict[((int, int), str), int] = {}
        self.yarn_start_direction: str = yarn_start_direction

        self.loops_on_front_part_of_the_tube: Set[int] = set()
        self.loops_on_back_part_of_the_tube: Set[int] = set()
        
        self.yarn_over_loop_to_loop_index: Dict[int, int] = {}

        self.course_id_to_walking_direction: Dict[int, str] = {}

    def add_loop_to_front_part(self, loop_id: int):
        self.loops_on_front_part_of_the_tube.add(loop_id)

    def add_loop_to_back_part(self, loop_id: int):
        self.loops_on_back_part_of_the_tube.add(loop_id)
    
    def add_index_for_yarn_over_loop(self, loop_id, index):
        self.yarn_over_loop_to_loop_index[loop_id] = index

    def add_loop(self, loop: Loop):
        """
        :param loop: the loop to be added in as a node in the graph
        """
        # below we can see "loop" is added as an attribute in add_node, corresponds to the get_item() down below
        self.graph.add_node(loop.loop_id, loop=loop)
        assert loop.yarn_id in self.yarns, f"No yarn {loop.yarn_id} in this graph"
      
        if loop not in self.yarns[loop.yarn_id]:  # make sure the loop is on the yarn specified
            self.yarns[loop.yarn_id].add_loop_to_end(loop_id=None, loop=loop)
           
        self.loops[loop.loop_id] = loop

    def add_yarn(self, yarn: Yarn):
        """
        :param yarn: the yarn to be added to the graph structure
        """
        self.yarns[yarn.yarn_id] = yarn

    def connect_loops(self, parent_loop_id: int, child_loop_id: int,
                      pull_direction: Pull_Direction = Pull_Direction.BtF,
                      stack_position: Optional[int] = None, depth: int = 0, parent_offset: int = 0):
        """
        Creates a stitch-edge by connecting a parent and child loop
        :param parent_offset: The direction and distance, oriented from the front, to the parent_loop
        :param depth: -1, 0, 1: The crossing depth in a cable over other stitches. 0 if Not crossing other stitches
        :param parent_loop_id: the id of the parent loop to connect to this child
        :param child_loop_id:  the id of the child loop to connect to the parent
        :param pull_direction: the direction the child is pulled through the parent
        :param stack_position: The position to insert the parent into, by default add on top of the stack
        """
        assert parent_loop_id in self, f"parent loop {parent_loop_id} is not in this graph"
        assert child_loop_id in self, f"child loop {child_loop_id} is not in this graph"
        self.graph.add_edge(parent_loop_id, child_loop_id, pull_direction=pull_direction, depth=depth, parent_offset=parent_offset)
        child_loop = self[child_loop_id]
        parent_loop = self[parent_loop_id]
        # print(child_loop, parent_loop)
        child_loop.add_parent_loop(parent_loop, stack_position)
    
    def get_courses(self) -> Tuple[Dict[int, int], Dict[int, List[int]]]:
        """
        :return: A dictionary of loop_ids to the course they are on,
        a dictionary or course ids to the loops on that course in the order of creation
        The first set of loops in the graph is on course 0.
        A course change occurs when a loop has a parent loop that is in the last course.
        """
        # loop_ids_to_course = {}
        # course_to_loop_ids = {}
        current_course_set = set()
        current_course = []
        course = 0
        #since given knit graph has only one yarn before being modified
        for loop_id in self.graph.nodes:
            no_parents_in_course = True
            for parent_id in self.graph.predecessors(loop_id):
                # print(f'predecessors is {[*self.graph.predecessors(loop_id)]}, loop_id is {loop_id}')
                if parent_id in current_course_set:
                    no_parents_in_course = False
                    break
            if no_parents_in_course:
                current_course_set.add(loop_id)
                current_course.append(loop_id)
            else:
                self.course_to_loop_ids[course] = current_course
                current_course = [loop_id]
                current_course_set = {loop_id}
                course += 1
            self.loop_ids_to_course[loop_id] = course
            # print(f'current_course_set is {current_course_set}')
        self.course_to_loop_ids[course] = current_course
        print(f'course_to_loop_ids in Knit_Graph is {self.course_to_loop_ids}')
        return self.loop_ids_to_course, self.course_to_loop_ids

    def get_wales(self) :
        print(f'self.yarn_over_loop_to_loop_index is {self.yarn_over_loop_to_loop_index}')
        yarns = [*self.yarns.values()]
        #since given knit graph has only one yarn before being modified
        yarn = yarns[0]
        # loop_ids_to_wale = {}
        # wale_to_loop_ids = {}
        first_course_loop_ids = self.course_to_loop_ids[0] 
        wale = 0
        assert (1/self.gauge).is_integer() == True, f'wrong gauge info'
        self.wale_dist = int(1/self.gauge)
        # print(f'self.wale_dist is {self.wale_dist}')
        for loop_id in first_course_loop_ids:
            self.loop_ids_to_wale[loop_id] = wale
            self.wale_to_loop_ids[wale] = [loop_id]
            # wale += 1
            wale += self.wale_dist
            # print(f'loop_id is {loop_id}, wale is {wale}')
        for course_id in [*self.course_to_loop_ids.keys()][1:]:
            next_row_loop_ids = self.course_to_loop_ids[course_id]
            for loop_id in next_row_loop_ids:
                self.has_parent_of_0_offset = False
                parent_ids = [*self.graph.predecessors(loop_id)]
                if len(parent_ids) > 0:
                    for parent_id in self.graph.predecessors(loop_id):
                        parent_offset = self.graph[parent_id][loop_id]['parent_offset']
                        if parent_offset == 0:
                            wale = self.loop_ids_to_wale[parent_id]
                            self.loop_ids_to_wale[loop_id] = wale
                            if wale not in self.wale_to_loop_ids:
                                self.wale_to_loop_ids[wale] = []
                                self.wale_to_loop_ids[wale].append(loop_id)
                            else:
                                self.wale_to_loop_ids[wale].append(loop_id)
                            # print(f'loop id is {loop_id}, parent id is {parent_id}, wale is {wale}')
                            self.has_parent_of_0_offset = True
                            break
                    if self.has_parent_of_0_offset == False:
                        for parent_id in self.graph.predecessors(loop_id):
                            parent_offset = self.graph[parent_id][loop_id]['parent_offset']
                            wale = self.loop_ids_to_wale[parent_id] - parent_offset*self.wale_dist
                            # if self.object_type == 'sheet':
                            #     wale = self.loop_ids_to_wale[parent_id] - parent_offset*self.wale_dist
                            # elif self.object_type == 'tube':
                            #     wale = self.loop_ids_to_wale[parent_id] + parent_offset*self.wale_dist
                            self.loop_ids_to_wale[loop_id] = wale
                            if wale not in self.wale_to_loop_ids:
                                self.wale_to_loop_ids[wale] = []
                                self.wale_to_loop_ids[wale].append(loop_id)
                            else:
                                self.wale_to_loop_ids[wale].append(loop_id)
                            break
                else:
                    #If its predecessor node on yarn has wale, then combined with corresponding course_id, its wale can be inferred
                    #Since a node on yarn always has one predecessor, except that starting node has 0 predecessor.
                    # yarn_predecessor = [*yarn.yarn_graph.predecessors(loop_id)][0]
                    # # yarn_successor = [*yarn.yarn_graph.successors(loop_id)][0]
                    # if yarn_predecessor in self.loop_ids_to_wale.keys():
                    #     pre_wale = self.loop_ids_to_wale[yarn_predecessor]
                    #     if self.object_type == 'sheet':
                    #         if course_id % 2 == 1:
                    #             wale = pre_wale - self.wale_dist
                    #             self.loop_ids_to_wale[loop_id] = wale
                    #         else: 
                    #             wale = pre_wale + self.wale_dist
                    #             self.loop_ids_to_wale[loop_id] = wale
                    #     elif self.object_type == 'tube':
                    #         wale = pre_wale + self.wale_dist
                    #         self.loop_ids_to_wale[loop_id] = wale
                    #     if wale not in self.wale_to_loop_ids:
                    #         self.wale_to_loop_ids[wale] = [loop_id]
                    #     else:
                    #         self.wale_to_loop_ids[wale].append(loop_id)
                    # else:
                    #     print(f'Error: wale of node {loop_id} cannot be determined')
                    #     exit()

                    #----#
                    if self.object_type == 'sheet':
                        if course_id % 2 == 1:
                            wale = self.loop_ids_to_wale[self.course_to_loop_ids[course_id-1][-1]] - self.yarn_over_loop_to_loop_index[loop_id]*self.wale_dist
                            self.loop_ids_to_wale[loop_id] = wale
                        else:
                            wale = self.loop_ids_to_wale[self.course_to_loop_ids[course_id-1][-1]] + self.yarn_over_loop_to_loop_index[loop_id]*self.wale_dist
                            self.loop_ids_to_wale[loop_id] = wale
                    else:
                        if loop_id in self.loops_on_front_part_of_the_tube:
                            wale = self.yarn_over_loop_to_loop_index[loop_id]*self.wale_dist
                            self.loop_ids_to_wale[loop_id] = wale
                        else:
                            mid_node =self.course_to_loop_ids[0][int(len(first_course_loop_ids)/2) - 1]
                            print(f'self.yarn_over_loop_to_loop_index[loop_id] is {self.yarn_over_loop_to_loop_index[loop_id]}')
                            wale = self.loop_ids_to_wale[mid_node] -1 - self.yarn_over_loop_to_loop_index[loop_id]*self.wale_dist
                            self.loop_ids_to_wale[loop_id] = wale
                    #----#
        print(f'loop_ids_to_wale in KnitGraph is {self.loop_ids_to_wale}, wale_to_loop_ids in KnitGraph is {self.wale_to_loop_ids}')
        return self.loop_ids_to_wale, self.wale_to_loop_ids

    def get_node_course_and_wale(self):
        """
        this used real wale id self.loop_ids_to_wale above to calculate the final wale id used for visualization for tube.
        """
        for node in self.graph.nodes:
            course = self.loop_ids_to_course[node]
            wale = self.loop_ids_to_wale[node]
            self.node_to_course_and_wale[node] = (course, wale)
        if self.object_type == 'tube':
            #-----deprecated as this not accommodate tube object with increase
            # first_course_loops = self.course_to_loop_ids[0] # first course loops is considered because there will be no slip for it.
            # mid_node_pos = int(len(first_course_loops)/2) - 1
            # mid_node = first_course_loops[mid_node_pos]
            # mid_node_wale = self.loop_ids_to_wale[mid_node]
            # last_node = first_course_loops[-1]
            # max_wale = self.loop_ids_to_wale[last_node]
            # #below is original version that works well except for tube with increase stitch
            # for node in self.graph.nodes:
            #     course = self.loop_ids_to_course[node]
            #     wale = self.loop_ids_to_wale[node]
            #     if wale > mid_node_wale:
            #         adjusted_wale = max_wale - wale -1 #-1 is because we use half gauging to avoid loop collision. And by doing this, the wale of the mirror
            #         #node on the back is always one wale smaller than that of corresponding node on the front.
            #         self.node_to_course_and_wale[node] = (course, adjusted_wale)
            #----deprecated-----
            #--- this version aims to accommodate tube object with increase---
            first_course_loop_ids = self.course_to_loop_ids[0] 
            mid_node_pos = int(len(first_course_loop_ids)/2) - 1
            mid_node = first_course_loop_ids[mid_node_pos]
            mid_node_wale = self.loop_ids_to_wale[mid_node]
            last_node = first_course_loop_ids[-1]
            max_wale = self.loop_ids_to_wale[last_node]
            #we do the wale adjustment only on the first course
            for node in first_course_loop_ids:
                course = self.loop_ids_to_course[node]
                wale = self.loop_ids_to_wale[node]
                if wale > mid_node_wale:
                    adjusted_wale = max_wale - wale -1 #-1 is because we use half gauging to avoid loop collision. And by doing this, the wale of the mirror
                    #node on the back is always one wale smaller than that of corresponding node on the front.
                    self.node_to_course_and_wale[node] = (course, adjusted_wale)
            #then for the remaining course, we use the adjusted wale to compute
            yarns = [*self.yarns.values()]
            #since given knit graph has only one yarn before being modified
            yarn = yarns[0]
            for course_id in [*self.course_to_loop_ids.keys()][1:]:
                next_row_loop_ids = self.course_to_loop_ids[course_id]
                for loop_id in next_row_loop_ids:
                    self.has_parent_of_0_offset = False
                    parent_ids = [*self.graph.predecessors(loop_id)]
                    if len(parent_ids) > 0:
                        for parent_id in self.graph.predecessors(loop_id):
                            parent_offset = self.graph[parent_id][loop_id]['parent_offset']
                            if parent_offset == 0:
                                wale = self.node_to_course_and_wale[parent_id][1]
                                self.node_to_course_and_wale[loop_id] = (course_id, wale)
                                # print(f'in tube wale recomputation, loop id is {loop_id}, parent id is {parent_id}, wale is {wale}')
                                self.has_parent_of_0_offset = True
                                break
                        if self.has_parent_of_0_offset == False:
                            for parent_id in self.graph.predecessors(loop_id):
                                parent_offset = self.graph[parent_id][loop_id]['parent_offset']
                                wale = self.node_to_course_and_wale[parent_id][1] - parent_offset*self.wale_dist
                                self.node_to_course_and_wale[loop_id] = (course_id, wale)
                                break
                    else:
                        #If its predecessor node on yarn has wale, then combined with corresponding course_id, its wale can be inferred
                        #Since a node on yarn always has one predecessor, except that starting node has 0 predecessor.
                        # yarn_predecessor = [*yarn.yarn_graph.predecessors(loop_id)][0]
                        # # yarn_successor = [*yarn.yarn_graph.successors(loop_id)][0]
                        # if yarn_predecessor in self.node_to_course_and_wale.keys():
                        #     pre_wale = self.node_to_course_and_wale[yarn_predecessor][1]
                        #     if self.object_type == 'tube':
                        #         wale = pre_wale + self.wale_dist
                        #         self.node_to_course_and_wale[loop_id] = (course_id, wale)
                        # else:
                        #     print(f'Error: wale of node {loop_id} cannot be determined')
                        #     exit()
                        #----#
                        if loop_id in self.loops_on_front_part_of_the_tube:
                            wale = self.yarn_over_loop_to_loop_index[loop_id]*self.wale_dist
                        else:
                            wale = mid_node_wale -1 - self.yarn_over_loop_to_loop_index[loop_id]*self.wale_dist
                        #----#
        #-------
        print(f'node_to_course_and_wale in KnitGraph is {self.node_to_course_and_wale}')
        return self.node_to_course_and_wale

    def get_node_bed(self):
        if self.object_type == 'sheet':
            for node in self.graph.nodes:
                self.node_on_front_or_back[node] = 'f'
        elif self.object_type == 'tube':
            for node in self.graph.nodes:
                if node in self.loops_on_front_part_of_the_tube:
                    self.node_on_front_or_back[node] = 'f'
                else:
                    self.node_on_front_or_back[node] = 'b'
        print(f'self.node_on_front_or_back in Knit Graph is {self.node_on_front_or_back}')
        return self.node_on_front_or_back

    def get_course_and_wale_and_bed_to_node(self):
        if self.object_type == 'tube':
            for node in self.node_on_front_or_back.keys():
                course_and_wale = self.node_to_course_and_wale[node]
                front_or_back = self.node_on_front_or_back[node]
                self.course_and_wale_and_bed_to_node[(course_and_wale, front_or_back)] = node
            return self.course_and_wale_and_bed_to_node
    
    def update_parent_offsets(self):  
        """
        update it to make all stitches consistent with the view -- comply with the only wale advancing direction, rather than the alternating yarn walking direction.
        We do this to avoid wrong parent-offset extracted in knitout interpreter, which would lead to failed conversion.
        """
        for loop_id in self.graph.nodes:
            parent_loops = [*self.graph.predecessors(loop_id)]
            if len(parent_loops) != 0:
                for parent_id in self.graph.predecessors(loop_id):
                    parent_offset = self.graph[parent_id][loop_id]['parent_offset']
                    if parent_offset != 0:
                        # print(f'loop id is {loop_id}, parent id is {parent_id}, original parent offset is {parent_offset}')
                        # we deprecated this because the actual wale_id we use to visualize graph is self.node_to_course_and_wale rather than self.loop_ids_to_wale.
                        # self.graph[parent_id][loop_id]['parent_offset'] =  int((self.loop_ids_to_wale[parent_id] - self.loop_ids_to_wale[loop_id])/self.wale_dist)
                        # print(f'wale of parent id {parent_id} is {self.loop_ids_to_wale[parent_id]}, wale of loop id {loop_id} is {self.loop_ids_to_wale[loop_id]}')
                        # self.graph[parent_id][loop_id]['parent_offset'] =  int((self.node_to_course_and_wale[parent_id][1] - self.node_to_course_and_wale[loop_id][1])/self.wale_dist)
                        # above is deprecated because it does not work for stitch like point from b2 to f1.
                        updated_parent_offset = (self.node_to_course_and_wale[parent_id][1] - self.node_to_course_and_wale[loop_id][1])/self.wale_dist
                        if parent_offset != updated_parent_offset:
                            print(f'offset update for loop id is {loop_id}! parent id is {parent_id}, original parent offset is {parent_offset}, updated parent offset is {updated_parent_offset}')
                        self.graph[parent_id][loop_id]['parent_offset'] = (self.node_to_course_and_wale[parent_id][1] - self.node_to_course_and_wale[loop_id][1])/self.wale_dist
                        # print(f'wale of parent id {parent_id} is {self.node_to_course_and_wale[parent_id][1]}, wale of loop id {loop_id} is {self.node_to_course_and_wale[loop_id][1]}')

    def get_carriers(self) -> List[Yarn_Carrier]:
        """
        :return: A list of yarn carriers that hold the yarns involved in this graph
        """
        return [yarn.carrier for yarn in self.yarns.values()]

    def __contains__(self, item):
        """
        :param item: the loop being checked for in the graph
        :return: true if the loop_id of item or the loop is in the graph
        """
        if type(item) is int:
            return self.graph.has_node(item)
        elif isinstance(item, Loop):
            return self.graph.has_node(item.loop_id)
        else:
            return False

    def __getitem__(self, item: int) -> Loop:
        """
        :param item: the loop_id being checked for in the graph
        :return: the Loop in the graph with the matching id
        """
        if item not in self:
            raise AttributeError
        else:
            return self.graph.nodes[item]["loop"]

