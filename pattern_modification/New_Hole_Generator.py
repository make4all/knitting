from typing import Optional, List, Dict, Tuple
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
import warnings

class Hole_Generator:
    """
    Biggest assumption: the function currently only apply for hole that are rectagular and only one hole. More yarns are needed if 
    the above condition is not satisfied.
    """
    def __init__(self, knit_graph: Knit_Graph, node_to_delete: List[int], new_carrier: int, new_yarn_id: str = 'new_yarn', starting_nodes_coor: Optional[List[Tuple[int, int]]] = None, ending_nodes_coor: Optional[List[Tuple[int, int]]] = None, course_to_loop_ids: Optional[Dict[int, List[int]]] = None, node_to_course_and_wale: Optional[Dict[int, Tuple[int, int]]] = None, course_and_wale_to_node: Optional[Dict[Tuple[int, int], int]] = None, is_polygon: bool = False, unmodified: bool = True):
        self._knit_graph: Knit_Graph = knit_graph
        assert len(self._knit_graph.yarns) == 1, "This only supports modifying graphs with one yarn"
        #since given knit graph has only one yarn before being modified
        self._old_yarn: Yarn = [*knit_graph.yarns.values()][0]
        assert new_carrier != None, f'new carrier is needed to introduce new yarn'
        self._new_carrier: int = new_carrier
        self._new_yarn: Yarn = None 
        self.new_yarn_id: str = new_yarn_id
        self._unmodified: bool = unmodified
        self._loop_id_to_course: Dict[int, float]
        self._course_to_loop_ids: Dict[float, List[int]] 
        self._loop_id_to_wale: Dict[int, float] 
        self._wale_to_loop_ids: Dict[float, List[int]]
        self.node_to_course_and_wale: Dict[int, Tuple(int, int)]    
        self.course_and_wale_to_node: Dict[Tuple[int, int], int] 
        self.starting_nodes_coor: List[Tuple[int, int]]
        self.ending_nodes_coor: List[Tuple[int, int]]
        self.course_id_to_start_wale_id: Optional[Dict[int, int]]
        self.course_id_to_end_wale_id: Optional[Dict[int, int]]
        if is_polygon == False: #then the input knit graph is a common retangle, it is safe to invoke knitgraph.get_course()
            self._loop_id_to_course, self._course_to_loop_ids, self._loop_id_to_wale, self._wale_to_loop_ids = self._knit_graph.get_courses(unmodified)
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
        self._pattern_width_per_course: Dict[int, int] 
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
   
    def get_nodes_course_and_wale(self):
        """
        Get the [course, wale] coordinate of each node in the knit graph.
        """
        node_to_course_and_wale = {}
        for node in self._knit_graph.graph.nodes:
            course = self._loop_id_to_course[node]
            wale = self._loop_id_to_wale[node]
            node_to_course_and_wale[node] = [course, wale]
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
        wale_involved = set()
        for node in self._node_to_delete:
            wale_id = self.node_to_course_and_wale[node][1]
            wale_involved.add(wale_id)
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
        assert len(wale_involved) <= 6, f'hole width is too large to achieve the racking bound by 3 on the machine'
        assert self._hole_end_course < self._pattern_height - 1, f'hole height is too large that it is exceeding the knit graph border'
        #hole_height: the height of the hole
        self._hole_height = self._hole_end_course - self._hole_start_course + 1
        #hole_width
        self._hole_width = self._hole_end_wale - self._hole_start_wale + 1
        

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
                print(f'Warning: node {node} is suspicious or a node on border for for having {len(child_ids)} child')
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
            if len(child_ids) != 1 and course_id != top_course_id:
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
    #Todo
    def hole_shape_and_number_constraints():
        xxx

    def remove_hole_nodes_from_graph(self):
        """
        remove the nodes for hole from both knit graph and yarn
        """
        self._knit_graph.graph.remove_nodes_from(self._node_to_delete)
        self._old_yarn.yarn_graph.remove_nodes_from(self._node_to_delete)
        print('course_to_loop_ids', self._course_to_loop_ids)

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

    def bring_new_yarn(self):
        """
        Create a new yarn with new carrier id.
        """
        self._new_yarn = Yarn(self.new_yarn_id, self._knit_graph, carrier_id=self._new_carrier)
        self._knit_graph.add_yarn(self._new_yarn)
    
    def remove_old_and_add_new_yarn(self, new_yarn_course_to_loop_ids):    
        """
        remove loop_ids from old yarn and add loop_ids to new yarn and connect them.
        """
        for course_id in new_yarn_course_to_loop_ids:
            loop_ids = new_yarn_course_to_loop_ids[course_id]
            for loop_id in loop_ids:
                self._old_yarn.yarn_graph.remove_node(loop_id)
                child_id, loop = self._new_yarn.add_loop_to_end(loop_id = loop_id)
        print(f'old yarn edges are {self._old_yarn.yarn_graph.edges}')
        print(f'new yarn edges are {self._new_yarn.yarn_graph.edges}')
    
    def connect_bottom_nodes(self):
        """
        connect bottom nodes below the hole to the nearest top neighbor to prevent them from falling off the parent loops,
        leading the hole bigger and bigger.
        """
        hole_bottom_course_id = self._hole_start_course - 1
        connected_course_id = self._hole_start_course 
        connected_wale_id_start = self._hole_start_wale - 1
        connected_wale_id_end = self._hole_end_wale + 1
        #the reason why the searching range for bottom nodes is increased 3 respectively on each side is because there might be
        # a case where decrease happens on the node we delete for hole, check knitgraph slide pp. 57 for an example.
        
        if self._hole_start_wale - self.course_id_to_start_wale_id[hole_bottom_course_id] > 3:
            bottom_node_start_wale = self._hole_start_wale - 3
        else:
            bottom_node_start_wale = self.course_id_to_start_wale_id[hole_bottom_course_id]
        course_width = len(self._course_to_loop_ids[hole_bottom_course_id]) 
        remain_width = course_width - (self._hole_end_wale - self.course_id_to_start_wale_id[hole_bottom_course_id]) - 1
        if remain_width > 3:
            bottom_node_end_wale = self._hole_end_wale + 3
        else:
            bottom_node_end_wale = self._hole_end_wale + remain_width
        for wale_id in range(bottom_node_start_wale, bottom_node_end_wale + 1):
            connected_flag = False
            if (hole_bottom_course_id, wale_id) not in self.course_and_wale_to_node.keys():
                print(f'no node is found position {(hole_bottom_course_id, wale_id)} on the bottom course of hole')
            else:
                node = self.course_and_wale_to_node[(hole_bottom_course_id, wale_id)]
                child_ids = [*self._knit_graph.graph.successors(node)] 
                #if both connected node don't exist, throw an error
                connected_node_start_position = (connected_course_id, connected_wale_id_start)
                connected_node_end_position = (connected_course_id, connected_wale_id_end)
                assert connected_node_start_position in self.course_and_wale_to_node.keys() or connected_node_end_position in self.course_and_wale_to_node.keys(),\
                    f'both connected_node_start and connected_node_end do not exist'
                # only connect node that have no child, i.e., unstable
                if len(child_ids) == 0:
                    if connected_node_start_position not in self.course_and_wale_to_node.keys():
                        print(f'connected_node_start at position {connected_node_start_position} not exist')
                    else:
                        connected_node_start = self.course_and_wale_to_node[connected_node_start_position]
                        if (wale_id - connected_wale_id_start) <= 3:
                            parent_offset = wale_id - connected_wale_id_start
                            self._knit_graph.connect_loops(node, connected_node_start, parent_offset = parent_offset)
                            connected_flag = True
            
                    if connected_node_end_position not in self.course_and_wale_to_node.keys():
                        print(f'connected_node_start at position {connected_node_end_position} not exist')
                    else:       
                        connected_node_end = self.course_and_wale_to_node[connected_node_end_position]
                        if (connected_wale_id_end - wale_id) <= 3 and connected_flag == False:
                            parent_offset = connected_wale_id_end - wale_id
                            self._knit_graph.connect_loops(node, connected_node_end, parent_offset = -parent_offset)
                            connected_flag = True
                    #throw an error if any node can not be connected to any neighbor node
                    if connected_flag == False:
                        print(f'node {node} can not be connected with any neighbor node')
                        exit()
                

    def add_hole(self):
        if self.is_polygon == False:
            node_to_course_and_wale, course_and_wale_to_node = self.get_nodes_course_and_wale()
        #return info including hole_start_wale, hole_end_wale, hole_start_course, hole_end_course, hole_height and hole_width.
        self.get_hole_size()
        #send out warning to user if special stitch might be broken or if hole node is set at places like top course.
        self.hole_location_errors()
        self.hole_location_warnings()
        #remove nodes for hole from both knit graph and yarn graph.
        self.remove_hole_nodes_from_graph()
        #get the start wale id and end wale id for each course, which can be used in get_new_yarn_loop_ids() to get new yarn loop ids.
        self.get_start_and_end_wale_id_per_course()
        #get new yarn loop ids
        new_yarn_course_to_loop_ids, old_yarn_course_to_margin_loop_ids = self.get_new_yarn_loop_ids()
        #create a new yarn object.
        self.bring_new_yarn()
        #reconnect nodes on old yarn margin (margin refers to the left wale and right wale around the hole).
        self.reconnect_old_yarn_at_margin(old_yarn_course_to_margin_loop_ids)
        #remove nodes in "new_yarn_course_to_loop_ids" from old yarn and add these nodes to the new yarn.
        self.remove_old_and_add_new_yarn(new_yarn_course_to_loop_ids) 
        #connect bottom nodes below the hole to the nearest top neighbor to prevent them from falling off the parent loops,
        #leading the hole bigger and bigger.
        self.connect_bottom_nodes()
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = self.node_to_course_and_wale, yarn_start_direction = 'left to right', unmodified = False, is_polygon = self.is_polygon)
        return self._knit_graph



