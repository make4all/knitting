"""The graph structure used to represent knitted objects"""
from enum import Enum
from typing import Dict, Optional, List, Tuple, Union

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
        self.yarn_start_direction = yarn_start_direction
        
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
                parent_ids = [*self.graph.predecessors(loop_id)]
                if len(parent_ids) > 0:
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
                    yarn_predecessor = [*yarn.yarn_graph.predecessors(loop_id)][0]
                    # yarn_successor = [*yarn.yarn_graph.successors(loop_id)][0]
                    if yarn_predecessor in self.loop_ids_to_wale.keys():
                        pre_wale = self.loop_ids_to_wale[yarn_predecessor]
                        if self.object_type == 'sheet':
                            if course_id % 2 == 1:
                                wale = pre_wale - self.wale_dist
                                self.loop_ids_to_wale[loop_id] = wale
                            else: 
                                wale = pre_wale + self.wale_dist
                                self.loop_ids_to_wale[loop_id] = wale
                        elif self.object_type == 'tube':
                            wale = pre_wale + self.wale_dist
                            self.loop_ids_to_wale[loop_id] = wale
                            # if course_id % 2 == 1:
                            #     wale = pre_wale + self.wale_dist
                            #     self.loop_ids_to_wale[loop_id] = wale
                            # else: 
                            #     wale = pre_wale - self.wale_dist
                            #     self.loop_ids_to_wale[loop_id] = wale
                        if wale not in self.wale_to_loop_ids:
                            self.wale_to_loop_ids[wale] = [loop_id]
                        else:
                            self.wale_to_loop_ids[wale].append(loop_id)
                    else:
                        print(f'Error: wale of node {loop_id} cannot be determined')
                        exit()
        print(f'loop_ids_to_wale is {self.loop_ids_to_wale}, wale_to_loop_ids is {self.wale_to_loop_ids}')
        return self.loop_ids_to_wale, self.wale_to_loop_ids

    def get_node_course_and_wale(self):
        # node_to_course_and_wale = {}
        for node in self.graph.nodes:
            course = self.loop_ids_to_course[node]
            wale = self.loop_ids_to_wale[node]
            self.node_to_course_and_wale[node] = (course, wale)
        if self.object_type == 'tube':
            first_course_loops = self.course_to_loop_ids[0] # first course loops is considered because there will be no slip for it.
            mid_node_pos = int(len(first_course_loops)/2) - 1
            mid_node = first_course_loops[mid_node_pos]
            mid_node_wale = self.loop_ids_to_wale[mid_node]
            last_node = first_course_loops[-1]
            max_wale = self.loop_ids_to_wale[last_node]
            for node in self.graph.nodes:
                course = self.loop_ids_to_course[node]
                wale = self.loop_ids_to_wale[node]
                if wale > mid_node_wale:
                    adjusted_wale = max_wale - wale -1 #-1 is because we use half gauging to avoid loop collision. And by doing this, the wale of the mirror
                    #node on the back is always one wale smaller than that of corresponding node on the front.
                    self.node_to_course_and_wale[node] = (course, adjusted_wale)
            #below is deprecated as it does not work for slip case as in test_write_slipped_rib(), i.e. when the len(loops_in_the_course) < swatch_width
            # for node in self.graph.nodes:
            #     course = loop_ids_to_course[node]
            #     node_pos = course_to_loop_ids[course].index(node)
            #     mid_node_pos = int(len(course_to_loop_ids[course])/2) - 1
            #     if node_pos > mid_node_pos:
            #         mirror_node_pos = len(course_to_loop_ids[course]) - 1 - node_pos
            #         mirror_node = course_to_loop_ids[course][mirror_node_pos]
            #         adjusted_wale = mirror_node_wale = loop_ids_to_wale[mirror_node]
            #         node_to_course_and_wale[node] = [course, adjusted_wale]
        print(f'node_to_course_and_wale is {self.node_to_course_and_wale}')
        return self.node_to_course_and_wale

    def get_node_bed(self):
        # node_on_front_or_back = {}
        if self.object_type == 'sheet':
            for node in self.graph.nodes:
                self.node_on_front_or_back[node] = 'f'
        # below require update later
        elif self.object_type == 'tube':
            for node in self.graph.nodes:
                course = self.loop_ids_to_course[node]
                index_last_node_on_front = int(len(self.course_to_loop_ids[course])/2) - 1
                last_node_on_front = self.course_to_loop_ids[course][index_last_node_on_front]
                if self.loop_ids_to_wale[node] <= self.loop_ids_to_wale[last_node_on_front]: 
                    self.node_on_front_or_back[node] = 'f'
                else:
                    self.node_on_front_or_back[node] = 'b'
        return self.node_on_front_or_back

    def get_course_and_wale_and_bed_to_node(self):
        if self.object_type == 'tube':
            for node in self.node_on_front_or_back.keys():
                course_and_wale = self.node_to_course_and_wale[node]
                front_or_back = self.node_on_front_or_back[node]
                self.course_and_wale_and_bed_to_node[(course_and_wale, front_or_back)] = node
            return self.course_and_wale_and_bed_to_node
    
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

