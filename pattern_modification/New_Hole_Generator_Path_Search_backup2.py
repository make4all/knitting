from typing import Optional, List, Dict, Tuple, Union
import networkx as nx
import random
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph, Pull_Direction
from debugging_tools.new_knit_graph_viz import visualize_knitGraph
from debugging_tools.new_simple_knitgraphs import *
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
import warnings

class Hole_Generator:
    """
    Compared to "Hole_Generator" version, this version can work on polygon shaped fabric rather then only a rectangle.
    Biggest assumption: the function currently only apply for hole that are rectagular and only one hole. More yarns are needed if 
    the above condition is not satisfied.
    """
    def __init__(self, knit_graph: Knit_Graph, object_type: str, node_to_delete: List[int], new_carrier: int, new_yarn_id: str = 'new_yarn', starting_nodes_coor: Optional[List[Tuple[int, int]]] = None, ending_nodes_coor: Optional[List[Tuple[int, int]]] = None, course_to_loop_ids: Optional[Dict[int, List[int]]] = None, node_to_course_and_wale: Optional[Dict[int, Tuple[int, int]]] = None, course_and_wale_to_node: Optional[Dict[Tuple[int, int], int]] = None, is_polygon: bool = False, unmodified: bool = True, gauge: Optional[float] = 1):
        self._knit_graph: Knit_Graph = knit_graph
        self.new_knit_graph: Knit_Graph
        self.knitgraph_coors_connectivity: List[Tuple] = []
        self.object_type: str = object_type
        self.gauge: float = gauge
        self.wale_dist = int(1/self.gauge)
        assert len(self._knit_graph.yarns) == 1, "This only supports modifying graphs with one yarn"
        #since given knit graph has only one yarn before being modified
        self._old_yarn: Yarn = [*knit_graph.yarns.values()][0]
        assert new_carrier != None, f'new carrier is needed to introduce new yarn'
        self._new_carrier: int = new_carrier
        self._new_yarns: Union[Yarn, List[Yarn]] = []
        self.new_yarn_id: str = new_yarn_id
        self._unmodified: bool = unmodified
        self._loop_id_to_course: Dict[int, float]
        self._course_to_loop_ids: Dict[float, List[int]] 
        self._loop_id_to_wale: Dict[int, float] 
        self._wale_to_loop_ids: Dict[float, List[int]]
        self.node_to_course_and_wale: Dict[int, Tuple(int, int)]    
        self.course_and_wale_to_node: Dict[Tuple[int, int], int] 
        self.course_id_to_wale_ids: Dict[int, List[int]] = {}
        self.starting_nodes_coor: List[Tuple[int, int]]
        self.ending_nodes_coor: List[Tuple[int, int]]
        self.course_id_to_start_wale_id: Optional[Dict[int, int]]
        self.course_id_to_end_wale_id: Optional[Dict[int, int]]
        if is_polygon == False: #then the input knit graph is a common retangle, it is safe to invoke knitgraph.get_course()
            print(f'gauge in hole_generator is {gauge}')
            self._loop_id_to_course, self._course_to_loop_ids, self._loop_id_to_wale, self._wale_to_loop_ids = self._knit_graph.get_courses(unmodified, gauge = gauge)
        elif is_polygon == True:
            assert starting_nodes_coor is not None
            self.starting_nodes_coor = starting_nodes_coor
            assert ending_nodes_coor is not None
            self.ending_nodes_coor = ending_nodes_coor
            assert course_to_loop_ids is not None
            assert node_to_course_and_wale is not None
            assert course_and_wale_to_node is not None
            self._course_to_loop_ids, self.node_to_course_and_wale, self.course_and_wale_to_node = course_to_loop_ids, node_to_course_and_wale, course_and_wale_to_node
        self.is_polygon = is_polygon   
        #pattern_height is the total number of courses 
        self._pattern_height: int = len(self._course_to_loop_ids)
        #pattern_width is the total number of wales
        # self._pattern_width: int = len(self._wale_to_loop_ids)
        # self._pattern_width_per_course: Dict[int, int] 
        self._node_to_delete: List[int] = node_to_delete
        self._hole_start_course: int = self._pattern_height - 1
        self._hole_end_course: int = 0
        # self._hole_start_wale: int = self._pattern_width - 1
        # self._hole_start_wale: int = max([len(i) for i in self._course_to_loop_ids.values()]) does not work for the case 
        # where the polygon is slanted towards the right, so it is possible that max([len(i) for i in self._course_to_loop_ids.values()]) is 
        #actually smaller than real "hole_start_wale".
        self._hole_start_wale: int = 10000
        self._hole_end_wale: int = 0
        self._hole_height: int = None
        self._hole_width: int = None
        self._hole_course_to_wale_ids: Dict[int, List[int]] = {}
   
    def get_nodes_course_and_wale(self):
        """
        Get the [course, wale] coordinate of each node in the knit graph.
        """
        node_to_course_and_wale = {}
        print(f'self._loop_id_to_wale is {self._loop_id_to_wale}')
        for node in self._knit_graph.graph.nodes:
            course = self._loop_id_to_course[node]
            wale = self._loop_id_to_wale[node]
            node_to_course_and_wale[node] = (course, wale)
        #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
        course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
        # print('loop_ids_to_course', loop_ids_to_course)
        print('course_and_wale_to_node', course_and_wale_to_node)
        print('node_to_course_and_wale', node_to_course_and_wale)
        self.node_to_course_and_wale = node_to_course_and_wale
        self.course_and_wale_to_node = course_and_wale_to_node
        return node_to_course_and_wale, course_and_wale_to_node
    
    def get_hole_size(self):
        """
        hole_start_course = self._pattern_height - 1
        :param hole_start_course: the minimal wale_id of any node in nodes_to_delete
        :param hole_end_course: the maximal course_id of any node in nodes_to_delete
        :param hole_start_wale: the minimal wale_id of any node in nodes_to_delete
        :param hole_end_wale: the maximal wale_id of any node in nodes_to_delete
        Assertion: number of unique wale id can not exceed 6 to make it a feasible to knit on knittimg machine taking into account racking constraint.
        """
        # wale_involved = set()
        for node in self._node_to_delete:
            wale_id = self.node_to_course_and_wale[node][1]
            # wale_involved.add(wale_id)
            course_id = self.node_to_course_and_wale[node][0]
            if course_id > self._hole_end_course:
                self._hole_end_course = course_id
            if course_id < self._hole_start_course:
                self._hole_start_course = course_id
            if wale_id < self._hole_start_wale:
                self._hole_start_wale = wale_id
            if wale_id > self._hole_end_wale:
                self._hole_end_wale = wale_id
        print(f'hole_start_course is {self._hole_start_course}, hole_end_course is {self._hole_end_course}, hole_start_wale is {self._hole_start_wale}, hole_end_wale is {self._hole_end_wale}')
        #number of unique wale id can not exceed 6 to make it a feasible to knit on knittimg machine taking into account racking constraint
        # assert len(wale_involved) <= 4, f'hole width is too large to achieve the racking bound by 2 on the machine'
        assert self._hole_end_course < self._pattern_height - 1, f'hole height is too large that it is exceeding the knit graph border'
        assert self._hole_start_course > 1, f'bind-off would fail if hole_start_course <= 1'
        #hole_height: the height of the hole
        self._hole_height = self._hole_end_course - self._hole_start_course + 1
        #hole_width
        self._hole_width = self._hole_end_wale - self._hole_start_wale + 1 

    # use self._hole_course_to_wale_ids to help with "connect hole bottom node ()"
    def get_hole_course_to_wale_ids(self):
        for node in self._node_to_delete:
            course_id = self.node_to_course_and_wale[node][0]
            wale_id = self.node_to_course_and_wale[node][1]
            if course_id not in self._hole_course_to_wale_ids:
                self._hole_course_to_wale_ids[course_id] = [wale_id]
            else:
                self._hole_course_to_wale_ids[course_id].append(wale_id)
        # instead of limiting number of wale_ids on every course to be less than 4(the racking constraint), the width of first course for hole is the only factor that matters 
        # refer to an example on pp. 56 of the slides
        assert len(self._hole_course_to_wale_ids[self._hole_start_course]) <= 4, f'hole width is too large to achieve the racking bound by 2 on the machine'
        print(f'hole_course_to_wale_ids is {self._hole_course_to_wale_ids}')

    def get_course_id_to_wale_ids(self):
        for course_id in self._course_to_loop_ids.keys():
            start_node = self._course_to_loop_ids[course_id][0]
            last_node = self._course_to_loop_ids[course_id][-1]
            start_wale_id = self.node_to_course_and_wale[start_node][1]
            last_wale_id = self.node_to_course_and_wale[last_node][1]
            self.course_id_to_wale_ids[course_id] = []
            if self.object_type == 'sheet':
                if course_id % 2 == 0:
                    for wale_id in range(start_wale_id, last_wale_id+1):
                        self.course_id_to_wale_ids[course_id].append(wale_id)
                if course_id % 2 == 1:
                    for wale_id in range(start_wale_id, last_wale_id-1, -1):
                        self.course_id_to_wale_ids[course_id].append(wale_id)
            # below does not work for decreased tube. rewrite.
            # elif self.object_type == 'tube':
            #     # for tube case, the first wale_id on each course in self.course_id_to_wale_ids is always the smallest one, and vice versa. 
            #     for wale_id in range(start_wale_id, last_wale_id+1):
            #         self.course_id_to_wale_ids[course_id].append(wale_id)
            elif self.object_type == 'tube':
                # for tube case, the first wale_id on each course in self.course_id_to_wale_ids is always the smallest one, and vice versa. 
                for loop_id in self._course_to_loop_ids[course_id]:
                    wale_id = self._loop_id_to_wale[loop_id]
                    self.course_id_to_wale_ids[course_id].append(wale_id)
        print(f'self.course_id_to_wale_ids is {self.course_id_to_wale_ids}')

    def hole_location_warnings(self):
        """
        check if any ready-to-be-hole node might break any special stitch or suspicious for lacking some property,
        signaling something might go wrong with the given knit graph.
        """
        for node in self._node_to_delete:
            #first, each node should have exactly one parent. 
            #If more than one, it is part of a decrease; If less than one, it itself is an increase.
            parent_ids = [*self._knit_graph.graph.predecessors(node)]
            child_ids = [*self._knit_graph.graph.successors(node)]
            if len(parent_ids) != 1:
                # warnings.warn("xxx")
                print(f'Warning: node {node} might break a special stitch for having {len(parent_ids)} parents')
            #Likewise, each node should have exactly one child (it can only be one or zero child).
            #If no child, it might be a node on top course/top border, which we do not consider. 
            #Or simply it can be an error node in the knit graph signaling something wrong with the program.
            if len(child_ids) != 1:
                print(f'Warning: node {node} is suspicious or a node on top border for for having {len(child_ids)} child')
            #Second, on knit graph, any edge related to the node must have a parent offset that is 0.
            #If not, it is part of decrease or cable.
            if len(parent_ids) != 0:
                for parent_id in parent_ids:
                    parent_offset = self._knit_graph.graph[parent_id][node]["parent_offset"]
                    if parent_offset != 0:
                        print(f'Warning: node {node} might break a special stitch for having parent offset of {parent_offset}')
            #the sample applies to child_offset
            if len(child_ids) != 0:
                child_id = child_ids[0] # no "for child_id in child_ids[0]:" here because a node can have <= 1 child on the knit graph
                child_offset = self._knit_graph.graph[node][child_id]["parent_offset"]
                if child_offset != 0:
                    print(f'Warning: node {node} might break a special stitch for having child offset of {child_offset}')
            #Third, on yarn graph, the number of yarn edges related to the node must be 2
            #If less than one, it is either the start node or end node of the yarn, or a huge error when adding loop with the yarn :)
            yarn_parent_ids = [*self._old_yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*self._old_yarn.yarn_graph.successors(node)]
            if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                print(f'Warning: node {node} is suspicious for having no parent node or child node on yarn')
            #Fourth, on yarn graph, parent node and child node of the node should be on the same course
            #If not, it might be part of short row, or a node on the border. Currently, we do not consider add hole on border.
            if len(yarn_parent_ids) != 0 and len(yarn_child_ids) != 0:
                parent_id = yarn_parent_ids[0]
                child_id = yarn_child_ids[0]
                if self.node_to_course_and_wale[parent_id][0] != self.node_to_course_and_wale[child_id][0]:
                    print(f'Warning: node {node} might break a special stitch or a node on border for having parent node and child node on yarn graph that are not on the same course')
            
    def hole_location_errors(self):
        for node in self._node_to_delete:
            #First, if a node has no child and is not a node on top course/top border 
            #it would be an error/unstable node in the knit graph signaling something wrong with the given knitgraph.
            parent_ids = [*self._knit_graph.graph.predecessors(node)]
            child_ids = [*self._knit_graph.graph.successors(node)]
            course_id = self.node_to_course_and_wale[node][0]
            top_course_id = self._pattern_height - 1
            if len(child_ids) < 1 and course_id != top_course_id:
                print(f'Error: node {node} is suspicious for for having {len(child_ids)} child')
                exit()
        #Second, on yarn graph, the number of yarn edges related to the node must be 2
        #If less than one, and is not the start node or end node of the yarn, it would be a huge error when adding loop with the yarn
        for node in self._old_yarn.yarn_graph.nodes:
            yarn_parent_ids = [*self._old_yarn.yarn_graph.predecessors(node)]
            yarn_child_ids = [*self._old_yarn.yarn_graph.successors(node)]
            if node not in [0, len(self._old_yarn.yarn_graph.nodes)-1]:
                if len(yarn_parent_ids) != 1 or len(yarn_child_ids) != 1:
                    print(f'Error: node {node} is suspicious for having no parent node or child node on yarn')
                    exit()
 
    def hole_shape_and_number_constraints(self):
        # first, get the wale_id for hole nodes on each course
        course_id_to_wale_ids = {}
        for node in self._node_to_delete:
            course_id = self.node_to_course_and_wale[node][0]
            wale_id = self.node_to_course_and_wale[node][1]
            if course_id not in course_id_to_wale_ids:
                course_id_to_wale_ids[course_id] = [wale_id]
            else:
                course_id_to_wale_ids[course_id].append(wale_id)
        print('course_id_to_wale_ids', course_id_to_wale_ids)
        # special case to consider
        if len(self._node_to_delete) == 2:
            node1 = self._node_to_delete[0]
            node2 = self._node_to_delete[1]
            course_id1 = self.node_to_course_and_wale[node1][0]
            course_id2 = self.node_to_course_and_wale[node2][0]
            wale_id1 = self.node_to_course_and_wale[node1][1]
            wale_id2 = self.node_to_course_and_wale[node2][1]
            if course_id1 != course_id2 and wale_id1 != wale_id2:
                print(f'hole nodes {self._node_to_delete} is detected to be non-rectangular, more than two yarns will be needed, which is not yet supported in our project')
                exit()
        # second, get the smallest wale id and biggest wale id on each course
        smallest_wale_ids = []
        biggest_wale_ids = []
        for course_id, wale_ids in course_id_to_wale_ids.items():
            smallest_wale_ids.append(min(wale_ids))
            biggest_wale_ids.append(max(wale_ids))
        print(f'set(smallest_wale_ids) is {set(smallest_wale_ids)}, set(biggest_wale_ids) is {set(biggest_wale_ids)}')
        # finally, ensure wale id in smallest_wale_ids and those in biggest_wale_ids are consistent
        if len(set(smallest_wale_ids)) != 1 or len(set(biggest_wale_ids)) != 1:
            print(f'hole nodes {self._node_to_delete} is detected to be non-rectangular, more than two yarns will be needed, which is not yet supported in our project')
            exit()

    def remove_hole_nodes_from_graph(self):
        """
        remove the nodes for hole from both knit graph and yarn
        """
        self._knit_graph.graph.remove_nodes_from(self._node_to_delete)
        self._old_yarn.yarn_graph.remove_nodes_from(self._node_to_delete)
        print('course_to_loop_ids before remove hole is', self._course_to_loop_ids)
    
    def get_start_and_end_wale_id_per_course(self):
        course_id_to_start_wale_id = {}
        course_id_to_end_wale_id = {}
        if self.is_polygon == True:
            for start_keynode in self.starting_nodes_coor:
                course_id = start_keynode[0]
                start_wale_id = start_keynode[1]
                course_id_to_start_wale_id[course_id] = start_wale_id
            for end_keynode in self.ending_nodes_coor:
                course_id = end_keynode[0]
                end_wale_id = end_keynode[1]
                course_id_to_end_wale_id[course_id] = end_wale_id
        else:
            for course_id in self._course_to_loop_ids.keys():
                if course_id % 2 == 0:
                    start_keynode = self._course_to_loop_ids[course_id][0]
                    start_wale_id = self.node_to_course_and_wale[start_keynode][1]
                    end_keynode = self._course_to_loop_ids[course_id][-1]
                    end_wale_id = self.node_to_course_and_wale[end_keynode][1]
                    course_id_to_start_wale_id[course_id] = start_wale_id
                    course_id_to_end_wale_id[course_id] = end_wale_id
                elif course_id % 2 == 1:
                    start_keynode = self._course_to_loop_ids[course_id][-1]
                    start_wale_id = self.node_to_course_and_wale[start_keynode][1]
                    end_keynode = self._course_to_loop_ids[course_id][0]
                    end_wale_id = self.node_to_course_and_wale[end_keynode][1]
                    course_id_to_start_wale_id[course_id] = start_wale_id
                    course_id_to_end_wale_id[course_id] = end_wale_id
        self.course_id_to_start_wale_id = course_id_to_start_wale_id
        self.course_id_to_end_wale_id = course_id_to_end_wale_id
    
    # @deprecated
    def get_new_yarn_loop_ids(self):
        """
        Provided the hole_start_course, no matter what the yarn starting direction is, i.e., from left to right or from right
        to left, the loop ids that should be re-assigned to a new yarn can be determined by if the hole_start_course is an 
        odd number or even number, though the use of wale id and course id.
        """
        new_yarn_course_to_loop_ids: Dict[float, List[int]]= {}
        old_yarn_course_to_margin_loop_ids: Dict[float, List[int]]= {}
        new_yarn_course_to_margin_loop_ids: Dict[float, List[int]]= {}
        # self.get_start_and_end_wale_id_per_course()
        if self._hole_start_course % 2 == 0:
            #new yarn spread between the hole_end_wale and the last wale_id, old yarn is between the wale_id = 0 to the hole_start_wale 
            for course_id in range(self._hole_start_course, self._hole_end_course + 1):
                if (course_id, self._hole_start_wale - 1) not in self.course_and_wale_to_node.keys():
                    print(f'no node is found on the old yarn margin {(course_id, self._hole_start_wale - 1)}')
                    # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}'
                else:
                    old_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, self._hole_start_wale - 1)]
                if (course_id, self._hole_end_wale + 1) not in self.course_and_wale_to_node.keys():
                    print(f'no node is found on the new yarn margin {(course_id, self._hole_end_wale + 1)}')
                    # assert (course_id, hole_end_wale + 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_end_wale + 1)}'
                else:
                    new_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, self._hole_end_wale + 1)]
                new_yarn_course_to_loop_ids[course_id] = []
                start_wale = self.course_id_to_start_wale_id[course_id]
                # if course_id % 2 == 0:
                #     delimit = self._hole_end_wale - start_wale + 1
                #     new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id][delimit:]
                # elif course_id % 2 == 1:
                #     delimit = len(self._course_to_loop_ids[course_id]) - (self._hole_end_wale - start_wale + 1)
                #     new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id][:delimit]
                if course_id % 2 == 0:
                    for wale_id in range(self._hole_end_wale + 1, self.course_id_to_end_wale_id[course_id]+1):
                        if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].append(self.course_and_wale_to_node[(course_id, wale_id)])
                elif course_id % 2 == 1:
                    for wale_id in range(self._hole_end_wale + 1, self.course_id_to_end_wale_id[course_id]+1):
                        if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].insert(0, self.course_and_wale_to_node[(course_id, wale_id)])
            if self._hole_height % 2 == 0:
                pass
            elif self._hole_height % 2 == 1:
                for course_id in range(self._hole_end_course + 1, self._pattern_height):
                    new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id]

        if self._hole_start_course % 2 == 1:
            #Contrary to the above,
            #new yarn spread between the wale_id = 0 to the hole_start_wale, old yarn is between the hole_end_wale and the last wale_id
            for course_id in range(self._hole_start_course, self._hole_end_course + 1):
                if (course_id, self._hole_end_wale + 1) not in self.course_and_wale_to_node.keys():
                    print(f'no node is found on the old yarn margin {(course_id, self._hole_end_wale + 1)}')
                    # assert (course_id, hole_end_wale + 1) in course_and_wale_to_node.keys(), f'no node is found on old yarn the margin {(course_id, hole_end_wale + 1)}'
                else:
                    old_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, self._hole_end_wale + 1)]
                if  (course_id, self._hole_start_wale - 1) not in self.course_and_wale_to_node.keys():
                    print(f'no node is found on the new yarn margin {(course_id, self._hole_start_wale - 1)}')
                    # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}'
                else:
                    new_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, self._hole_start_wale - 1)]
                new_yarn_course_to_loop_ids[course_id] = []
                start_wale = self.course_id_to_start_wale_id[course_id]
                # if course_id % 2 == 0:
                #     delimit =  self._hole_start_wale - start_wale
                #     new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id][:delimit]
                # elif course_id % 2 == 1:
                #     delimit =  len(self._course_to_loop_ids[course_id]) - self._hole_start_wale 
                #     new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id][delimit:]
                if course_id % 2 == 0:
                    for wale_id in range(self.course_id_to_start_wale_id[course_id], self._hole_start_wale):
                        if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].append(self.course_and_wale_to_node[(course_id, wale_id)])
                elif course_id % 2 == 1:
                    for wale_id in range(self.course_id_to_start_wale_id[course_id], self._hole_start_wale):
                        if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                            new_yarn_course_to_loop_ids[course_id].insert(0, self.course_and_wale_to_node[(course_id, wale_id)])
            if self._hole_height % 2 == 0:
                pass
            elif self._hole_height % 2 == 1:
                for course_id in range(self._hole_end_course + 1, self._pattern_height):
                    new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id]

        print('old_yarn_course_to_margin_loop_ids', old_yarn_course_to_margin_loop_ids)
        print('new_yarn_course_to_margin_loop_ids', new_yarn_course_to_margin_loop_ids)
        print('new_yarn_course_to_loop_ids', new_yarn_course_to_loop_ids)
        return new_yarn_course_to_loop_ids, old_yarn_course_to_margin_loop_ids

    # @deprecated
    def reconnect_old_yarn_at_margin(self, old_yarn_course_to_margin_loop_ids):
        """
        reconnect nodes on old yarn margin (margin refers to the left wale and right wale around the hole).
        """
        if self._hole_start_course % 2 == 0:
            for course_id in old_yarn_course_to_margin_loop_ids: 
                if course_id%2 == 0 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                    start_node = old_yarn_course_to_margin_loop_ids[course_id]
                    next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                    self._old_yarn.yarn_graph.add_edge(start_node, next_node)
        elif self._hole_start_course % 2 == 1:
            for course_id in old_yarn_course_to_margin_loop_ids: 
                if course_id%2 == 1 and course_id + 1 in old_yarn_course_to_margin_loop_ids:
                    start_node = old_yarn_course_to_margin_loop_ids[course_id]
                    next_node = old_yarn_course_to_margin_loop_ids[course_id+1]
                    self._old_yarn.yarn_graph.add_edge(start_node, next_node)

    def find_shortest_path_for_sheet(self):
        G1 = nx.DiGraph()
        # add stitch paths
        for parent_id, child_id in self._knit_graph.graph.edges:
            G1.add_edge(parent_id, child_id, weight = -1)
        # additional stitch edges processing is needed for some cases. For example, for cable case, if we only rely on existing cable edges, some node would become
        # isolated and in the end leading to no feasible solution. For more details, please refer to pp.44 in Slide 'KnitGraph'.
        # to avoid "dictionary changed size during iteration" error
        # for node in G1.nodes: 
        for node in self.node_to_course_and_wale.keys():
            wale_id = self.node_to_course_and_wale[node][1]
            course_id = self.node_to_course_and_wale[node][0]
            #node right above it
            if (course_id+1, wale_id) in self.node_to_course_and_wale.values():
                above_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                if above_node not in self._node_to_delete:
                    if (node, above_node) not in G1.edges():
                        G1.add_edge(node, above_node, weight = -1)
        # More stitch processing is needed to be able to create holes of different shapes, for example, refer to pp.51 in Slide 'KnitGraph' for the diamond hole.
        # to be able to do this, we connect each node to the three nearest neighbor nodes on the next above course
        # for node in G1.nodes:
        for node in self.node_to_course_and_wale.keys():
            wale_id = self.node_to_course_and_wale[node][1]
            course_id = self.node_to_course_and_wale[node][0]
            #node right above it
            if (course_id+1, wale_id) in self.node_to_course_and_wale.values():
                above_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                G1.add_edge(node, above_node, weight = -1)
            #node one wale left above it
            if (course_id+1, wale_id-1) in self.node_to_course_and_wale.values():
                left_above_node = self.course_and_wale_to_node[(course_id+1, wale_id-1)]
                G1.add_edge(node, left_above_node, weight = -1)
            #node one wale right above it
            if (course_id+1, wale_id+1) in self.node_to_course_and_wale.values():
                right_above_node = self.course_and_wale_to_node[(course_id+1, wale_id+1)]
                G1.add_edge(node, right_above_node, weight = -1)
        # add yarn paths (adding yarn path is put at the last place because )
        for prior_node, next_node in self._old_yarn.yarn_graph.edges:
            G1.add_edge(prior_node, next_node, weight = -10)
            # below two syntax works too
            # nx.add_path(G, [prior_node, next_node], distance = 1)
            # G.edges[prior_node, next_node]['distance'] = 1
        # the reason we preprocess the KnitGraph before remove the hole nodes is to avoid the the potential error "RuntimeError: dictionary changed size during iteration"
        # caused by "for node in G1.nodes: xxx"
        G1.remove_nodes_from(self._node_to_delete)
        # has to remove nodes on knitgraph and old yarn graph as well, because we are gonna use old yarn graph below to get "all_yarn_edges"
        self._knit_graph.graph.remove_nodes_from(self._node_to_delete)
        self._old_yarn.yarn_graph.remove_nodes_from(self._node_to_delete)
        print('all edges', G1.edges)
        # we use bellman-ford rather than dijkstra because the former can deal with negative weighted graph while the latter cannot.
        # note that the shortest_path() below does not include "target" param, what it returns is the shortest path to all other nodes on the graph
        shortest_paths = nx.shortest_path(G1, source=0, weight='weight', method = 'bellman-ford')
        print(f'len(shortest_paths) is {len(shortest_paths)}')
        # shortest_paths = nx.shortest_path(G1,source=0,target=55, weight='weight', method = 'dijkstra')
        # get dict whose keys are reward, and values are corresponding shortest path
        d_reward_to_path = {}
        for destination in shortest_paths.keys():
            reward = nx.shortest_path_length(G1, source = 0, target = destination, weight = 'weight', method = 'bellman-ford')
            # negative weight is not applicable to djikstra 
            # reward = nx.dijkstra_path_length(G1, source = 0, target = destination)
            # print('reward', reward)
            if reward not in d_reward_to_path:
                d_reward_to_path[reward] = [shortest_paths[destination]]
            else:
                d_reward_to_path[reward].append(shortest_paths[destination])
        print(f'd_reward_to_path is {d_reward_to_path}')
        print(f'sorted(d_reward_to_path) is {sorted(d_reward_to_path.items())}, len is {len(sorted(d_reward_to_path.items()))}')
        # get complete node set
        all_nodes = set(G1.nodes)
        # get complete yarn edge set
        all_yarn_edges = set(self._old_yarn.yarn_graph.edges)
        # iterate over the dict "d_reward_to_path" according to ascending order of reward (i.e, from smaller to larger, since reward is a non-positive number due to
        # negative weights in our graph, thus shortest path on old yarn has smallest reward (most negative), in other words, the longest path)
        for reward, paths_on_old_yarn in sorted(d_reward_to_path.items()):
            # print(f'reward is {reward}, paths_on_old_yarn is {paths_on_old_yarn}, len(paths_on_old_yarn) is {len(paths_on_old_yarn)}')
            # add node on old yarn in the set
            for path_on_old_yarn in paths_on_old_yarn:
                # if not copy but instead using "G1_for_new_yarn = G1", any action taken on updated_G1 will be applied to G1, which is unwanted
                # G1_for_new_yarn = nx.DiGraph()
                G1_for_new_yarn = G1.copy()
                # initialize node set for old yarn and new yarn
                node_on_old_yarn = set()
                node_on_new_yarn = set()
                # initialize yarn edge set for old yarn and new yarn
                old_yarn_edges = set()
                new_yarn_edges = set()
                for node in path_on_old_yarn:
                    node_on_old_yarn.add(node)
                # add yarn edges on old yarn in the set
                for i in range(len(path_on_old_yarn)-1):
                    prior_node = path_on_old_yarn[i]
                    next_node = path_on_old_yarn[i+1]
                    yarn_edge = (prior_node, next_node)
                    old_yarn_edges.add(yarn_edge)
                # identify starting node and destination node from the remain nodes excluding node_on_old_yarn
                remain_nodes = all_nodes.difference(node_on_old_yarn)
                if len(remain_nodes) != 0:
                    print('remain_nodes', remain_nodes)
                    destination = max(remain_nodes)
                    start_node = min(remain_nodes)
                    print(f'start_node is {start_node}, destination is {destination}')
                    # get shortest_path from start_node to destination in remain_nodes set
                    # note that we need to update the graph for new yarn to go through after assigning the nodes to old yarn
                    print('G1 before update', G1_for_new_yarn)
                    # now it becomes real "G1_for_new_yarn"
                    G1_for_new_yarn.remove_nodes_from(path_on_old_yarn)
                    print('path', path_on_old_yarn)
                    print('updated G1', G1_for_new_yarn)
                    print(f'G1_for_new_yarn.nodes is {G1_for_new_yarn.nodes}, G1_for_new_yarn.edges is {G1_for_new_yarn.edges}')
                    print('node_on_old_yarn', node_on_old_yarn)
                    print('set(G1_for_new_yarn.nodes) == remain_nodes', set(G1_for_new_yarn.nodes) == remain_nodes)
                    if nx.has_path(G1_for_new_yarn, source = start_node, target = destination) == True:
                        # sp means shortest path
                        # note that shortest_path() below does include the "target" param, because for situation where we have only one hole on the graph, it can be guaranteed
                        # that with only two yarns, each node and each edge on the graph can be visited.
                        sp_on_new_yarn = nx.shortest_path(G1_for_new_yarn, source = start_node, target = destination, weight='weight', method = 'bellman-ford')
                    else: 
                        print(f"no path available for new yarn to walk on from start node {start_node} to destination node {destination}")
                        continue
                    # add node on new yarn in the set
                    for node in sp_on_new_yarn:
                        node_on_new_yarn.add(node)
                    # add yarn edges on new yarn in the set
                    for i in range(len(sp_on_new_yarn)-1):
                        prior_node = sp_on_new_yarn[i]
                        next_node = sp_on_new_yarn[i+1]
                        yarn_edge = (prior_node, next_node)
                        new_yarn_edges.add(yarn_edge)
                    # constraint 1: ensure union of node_on_new_yarn and node_on_old_yarn == all_node
                    if node_on_old_yarn.union(node_on_new_yarn) != all_nodes:
                        print("union of node_on_new_yarn and node_on_old_yarn != all_node")
                        continue
                    else:
                        print("union of node_on_new_yarn and node_on_old_yarn == all_node")
                    # constraint 2: ensure union of node_on_new_yarn and node_on_old_yarn == all_node
                    if all_yarn_edges.issubset(old_yarn_edges.union(new_yarn_edges)) == False:
                        print("all_yarn_edges.issubset(old_yarn_edges.union(new_yarn_edges)) == False")
                        continue
                    else:
                        print("all_yarn_edges.issubset(old_yarn_edges.union(new_yarn_edges)) == True")
                    print(f'highest reward is {reward}, path for old yarn is {path_on_old_yarn}, while path for new yarn is {sp_on_new_yarn}')
                    # when two path on two yarn can satisfy the above two constraints, the for loop would break
                    return path_on_old_yarn, sp_on_new_yarn
                
                elif len(remain_nodes) == 0:
                    print(f'old yarn is sufficient to walk through all nodes on the graph, highest reward is {reward}, path for old yarn is {path_on_old_yarn}')
                    return path_on_old_yarn
        

    def find_shortest_path_for_tube(self):
            G1 = nx.DiGraph()   
            # First, preprocessing: add more edges to the graph to make the path searching problem solvable
            def preprocessing_on_graph(G):
                # 1. add yarn paths of opposite direction in addition to the original direction for any neighbor nodes on the same course
                for prior_node, next_node in self._old_yarn.yarn_graph.edges:
                    # different from sheet, for a tube, the yarn edge/yarn path needs to be walkable in both left and right direction, otherwise the problem tend to be
                    # have no solution
                    G1.add_edge(prior_node, next_node, weight = -10)
                    # add an edge that is exactly of opposite direction again if they are on the same course
                    if self.node_to_course_and_wale[prior_node][0] == self.node_to_course_and_wale[next_node][0]:
                        G1.add_edge(next_node, prior_node, weight = -10)
                # 2. add edge of two opposite direction between the start node and end node on each course
                for course_id in self._course_to_loop_ids.keys():
                    start_node = self._course_to_loop_ids[course_id][0]
                    end_node = self._course_to_loop_ids[course_id][-1]
                    G1.add_edge(start_node, end_node, weight = -10)
                    G1.add_edge(end_node, start_node, weight = -10)
                # 3. add stitch paths, for each node, it should have three stitch edges, one is connected with node right above it, one is one wale left above it, and one
                # is one wale right above it. first node and last node on each course is special node, thus need separate discussion as below.
                for node in G1.nodes:
                    wale_id = self.node_to_course_and_wale[node][1]
                    course_id = self.node_to_course_and_wale[node][0]
                    # connect until the second highest course
                    if course_id < max([*self._course_to_loop_ids.keys()]):
                        # for first node on each course
                        if node == self._course_to_loop_ids[course_id][0]:
                            #node right above it
                            if (course_id+1, wale_id) in self.node_to_course_and_wale.values():
                                above_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                                G1.add_edge(node, above_node, weight = -1)
                               
                            #node one wale right above it
                            if (course_id+1, wale_id+self.wale_dist) in self.node_to_course_and_wale.values():
                                right_above_node = self.course_and_wale_to_node[(course_id+1, wale_id+self.wale_dist)]
                                G1.add_edge(node, right_above_node, weight = -1)
                               
                            #last node on next course
                            if course_id+1 in self._course_to_loop_ids.keys():
                                target_node = self._course_to_loop_ids[course_id+1][-1]
                                G1.add_edge(node, target_node, weight = -1)
                                
                            # print(f'node is {node}, {(node, above_node), (node, right_above_node), (node, target_node)}')
                        # for last node on each course
                        elif node == self._course_to_loop_ids[course_id][-1]:
                            #node right above it
                            if (course_id+1, wale_id) in self.node_to_course_and_wale.values():
                                above_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                                G1.add_edge(node, above_node, weight = -1)
                                
                            #node one wale left above it
                            if (course_id+1, wale_id-self.wale_dist) in self.node_to_course_and_wale.values():
                                left_above_node = self.course_and_wale_to_node[(course_id+1, wale_id-self.wale_dist)]
                                G1.add_edge(node, left_above_node, weight = -1)
                                
                            #first node on next course
                            if course_id+1 in self._course_to_loop_ids.keys():
                                target_node = self._course_to_loop_ids[course_id+1][0]
                                G1.add_edge(node, target_node, weight = -1)
                            
                            # print(f'node is {node}, {(node, above_node), (node, left_above_node), (node, target_node)}')
                        # updated as below for node in between on each course, because prior method does not work for decreased tube, specifically, the last node on the front
                        # side of the tube and the first node on the back side of the tube. thus, rewrite the part as below
                        # for node in beweetn on each course 
                        else:
                            #node right above it
                            if (course_id+1, wale_id) in self.node_to_course_and_wale.values():
                                above_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                                G1.add_edge(node, above_node, weight = -1)
                                
                            # print(f'here1: node is {node}, above node is {above_node}, wale id is {wale_id}, {(course_id+1, wale_id)}, {(course_id+1, wale_id) in self.node_to_course_and_wale.values()}')
                            # print(f'here1: node is {node}, above node is {above_node}, wale id is {wale_id}, {(course_id+1, wale_id)}, {self.course_and_wale_to_node[(course_id+1, wale_id)]}')
                            #node one wale left above it
                            wale_ids_on_above_course = self.course_id_to_wale_ids[course_id+1]
                            # first get the nearest neighbor with smaller wale
                            # below work for normal tube but does not work for decreased tube. rewrite.
                            # min_wale_difference_for_smaller_wale = wale_id - wale_ids_on_above_course[0]
                            min_wale_difference_for_smaller_wale = wale_id 
                            # print(f'min_wale_difference_for_smaller_wale1 is {min_wale_difference_for_smaller_wale}')
                            wale_of_smaller_nearest_neighbor = wale_ids_on_above_course[0]
                            for wale_id_above_course in wale_ids_on_above_course:
                                wale_difference = wale_id -  wale_id_above_course
                                if wale_difference > 0 and wale_difference < min_wale_difference_for_smaller_wale:
                                    min_wale_difference_for_smaller_wale = wale_difference
                                    wale_of_smaller_nearest_neighbor = wale_id_above_course
                            # print(f'min_wale_difference_for_smaller_wale2 is {min_wale_difference_for_smaller_wale}')
                            if (course_id+1, wale_of_smaller_nearest_neighbor) in self.node_to_course_and_wale.values():
                                left_above_node = self.course_and_wale_to_node[(course_id+1, wale_of_smaller_nearest_neighbor)]
                                # print(f'node is {node}, left_above_node is {left_above_node}')
                                G1.add_edge(node, left_above_node, weight = -1)
                            #node one wale right above it
                            # then get the nearest neighbor with bigger wale
                            # first get the nearest neighbor with smaller wale
                            # below work for normal tube but does not work for decreased tube. rewrite.
                            # min_wale_difference_for_bigger_wale = wale_ids_on_above_course[-1] - wale_id 
                            min_wale_difference_for_bigger_wale = 10000
                            # print(f'min_wale_difference_for_bigger_wale1 is {min_wale_difference_for_bigger_wale}')
                            wale_of_bigger_nearest_neighbor = wale_ids_on_above_course[-1]
                            # print(f'wale_ids_on_above_course is {wale_ids_on_above_course}')
                            for wale_id_above_course in wale_ids_on_above_course:
                                wale_difference = wale_id_above_course - wale_id 
                                if wale_difference > 0 and wale_difference < min_wale_difference_for_bigger_wale:
                                    min_wale_difference_for_bigger_wale = wale_difference
                                    wale_of_bigger_nearest_neighbor = wale_id_above_course
                            # print(f'min_wale_difference_for_bigger_wale2 is {min_wale_difference_for_bigger_wale}')
                            if (course_id+1, wale_of_bigger_nearest_neighbor) in self.node_to_course_and_wale.values():
                                right_above_node = self.course_and_wale_to_node[(course_id+1, wale_of_bigger_nearest_neighbor)]
                                # print(f'node is {node}, right_above_node is {right_above_node}')
                                G1.add_edge(node, right_above_node, weight = -1)    
                            # print(f'node is {node}, {(node, above_node), (node, left_above_node), (node, right_above_node)}')
                print('all edges', G1.edges)
            '''
            # Second, path search algorithm for the graph of tube with a hole
            def path_search(G, yarn:str):
                # for old yarn, source node always starts from 0
                if yarn == 'old':
                    source_node = 0
                    visited_nodes = [0]
                    curr_course_id = 0
                elif yarn == 'new':
                    source_node = min(set(G.nodes))
                    visited_nodes = [source_node]
                    curr_course_id = self.node_to_course_and_wale[source_node][0]
                reward = 0
                course_nodes = []
                
                while source_node != None:
                    print('source_node', source_node)
                    reward_dict = {}
                    course_id = self.node_to_course_and_wale[source_node][0]
                    print('course_id', course_id)
                    total_num_of_nodes_each_course = len(self._course_to_loop_ids[course_id])
                    if course_id != curr_course_id:
                        course_nodes = []
                        # course_nodes.append(source_node)
                        curr_course_id = course_id
                    course_nodes.append(source_node)
                    print('course_nodes', course_nodes)
                    if len(course_nodes) == total_num_of_nodes_each_course:
                        start_node_on_course = course_nodes[0]
                        wale_id = self.node_to_course_and_wale[start_node_on_course][1]
                        flag = 0
                        for edge in G.out_edges(start_node_on_course):
                            edge_end_node = edge[1]
                            if edge_end_node in visited_nodes:
                                continue
                            else:
                                flag = 1
                                visited_nodes.append(edge_end_node)
                                reward += G.edges[start_node_on_course, edge_end_node]['weight']
                                source_node = edge_end_node
                                print('end_node when len(course_nodes) == total_num_of_nodes_each_course', edge_end_node)
                                break
                        if flag == 0:
                            print(f"no node in next course to begin a new course, visited nodes so far is {visited_nodes}")
                            break
                    else:
                        for edge in G.out_edges(source_node):
                            reward_dict[edge] = G.edges[edge[0], edge[1]]['weight']
                        print('reward_dict', reward_dict)
                        sorted_reward_dict = {k: v for k, v in sorted(reward_dict.items(), key=lambda item: item[1])}
                        flag = 0
                        for edge, weight in sorted_reward_dict.items():
                            edge_end_node = edge[1]
                            if edge_end_node in visited_nodes:
                                continue
                            else:
                                flag = 1
                                visited_nodes.append(edge_end_node)
                                reward += weight
                                source_node = edge_end_node
                                print('end_node', edge_end_node)
                                break
                        if flag == 0:
                            print(f"no next node available due to all have been visited before, visited nodes so far is {visited_nodes}") 
                            break
                return visited_nodes
            '''
            # perform preprocessing on the graph
            preprocessing_on_graph(G1)
            # remove hole nodes
            # the reason we preprocess the KnitGraph before remove the hole nodes is to avoid the the potential error "RuntimeError: dictionary changed size during iteration"
            # caused by "for node in G1.nodes: xxx"
            G1.remove_nodes_from(self._node_to_delete)
            # record all nodes excluding hole nodes
            all_nodes = set(G1.nodes)
            # perform path search algorithm on the graph of tube with a hole
            visited_nodes_old_yarn = self.path_search(G1, yarn = "old")
            # get the remain nodes that are not on old yarn
            remain_nodes = all_nodes.difference(visited_nodes_old_yarn)
            print('remain nodes', remain_nodes)
            # if len(remain_nodes) != 0:
            #     # before searching for the path, first delete the nodes in the visited_nodes
            #     G1.remove_nodes_from(visited_nodes_old_yarn)
            #     # perform path search algorithm on the updated graph
            #     visited_nodes_new_yarn = path_search(G1, yarn = "new")
            #     # if visited_nodes_new_yarn == remain_nodes, meaning that new yarn can walk through all the remain nodes, thus two yarns are sufficient for establishing a
            #     # tube with a hole
            #     if set(visited_nodes_new_yarn) == remain_nodes:
            #         print(f'two yarns are sufficient for establishing this knit graph of a tube with a hole! Specifically, nodes on old yarn is {visited_nodes_old_yarn},\
            #         nodes on new yarn is {visited_nodes_new_yarn}')
            #         return visited_nodes_old_yarn, visited_nodes_new_yarn
            # else:
            #     print(f'only old yarn is sufficient to walk through all nodes on the graph of a tube with a hole, and nodes on old yarn is {visited_nodes_old_yarn}')
            #     return visited_nodes_old_yarn
            G1.remove_nodes_from(visited_nodes_old_yarn)
            print(f'separate subgraphs in find_shortest_path_for_tube() are {list(nx.weakly_connected_components(G1))}')
            return visited_nodes_old_yarn, list(nx.weakly_connected_components(G1)), G1

    # Second, path search algorithm for the graph of tube with a hole
    def path_search(self, G, yarn: Optional[str] = None):
        # for old yarn, source node always starts from 0
        if yarn == 'old':
            source_node = 0
            visited_nodes = [0]
            curr_course_id = 0
        else:
            source_node = min(set(G.nodes))
            visited_nodes = [source_node]
            curr_course_id = self.node_to_course_and_wale[source_node][0]
        reward = 0
        course_nodes = []
        
        while source_node != None:
            print('source_node', source_node)
            reward_dict = {}
            course_id = self.node_to_course_and_wale[source_node][0]
            print('course_id', course_id)
            total_num_of_nodes_each_course = len(self._course_to_loop_ids[course_id])
            if course_id != curr_course_id:
                course_nodes = []
                # course_nodes.append(source_node)
                curr_course_id = course_id
            course_nodes.append(source_node)
            print('course_nodes', course_nodes)
            if len(course_nodes) == total_num_of_nodes_each_course:
                start_node_on_course = course_nodes[0]
                wale_id = self.node_to_course_and_wale[start_node_on_course][1]
                flag = 0
                for edge in G.out_edges(start_node_on_course):
                    edge_end_node = edge[1]
                    if edge_end_node in visited_nodes:
                        continue
                    else:
                        flag = 1
                        visited_nodes.append(edge_end_node)
                        reward += G.edges[start_node_on_course, edge_end_node]['weight']
                        source_node = edge_end_node
                        print('end_node when len(course_nodes) == total_num_of_nodes_each_course', edge_end_node)
                        break
                if flag == 0:
                    print(f"no node in next course to begin a new course, visited nodes so far is {visited_nodes}")
                    break
            else:
                for edge in G.out_edges(source_node):
                    reward_dict[edge] = G.edges[edge[0], edge[1]]['weight']
                print('reward_dict', reward_dict)
                sorted_reward_dict = {k: v for k, v in sorted(reward_dict.items(), key=lambda item: item[1])}
                flag = 0
                for edge, weight in sorted_reward_dict.items():
                    edge_end_node = edge[1]
                    if edge_end_node in visited_nodes:
                        continue
                    else:
                        flag = 1
                        visited_nodes.append(edge_end_node)
                        reward += weight
                        source_node = edge_end_node
                        print('end_node', edge_end_node)
                        break
                if flag == 0:
                    print(f"no next node available due to all have been visited before, visited nodes so far is {visited_nodes}") 
                    break
        return visited_nodes

    # @deprecated
    def bring_new_yarn(self):
        """
        Create a new yarn with new carrier id.
        """
        self._new_yarn = Yarn(self.new_yarn_id, self._knit_graph, carrier_id=self._new_carrier)
        self._knit_graph.add_yarn(self._new_yarn)
   
    def bring_new_yarn(self):
        """
        Create a new yarn with new carrier id.
        """
        # self._new_carriers
        # self.new_yarn_ids
        hole_index = 0
        print(f'self.new_yarn_ids is {self.new_yarn_ids}, self._new_carriers is {self._new_carriers}')
        for new_yarn_id, carrier_id in zip(self.new_yarn_ids, self._new_carriers):
            print(f'new_yarn_id is {new_yarn_id}, carrier_id is {carrier_id}, type(carrier_id) is {type(carrier_id)}')
            new_yarn = Yarn(new_yarn_id, self._knit_graph, carrier_id=carrier_id)
            self._knit_graph.add_yarn(new_yarn)
            self._new_yarns[hole_index] = new_yarn
            hole_index += 1

    # @deprecated
    def deprecated_remove_old_and_add_new_yarn(self, new_yarn_course_to_loop_ids):    
        """
        remove loop_ids from old yarn and add loop_ids to new yarn.
        """
        for course_id in new_yarn_course_to_loop_ids:
            loop_ids = new_yarn_course_to_loop_ids[course_id]
            for loop_id in loop_ids:
                self._old_yarn.yarn_graph.remove_node(loop_id)
                child_id, loop = self._new_yarn.add_loop_to_end(loop_id = loop_id)
        print(f'old yarn edges are {self._old_yarn.yarn_graph.edges}')
        print(f'new yarn edges are {self._new_yarn.yarn_graph.edges}')
    
    def remove_old_and_add_new_yarn(self, need_new_yarn: bool, path: Union[List[int], Tuple[List[int], List[int]]], remain_subgraphs, G1):    
        """
        remove loop_ids from old yarn and add loop_ids to new yarn.
        """
        # print(f'old yarn carrier id is {self._old_yarn.yarn_id}, carrier id is {self._old_yarn.carrier.carrier_ids}')
        if need_new_yarn == True:
            self._new_yarn = Yarn(yarn_id = self.new_yarn_id, knit_graph = self._knit_graph, carrier_id = 4)
            self._knit_graph.add_yarn(self._new_yarn)
            visited_nodes_old_yarn = path[0]
            visited_nodes_new_yarn = path[1]
            # delete all nodes on old yarn and use the visited_nodes_old_yarn to walk the old yarn to form the new old yarn graph
            self._old_yarn.yarn_graph.remove_nodes_from(visited_nodes_new_yarn)
            self._old_yarn.yarn_graph.remove_nodes_from(visited_nodes_old_yarn)
            self._old_yarn.last_loop_id = None
            for loop_id in visited_nodes_old_yarn:
                child_id, loop = self._old_yarn.add_loop_to_end(loop_id = loop_id)
            for loop_id in visited_nodes_new_yarn:
                child_id, loop = self._new_yarn.add_loop_to_end(loop_id = loop_id)
            print(f'old yarn edges are {self._old_yarn.yarn_graph.edges}')
            print(f'new yarn edges are {self._new_yarn.yarn_graph.edges}')
        elif need_new_yarn == False:
            visited_nodes_old_yarn = path
            # delete all nodes on old yarn and use the visited_nodes_old_yarn to walk the old yarn to form the new old yarn graph
            # original 
            # self._old_yarn.yarn_graph.remove_nodes_from(visited_nodes_old_yarn)
            # updated for debugging
            self._old_yarn.yarn_graph.remove_nodes_from(self._knit_graph.graph.nodes)
            remain_nodes = set(self._knit_graph.graph.nodes).difference(set(visited_nodes_old_yarn))
            # self._knit_graph.graph.remove_nodes_from(remain_nodes)
            self._old_yarn.last_loop_id = None
            for loop_id in visited_nodes_old_yarn:
                child_id, loop = self._old_yarn.add_loop_to_end(loop_id = loop_id)
            new_yarns = []
            # threshold is set at 9 is because at most we have 10 yarns on the machines, while 1 is for old yarn already.
            while len(new_yarns) < 9:
                yarn_carrier_id = random.randint(1,10)
                if yarn_carrier_id!=self._old_yarn.carrier.carrier_ids and yarn_carrier_id not in new_yarns:
                    new_yarns.append(yarn_carrier_id)
                else:
                    continue
            for new_yarn_carrier_id in new_yarns:
                new_yarn_id = str(new_yarn_carrier_id)
                new_yarn = Yarn(new_yarn_id, self._knit_graph, carrier_id=new_yarn_carrier_id)
                self._knit_graph.add_yarn(new_yarn)
                self._new_yarns.append(new_yarn)
            # walk new yarns on remain subgraphs
            for i in range(len(remain_subgraphs)):
                G2 = G1.copy()
                subgraph = remain_subgraphs[i]
                new_yarn = self._new_yarns[i]
                # for loop_id in sorted(subgraph):
                #     child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
                other_subgraphs = []
                for other_subgraph in remain_subgraphs:
                    if other_subgraph != subgraph:
                        print(f'other_subgraph is {other_subgraph}')
                        other_subgraphs = other_subgraphs+list(other_subgraph)
                print(f'other_subgraphs is {other_subgraphs}, subgraph is {subgraph}, remain_subgraphs is {remain_subgraphs}')
                # nodes_to_remove = set(visited_nodes_old_yarn).union(other_subgraphs)
                G2.remove_nodes_from(other_subgraphs)
                print(f'G2 is {G2}, subgraph is {subgraph}')
                # bellman-ford algorithm below does not work because negative weighted cycle is introduced in the pre-processing phase
                # shortest_paths = nx.shortest_path(G2, source=min(subgraph), weight='weight', method = 'bellman-ford')
                path = self.path_search(G2)
                print(f'path is {path}')
                # for loop_id in sorted(shortest_paths):
                #     child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
                for loop_id in path:
                    child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
            # below is used to see how the remain nodes distributed on the graph and can be used to verify the correctness of newly added yarn walking
            # self._new_yarn = Yarn(yarn_id = self.new_yarn_id, knit_graph = self._knit_graph, carrier_id = 4)
            # self._knit_graph.add_yarn(self._new_yarn)
            # for loop_id in sorted(remain_nodes):
            #     child_id, loop = self._new_yarn.add_loop_to_end(loop_id = loop_id)
            
            '''
            # different from the result returned in the find_shortest_path_for_tube(), which is [{27, 39}, {32, 33, 34, 35, 29, 30, 31}], the result returned below is 
            # "[{27, 39}, {29}, {30}, {31}, {32}, {33}, {34}, {35}]", this is because in our self._knit_graph, it is only stitch graph, meaning that nodes on the same
            # course is not connected, and in our design, yarn graph is used to connect these nodes. thus, to correctly walk the newly added yarn to build the holes together,
            # we need to use the result returned in the find_shortest_path_for_tube().
            knit_graph_copied = self._knit_graph.graph.copy()
            knit_graph_copied.remove_nodes_from(visited_nodes_old_yarn)
            print(f'separate subgraphs are {list(nx.weakly_connected_components(knit_graph_copied))}')
            '''
            print(f'old yarn edges are {self._old_yarn.yarn_graph.edges}')
    
    def read_connectivity_from_knitgraph(self):
        """
        transform edge_data_list where connectivity is expressed in terms of node id into coor_connectivity where connectivity is
        expressed in terms of coordinate in formart of (course_id, wale_id). This transform is needed because we are going to 
        change the node order to represent the correct knitting operation order when knitting a pocket, thus at each coor, the node
        id would change, that's why we need to update node_to_course_and_wale for both parent graph and child graph.
        """
        knitgraph_edge_data_list = self._knit_graph.graph.edges(data=True)
        for edge_data in knitgraph_edge_data_list:
            node = edge_data[1]
            node_coor = self.node_to_course_and_wale[node]
            predecessor = edge_data[0]
            predecessor_coor = self.node_to_course_and_wale[predecessor]
            attr_dict = edge_data[2]
            self.knitgraph_coors_connectivity.append([predecessor_coor, node_coor, attr_dict])

    def rebuild_yarn_graph(self):
        yarns = [*self._knit_graph.yarns.values()]
        for yarn in yarns:
            # node_coor_order = []
            course_to_wale_ids = {}
            if len(yarn.yarn_graph.nodes) > 0:
                nodes_on_yarn = [*yarn.yarn_graph.nodes]
                for node in nodes_on_yarn:
                    course_id = self.node_to_course_and_wale[node][0]
                    if course_id not in course_to_wale_ids:
                        course_to_wale_ids[course_id] = [self.node_to_course_and_wale[node][1]]
                    else:
                        course_to_wale_ids[course_id].append(self.node_to_course_and_wale[node][1])
                    # del self.node_to_course_and_wale[node] 
                # print(f'course_to_wale_ids for {yarn.yarn_id} is {course_to_wale_ids}')    
                # update nodes on this yarn
                yarn.last_loop_id = None
                yarn.yarn_graph.remove_edges_from([*yarn.yarn_graph.edges])
                yarn.yarn_graph.remove_nodes_from(nodes_on_yarn)
                # self._knit_graph.graph.remove_nodes_from(nodes_on_yarn)
                # self.new_knit_graph.add_yarn(yarn)
                i = 0
                for course_id in sorted([*course_to_wale_ids.keys()]):
                    wale_ids = course_to_wale_ids[course_id]
                    # print(f'wale_ids is {wale_ids}')
                    for wale_id in wale_ids:
                        # print(f'nodes_on_yarn[i] is {nodes_on_yarn[i]}')
                        sorted_nodes_on_yarn = sorted(nodes_on_yarn) 
                        loop_id, loop = yarn.add_loop_to_end(loop_id = sorted_nodes_on_yarn[i])
                        # print(f'wale_id is {wale_id}, loop_id is {loop_id}')
                        self._knit_graph.add_loop(loop)        
                        # update because change incurred 
                        self.node_to_course_and_wale[loop_id] = (course_id, wale_id)
                        self.course_and_wale_to_node[(course_id, wale_id)] = loop_id
                        i+=1
            # print(f'nodes on yarn {yarn.yarn_id} is {yarn.yarn_graph.nodes}')
            print(f'yarn_edges is {yarn.yarn_graph.edges}')
        # print(f'self.node_to_course_and_wale is {self.node_to_course_and_wale}')
        

    def connect_stitches_on_knitgraph(self):
        print(f'self._knit_graph.graph.edges before reconnect stitch is {self._knit_graph.graph.edges}')
        self._knit_graph.graph.remove_edges_from([*self._knit_graph.graph.edges])
        for (parent_coor, child_coor, attr_dict) in self.knitgraph_coors_connectivity:
            parent_node = self.course_and_wale_to_node[parent_coor]
            child_node = self.course_and_wale_to_node[child_coor]
            pull_direction = attr_dict['pull_direction']
            depth = attr_dict['depth']
            parent_offset = attr_dict['parent_offset']
            self._knit_graph.connect_loops(parent_node, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
        print(f'self._knit_graph.graph.edges after reconnect stitch is {self._knit_graph.graph.edges}')

            
    def connect_bottom_nodes(self):
        """
        connect bottom nodes below the hole to the nearest top neighbor to prevent them from falling off the parent loops,
        leading the hole bigger and bigger.
        """
        hole_bottom_course_id = self._hole_start_course - 1
        connected_node_course_id = self._hole_start_course 
        connected_node_small_wale_id = min(self._hole_course_to_wale_ids[self._hole_start_course]) - 1
        # connected_node_small_wale_id = self._hole_start_wale - 1
        connected_node_big_wale_id = max(self._hole_course_to_wale_ids[self._hole_start_course]) + 1
        # connected_node_big_wale_id = self._hole_end_wale + 1
        #the reason why the searching range for bottom nodes is increased 2 respectively on each side is because there might be
        # a case where decrease happens on the node we delete for hole, check knitgraph slide pp. 57 for an example.
        # and 2 is because the racking constraint on the machine is -2 to +2.
        if self._hole_start_wale - self.course_id_to_start_wale_id[hole_bottom_course_id] > 2:
            bottom_node_start_wale = self._hole_start_wale - 2
        else:
            bottom_node_start_wale = self.course_id_to_start_wale_id[hole_bottom_course_id]
        course_width = len(self._course_to_loop_ids[hole_bottom_course_id]) 
        remain_width = course_width - (self._hole_end_wale - self.course_id_to_start_wale_id[hole_bottom_course_id]) - 1
        if remain_width > 2:
            bottom_node_end_wale = self._hole_end_wale + 2
        else:
            bottom_node_end_wale = self._hole_end_wale + remain_width
        # the reason why we expand the searching area for hole bottom node by -2 and +2 is because when deleting nodes for hole, if decrease stitch is involved,
        # meaning that extra node in the bottom course would become unstabilzed (i.e, no child), that's why we expanding the search area. 
        for wale_id in range(bottom_node_start_wale, bottom_node_end_wale + 1):
            connected_flag = False
            if (hole_bottom_course_id, wale_id) not in self.course_and_wale_to_node.keys():
                print(f'no node is found at position {(hole_bottom_course_id, wale_id)} on the bottom course of hole')
            else:
                node = self.course_and_wale_to_node[(hole_bottom_course_id, wale_id)]
                child_ids = [*self._knit_graph.graph.successors(node)] 
                #if both connected node don't exist, throw an error
                connected_node_small_wale_position = (connected_node_course_id, connected_node_small_wale_id)
                connected_node_big_wale_position = (connected_node_course_id, connected_node_big_wale_id)
                connected_node_small_wale_predecessor_position = (connected_node_course_id - 1, connected_node_small_wale_id)
                connected_node_big_wale_predecessor_position = (connected_node_course_id - 1, connected_node_big_wale_id)
                assert connected_node_small_wale_position in self.course_and_wale_to_node.keys() or connected_node_big_wale_position in self.course_and_wale_to_node.keys(),\
                    f'both connected_node_small_wale and connected_node_big_wale do not exist'
                # only connect node that have no child, i.e., unstable
                if len(child_ids) == 0:
                    # first try to connect this unstable node to connected_node_small_wale
                    if connected_node_small_wale_position not in self.course_and_wale_to_node.keys():
                        print(f'connected_node_small_wale at position {connected_node_small_wale_position} not exist')
                    else:
                        connected_node_small_wale = self.course_and_wale_to_node[connected_node_small_wale_position]
                        if (wale_id - connected_node_small_wale_id) <= 2:
                            parent_offset = wale_id - connected_node_small_wale_id
                            # the reason why we need "connected_node_xx_wale_predecessor_position" and the pull direction between it and its successor here
                            # is because, the newly connected stitch should have the same pull direction as that. 
                            if connected_node_small_wale_predecessor_position in self.course_and_wale_to_node.keys():
                                connected_node_small_wale_predeccessor = self.course_and_wale_to_node[connected_node_small_wale_predecessor_position]
                                if (connected_node_small_wale_predeccessor, connected_node_small_wale) in self._knit_graph.graph.edges:
                                    pull_direction = self._knit_graph.graph[connected_node_small_wale_predeccessor][connected_node_small_wale]["pull_direction"]
                                else: 
                                    pull_direction = Pull_Direction.BtF
                            self._knit_graph.connect_loops(node, connected_node_small_wale, parent_offset = parent_offset, pull_direction = pull_direction)
                            connected_flag = True
                    # if this unstable node can't be connected with connected_node_small_wale, then we should connect it with connected_node_big_wale
                    if connected_node_big_wale_position not in self.course_and_wale_to_node.keys():
                        print(f'connected_node_big_wale at position {connected_node_big_wale_position} not exist')
                    else:       
                        connected_node_big_wale = self.course_and_wale_to_node[connected_node_big_wale_position]
                        # if this unstable node can't be connected with connected_node_small_wale, then we should connect it with connected_node_big_wale
                        if (connected_node_big_wale_id - wale_id) <= 2 and connected_flag == False:
                            parent_offset = connected_node_big_wale_id - wale_id
                            if connected_node_big_wale_predecessor_position in self.course_and_wale_to_node.keys():
                                connected_node_big_wale_predeccessor = self.course_and_wale_to_node[connected_node_big_wale_predecessor_position]
                                if (connected_node_big_wale_predeccessor, connected_node_big_wale) in self._knit_graph.graph.edges:
                                    pull_direction = self._knit_graph.graph[connected_node_big_wale_predeccessor][connected_node_big_wale]["pull_direction"]
                                else: 
                                    pull_direction = Pull_Direction.BtF
                            self._knit_graph.connect_loops(node, connected_node_big_wale, parent_offset = -parent_offset)
                            connected_flag = True
                    #throw an error if any node can not be connected to any neighbor node
                    if connected_flag == False:
                        print(f'node {node} can not be connected with any neighbor node')
                        exit()
    # 
    def connect_hole_edge_nodes(self):
        # since now we allow hole of different shapes, hole edge node can be unstable because of this, refer to node 21 on pp. 52 of the sldies,
        # thus besides hole bottom nodes, we also need to examine the hole edge node on the hole_start_course to see if any of them needs to be connected
        # print(f'self._hole_start_course is {self._hole_start_course}')
        hole_edge_node_small_wale_id =  min(self._hole_course_to_wale_ids[self._hole_start_course]) - 1
        # print(f'hole_edge_node_small_wale_id is {hole_edge_node_small_wale_id}')
        hole_edge_node_big_wale_id = max(self._hole_course_to_wale_ids[self._hole_start_course]) + 1
        # for hole_edge_node_small_wale and hole_edge_node_big_wale, the connected node should be 
        connected_node_small_wale_id_for_hole_edge = min(self._hole_course_to_wale_ids[self._hole_start_course + 1]) - 1
        connected_node_big_wale_id_for_hole_edge = max(self._hole_course_to_wale_ids[self._hole_start_course + 1]) + 1
        # hole edge node work as node to connect for unstable node (hole bottom nodes). hole edge node refer to nodes sit immediately right next to the hole nodes on first
        # row. More details please refer to pp. 168 
        hole_edge_node_small_wale_position = (self._hole_start_course, hole_edge_node_small_wale_id)
        hole_edge_node_big_wale_position = (self._hole_start_course, hole_edge_node_big_wale_id)
        connected_node_small_wale_for_hole_edge_position = (self._hole_start_course+1, connected_node_small_wale_id_for_hole_edge)
        connected_node_big_wale_for_hole_edge_position =  (self._hole_start_course+1, connected_node_big_wale_id_for_hole_edge)
        # connected_node_small_wale_predecessor_for_hole_edge_position = (self._hole_start_course, connected_node_small_wale_id_for_hole_edge)
        # connected_node_big_wale_predecessor_for_hole_edge_position = (self._hole_start_course, connected_node_big_wale_id_for_hole_edge)
        if hole_edge_node_small_wale_position in self.course_and_wale_to_node.keys():
            node = self.course_and_wale_to_node[hole_edge_node_small_wale_position]
            child_ids = [*self._knit_graph.graph.successors(node)] 
            if len(child_ids) == 0:
                parent_offset = hole_edge_node_small_wale_id - connected_node_small_wale_id_for_hole_edge
                if connected_node_small_wale_for_hole_edge_position in self.course_and_wale_to_node.keys():
                    connected_node_small_wale_for_hole_edge = self.course_and_wale_to_node[connected_node_small_wale_for_hole_edge_position]
                    self._knit_graph.connect_loops(node, connected_node_small_wale_for_hole_edge, parent_offset = -parent_offset)
                else:
                    print(f'no connected_node_small_wale_for_hole_edge is found at position {connected_node_small_wale_for_hole_edge}')
        if hole_edge_node_big_wale_position in self.course_and_wale_to_node.keys():
            node = self.course_and_wale_to_node[hole_edge_node_big_wale_position]
            child_ids = [*self._knit_graph.graph.successors(node)] 
            if len(child_ids) == 0:
                parent_offset = hole_edge_node_big_wale_id - connected_node_big_wale_id_for_hole_edge
                if connected_node_big_wale_for_hole_edge_position in self.course_and_wale_to_node.keys():
                    connected_node_big_wale_for_hole_edge = self.course_and_wale_to_node[connected_node_big_wale_for_hole_edge_position]
                    self._knit_graph.connect_loops(node, connected_node_big_wale_for_hole_edge, parent_offset = -parent_offset)
                else:
                    print(f'no connected_node_big_wale_for_hole_edge is found at position {connected_node_big_wale_for_hole_edge}')    

    # currently, we only apply bind-off on the hole bottom nodes to stabilize them
    def bind_off(self):
        # first search for nodes that have no child on the hole bottom course (the course immediately below the hole area)
        hole_bottom_course_id = self._hole_start_course - 1
        if self._hole_start_wale - self.course_id_to_start_wale_id[hole_bottom_course_id] > 2:
            bottom_node_start_wale = self._hole_start_wale - 2
        else:
            bottom_node_start_wale = self.course_id_to_start_wale_id[hole_bottom_course_id]
        course_width = len(self._course_to_loop_ids[hole_bottom_course_id]) 
        remain_width = course_width - (self._hole_end_wale - self.course_id_to_start_wale_id[hole_bottom_course_id]) - 1
        # here it is 3 rather than 2, because we need to consider connecting the last node (i.e. at wale id of self._hole_end_wale + 2) to its neighbor node if
        # it has no child, that's why we increase 2 by 1 to 3, just to collect the nearest node to connect to in bottom_nodes list below.
        if remain_width > 3:
            bottom_node_end_wale = self._hole_end_wale + 3
        else:
            bottom_node_end_wale = self._hole_end_wale + remain_width
        # the reason why we expand the searching area for hole bottom node by -2 and +2 is because when deleting nodes for hole, if decrease stitch is involved,
        # meaning that extra node in the bottom course would become unstabilzed (i.e, no child), that's why we expanding the search area. 
        
        # then, connect them end to end, consistent with the yarn walking direction for that course
        bottom_nodes = []
        # put bottom nodes in bottom_nodes by small to large order of the wale id. the reason we use a list to hold the nodes rather than finish that inside a for loop like
        # below is that it makes it easy when there is no node on position right next to the unstable node, we will connect it to the "nearest neighbor" we can find.
        for wale_id in range(bottom_node_start_wale, bottom_node_end_wale + 1):
            if (hole_bottom_course_id, wale_id) not in self.course_and_wale_to_node.keys():
                print(f'no node is found at position {(hole_bottom_course_id, wale_id)} on the bottom course of hole')
            else:
                node = self.course_and_wale_to_node[(hole_bottom_course_id, wale_id)]
                bottom_nodes.append(node)
        # then connect nodes that have no child to its nearest neighbor node
        # we sorted the nodes so that we can guarantee that small nodes is connected to the bigger nodes, which is consistent with bind-off. it can be reverted.
        sorted_bottom_nodes = sorted(bottom_nodes)
        for i in range(len(sorted_bottom_nodes)-1):
            node = sorted_bottom_nodes[i]
            nearest_neighbor = sorted_bottom_nodes[i+1]
            child_ids = [*self._knit_graph.graph.successors(node)] 
            # only connect node that have no child, i.e., unstable
            if len(child_ids) == 0:
                parent_wale_id = self.node_to_course_and_wale[node][1]
                child_wale_id = self.node_to_course_and_wale[nearest_neighbor][1]
                self._knit_graph.connect_loops(node, nearest_neighbor, parent_offset = parent_wale_id - child_wale_id)
        
    def add_hole(self):
        if self.is_polygon == False:
            node_to_course_and_wale, course_and_wale_to_node = self.get_nodes_course_and_wale()
        # self.hole_shape_and_number_constraints()
        #return info including hole_start_wale, hole_end_wale, hole_start_course, hole_end_course, hole_height and hole_width.
        self.get_hole_size()
        # get course_to_wale_ids for hole area
        self.get_hole_course_to_wale_ids()
        self.get_course_id_to_wale_ids()
        #send out warning to user if special stitch might be broken or if hole node is set at places like top course.
        self.hole_location_errors()
        self.hole_location_warnings()
        #get the start wale id and end wale id for each course, which can be used in get_new_yarn_loop_ids() to get new yarn loop ids.
        self.get_start_and_end_wale_id_per_course()
        if self.object_type == 'tube':
            path_result, remain_subgraphs, G1 = self.find_shortest_path_for_tube()
        elif self.object_type == 'sheet':
            path_result = self.find_shortest_path_for_sheet()
        #remove nodes for hole from both knit graph and yarn graph.
        self.remove_hole_nodes_from_graph()
        # print(type(path_result), path_result)
        if type(path_result) == list:
            need_new_yarn = False
        elif type(path_result) == tuple:
            need_new_yarn = True
        elif path_result == None:
            print('can not find feasible solution to walk through the nodes on the graph')
            exit()
        self.remove_old_and_add_new_yarn(need_new_yarn, path = path_result, remain_subgraphs = remain_subgraphs, G1 = G1)
        #connect bottom nodes below the hole to the nearest top neighbor to prevent them from falling off the parent loops,
        #leading the hole bigger and bigger.
        # if self._hole_start_course > 0:
        #     self.connect_bottom_nodes()
        if len(self._hole_course_to_wale_ids.keys()) > 1:
            self.connect_hole_edge_nodes()
        # to prevent hole deformation, we can also use the bind-off
        self.bind_off()
        # 
        # self.read_connectivity_from_knitgraph()
        # # 
        # self.rebuild_yarn_graph()
        # # 
        # self.connect_stitches_on_knitgraph()
        # a, b, _, _ = self._knit_graph.get_courses(unmodified = False, gauge = self.gauge)
        # print(f'course_to_loop_ids after hole added is {b}')
        # self._knit_graph.graph.remove_edges_from([*self._knit_graph.graph.edges])
        # visualize_knitGraph(self._knit_graph, node_to_course_and_wale = self.node_to_course_and_wale, yarn_start_direction = 'left to right', object_type = self.object_type, unmodified = False, is_polygon = self.is_polygon)
        return self._knit_graph



