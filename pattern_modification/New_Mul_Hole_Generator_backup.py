from typing import Optional, List, Dict, Tuple, Union
import networkx as nx
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph
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
    def __init__(self, knit_graph: Knit_Graph, yarns_and_holes_to_add: Dict[int, List[int]], starting_nodes_coor: Optional[List[Tuple[int, int]]] = None, ending_nodes_coor: Optional[List[Tuple[int, int]]] = None, course_to_loop_ids: Optional[Dict[int, List[int]]] = None, node_to_course_and_wale: Optional[Dict[int, Tuple[int, int]]] = None, course_and_wale_to_node: Optional[Dict[Tuple[int, int], int]] = None, is_polygon: bool = False, unmodified: bool = True):
        self._knit_graph: Knit_Graph = knit_graph
        self.graph_nodes: set[int] = set(self._knit_graph.graph.nodes)
        assert len(self._knit_graph.yarns) == 1, "This only supports modifying graphs with one yarn"
        #since given knit graph has only one yarn before being modified
        self._old_yarn: Yarn = [*knit_graph.yarns.values()][0]
        # assert the type of keys is integer instead of str, otherwise will throw an error when it comes to create new yarn object in bring the new yarns() below
        assert set(map(type, yarns_and_holes_to_add.keys())) == {int}, f'yarn carrier id should be of integer type'
        self.yarns_and_holes_to_add:Dict[int, List[int]] = yarns_and_holes_to_add
        self._new_carriers: List[int] = [*yarns_and_holes_to_add.keys()]
        self.new_yarn_ids: List[str] = [str(new_yarn_id) for new_yarn_id in self._new_carriers]
        self._new_yarns: Dict[int, Yarn] = {}
        self.holes_size: Dict[int, Dict[str, int]] = {}
        self.holes_to_old_and_new_yarns: Dict[int, Dict[str, List[int]]] = {}
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
    
        self._hole_course_to_wale_ids: Dict[int, Dict[int, List[int]]] = {}
   
    def get_nodes_course_and_wale(self):
        """
        Get the [course, wale] coordinate of each node in the knit graph.
        """
        node_to_course_and_wale = {}
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
        # index starts from 0
        hole_index = 0 
        for hole in self.yarns_and_holes_to_add.values():
            self._hole_start_course: int = self._pattern_height - 1
            self._hole_end_course: int = 0
            self._hole_start_wale: int = 10000
            self._hole_end_wale: int = 0
            self._hole_height: int = None
            self._hole_width: int = None
            # 
            self.holes_size[hole_index] = {}
            self.holes_size[hole_index]['hole_nodes'] = hole
            for node in hole:
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
            #number of unique wale id can not exceed 6 to make it a feasible to knit on knittimg machine taking into account racking constraint
            # deprecated because now turn to bind-off on unstable hole nodes
            # assert len(wale_involved) <= 5, f'hole width is too large to achieve the racking bound by 2 on the machine'
            assert self._hole_start_course > 1, f'bind-off would fail if hole_start_course <= 1'
            assert self._hole_end_course < self._pattern_height - 1, f'hole height is too large that it is exceeding the knit graph border'
            self._hole_height = self._hole_end_course - self._hole_start_course + 1
            self._hole_width = self._hole_end_wale - self._hole_start_wale + 1
            self.holes_size[hole_index]['hole_start_course'] = self._hole_start_course
            self.holes_size[hole_index]['hole_end_course'] = self._hole_end_course
            self.holes_size[hole_index]['hole_start_wale'] = self._hole_start_wale
            self.holes_size[hole_index]['hole_end_wale'] = self._hole_end_wale
            self.holes_size[hole_index]['hole_height'] = self._hole_height
            self.holes_size[hole_index]['hole_width'] = self._hole_width
            hole_index += 1
            print(f'hole_start_course is {self._hole_start_course}, hole_end_course is {self._hole_end_course}, hole_start_wale is {self._hole_start_wale}, hole_end_wale is {self._hole_end_wale}')
        print(f'holes_size is {self.holes_size}')
    
    # use self._hole_course_to_wale_ids inside the get_new_yarn_loop_ids()
    def get_hole_course_to_wale_ids(self):
        hole_index = 0
        for hole in self.yarns_and_holes_to_add.values():
            self._hole_course_to_wale_ids[hole_index] = {}
            for node in hole:
                course_id = self.node_to_course_and_wale[node][0]
                wale_id = self.node_to_course_and_wale[node][1]
                # print(f'node is {node}, course_id is {course_id}, wale_id is {wale_id}')
                if course_id not in self._hole_course_to_wale_ids[hole_index]:
                    self._hole_course_to_wale_ids[hole_index][course_id] = [wale_id]
                else:
                    self._hole_course_to_wale_ids[hole_index][course_id].append(wale_id)
            hole_index += 1
        print(f'hole_course_to_wale_ids is {self._hole_course_to_wale_ids}')

    def hole_location_warnings(self):
        """
        check if any ready-to-be-hole node might break any special stitch or suspicious for lacking some property,
        signaling something might go wrong with the given knit graph.
        """
        for hole in self.yarns_and_holes_to_add.values():
            for node in hole:
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
        for hole in self.yarns_and_holes_to_add.values():
            for node in hole:
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
  
    def remove_hole_nodes_from_graph(self):
        """
        remove the nodes for hole from both knit graph and yarn
        """
        for hole in self.yarns_and_holes_to_add.values():
            self._knit_graph.graph.remove_nodes_from(hole)
            self._old_yarn.yarn_graph.remove_nodes_from(hole)
        # print('course_to_loop_ids', self._course_to_loop_ids)

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
    # only applicable to sheet case
    def get_new_yarn_loop_ids_for_holes(self):
        """
        Provided the hole_start_course, no matter what the yarn starting direction is, i.e., from left to right or from right
        to left, the loop ids that should be re-assigned to a new yarn can be determined by if the hole_start_course is an 
        odd number or even number, though the use of wale id and course id.
        """
        for hole_index in [*self.holes_size.keys()]:
            new_yarn_course_to_loop_ids: Dict[float, List[int]]= {}
            old_yarn_course_to_margin_loop_ids: Dict[float, List[int]]= {}
            new_yarn_course_to_margin_loop_ids: Dict[float, List[int]]= {}
            hole_info = self.holes_size[hole_index] 
            # print('hole_nodes is', hole_info['hole_nodes'])
            self.holes_to_old_and_new_yarns[hole_index] = {}
            if hole_info['hole_start_course'] % 2 == 0:
                #new yarn spread between the hole_end_wale and the last wale_id, old yarn is between the wale_id = 0 to the hole_start_wale 
                for course_id in range(hole_info['hole_start_course'], hole_info['hole_end_course'] + 1):
                    smallest_wale_id = min(self._hole_course_to_wale_ids[hole_index][course_id])
                    biggest_wale_id = max(self._hole_course_to_wale_ids[hole_index][course_id])
                    if (course_id, smallest_wale_id-1) not in self.course_and_wale_to_node.keys():
                        print(f'no node is found on the hole margin near the old yarn side {(course_id, smallest_wale_id - 1)}')
                        # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the old yarn margin {(course_id, hole_start_wale - 1)}'
                    else:
                        old_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, smallest_wale_id - 1)]
                    if (course_id, biggest_wale_id + 1) not in self.course_and_wale_to_node.keys():
                        print(f'no node is found on the hole margin near the new yarn side {(course_id, biggest_wale_id + 1)}')
                        # assert (course_id, hole_end_wale + 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_end_wale + 1)}'
                    else:
                        new_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, biggest_wale_id + 1)]
                    new_yarn_course_to_loop_ids[course_id] = []
                    if course_id % 2 == 0:
                        for wale_id in range(biggest_wale_id + 1, self.course_id_to_end_wale_id[course_id]+1):
                            if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].append(self.course_and_wale_to_node[(course_id, wale_id)])
                    elif course_id % 2 == 1:
                        for wale_id in range(biggest_wale_id + 1, self.course_id_to_end_wale_id[course_id]+1):
                            if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].insert(0, self.course_and_wale_to_node[(course_id, wale_id)])
                    if hole_info['hole_height'] % 2 == 0:
                        pass
                    elif hole_info['hole_height'] % 2 == 1:
                        for course_id in range(hole_info['hole_end_course'] + 1, self._pattern_height):
                            new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id]
            if hole_info['hole_start_course'] % 2 == 1:
                #Contrary to the above,
                #new yarn spread between the wale_id = 0 to the hole_start_wale, old yarn is between the hole_end_wale and the last wale_id
                for course_id in range(hole_info['hole_start_course'], hole_info['hole_end_course'] + 1):
                    smallest_wale_id = min(self._hole_course_to_wale_ids[hole_index][course_id])
                    biggest_wale_id = max(self._hole_course_to_wale_ids[hole_index][course_id])
                    if (course_id, biggest_wale_id + 1) not in self.course_and_wale_to_node.keys():
                        print(f'no node is found on the hole margin near the old yarn side {(course_id, biggest_wale_id + 1)}')
                        # assert (course_id, hole_end_wale + 1) in course_and_wale_to_node.keys(), f'no node is found on old yarn the margin {(course_id, hole_end_wale + 1)}'
                    else:
                        old_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, biggest_wale_id + 1)]
                    if  (course_id, smallest_wale_id - 1) not in self.course_and_wale_to_node.keys():
                        print(f'no node is found on the hole margin near the new yarn side {(course_id, smallest_wale_id - 1)}')
                        # assert (course_id, hole_start_wale - 1) in course_and_wale_to_node.keys(), f'no node is found on the new yarn margin {(course_id, hole_start_wale - 1)}'
                    else:
                        new_yarn_course_to_margin_loop_ids[course_id] = self.course_and_wale_to_node[(course_id, smallest_wale_id - 1)]
                    new_yarn_course_to_loop_ids[course_id] = []
                    if course_id % 2 == 0:
                        for wale_id in range(self.course_id_to_start_wale_id[course_id], smallest_wale_id):
                            if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].append(self.course_and_wale_to_node[(course_id, wale_id)])
                    elif course_id % 2 == 1:
                        for wale_id in range(self.course_id_to_start_wale_id[course_id], smallest_wale_id ):
                            if (course_id, wale_id) in self.course_and_wale_to_node.keys():
                                new_yarn_course_to_loop_ids[course_id].insert(0, self.course_and_wale_to_node[(course_id, wale_id)])
                    if hole_info['hole_height'] % 2 == 0:
                        pass
                    elif hole_info['hole_height'] % 2 == 1:
                        for course_id in range(hole_info['hole_end_course'] + 1, self._pattern_height):
                            new_yarn_course_to_loop_ids[course_id] = self._course_to_loop_ids[course_id]
            print('old_yarn_course_to_margin_loop_ids', old_yarn_course_to_margin_loop_ids)
            print('new_yarn_course_to_margin_loop_ids', new_yarn_course_to_margin_loop_ids)
            print('new_yarn_course_to_loop_ids', new_yarn_course_to_loop_ids)
            print(f'[*new_yarn_course_to_loop_ids.values()] is {[*new_yarn_course_to_loop_ids.values()]}')
            new_yarn_nodes = set(item for sublist in [*new_yarn_course_to_loop_ids.values()] for item in sublist) 
            self.holes_to_old_and_new_yarns[hole_index]['new_yarn_nodes'] = new_yarn_nodes
            self.holes_to_old_and_new_yarns[hole_index]['old_yarn_nodes'] = self.graph_nodes.difference(new_yarn_nodes).difference(set(hole_info['hole_nodes']))
        print(f'self.holes_to_old_and_new_yarns is {self.holes_to_old_and_new_yarns}')
        # get nodes on the old yarn
        real_old_yarn_nodes = self.holes_to_old_and_new_yarns[hole_index]['old_yarn_nodes']
        for hole_index in self.holes_to_old_and_new_yarns.keys():
            old_yarn_nodes = self.holes_to_old_and_new_yarns[hole_index]['old_yarn_nodes']
            real_old_yarn_nodes = sorted(real_old_yarn_nodes.intersection(old_yarn_nodes))
        print(f'final old yarn nodes is {real_old_yarn_nodes}')
        # get nodes for different new yarns
        hole_index_to_new_yarn_nodes = {}
        for hole_index in self.holes_to_old_and_new_yarns.keys():
            print(f'hole_index is {hole_index}')
            real_new_yarn_nodes = self.holes_to_old_and_new_yarns[hole_index]['new_yarn_nodes']
            print('real_new_yarn_nodes1 is', real_new_yarn_nodes)
            for hole_index_inside in self.holes_to_old_and_new_yarns.keys():
                other_new_yarn_nodes = self.holes_to_old_and_new_yarns[hole_index_inside]['new_yarn_nodes']
                if real_new_yarn_nodes == other_new_yarn_nodes:
                    continue
                else:
                    if len(real_new_yarn_nodes.intersection(other_new_yarn_nodes)) != 0:
                        if real_new_yarn_nodes.issubset(other_new_yarn_nodes):
                            continue
                        else:
                            real_new_yarn_nodes = real_new_yarn_nodes.difference(other_new_yarn_nodes)
            print('real_new_yarn_nodes2 is', real_new_yarn_nodes)
            # finally, we need to delete the all hole nodes if it is included on the real_new_yarn_nodes
            for hole in self.yarns_and_holes_to_add.values():
                for node in hole:
                    if node in real_new_yarn_nodes:
                        real_new_yarn_nodes.remove(node)
            hole_index_to_new_yarn_nodes[hole_index] = sorted(real_new_yarn_nodes)
        print(f'hole_index_to_new_yarn_nodes is {hole_index_to_new_yarn_nodes}')
        return real_old_yarn_nodes, hole_index_to_new_yarn_nodes
    
    # path search still needed for tube case
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
                # for first node on each course
                if node == self._course_to_loop_ids[course_id][0]:
                    #node right above it
                    if (course_id+1, wale_id) in self.node_to_course_and_wale.values():
                        above_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                        G1.add_edge(node, above_node, weight = -1)
                    #node one wale right above it
                    if (course_id+1, wale_id+1) in self.node_to_course_and_wale.values():
                        right_above_node = self.course_and_wale_to_node[(course_id+1, wale_id+1)]
                        G1.add_edge(node, right_above_node, weight = -1)
                    #last node on next course
                    if course_id+1 in self._course_to_loop_ids.keys():
                        target_node = self._course_to_loop_ids[course_id+1][-1]
                        G1.add_edge(node, target_node, weight = -1)
                # for last node on each course
                elif node == self._course_to_loop_ids[course_id][-1]:
                    #node right above it
                    if (course_id+1, wale_id) in self.node_to_course_and_wale.values():
                        above_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                        G1.add_edge(node, above_node, weight = -1)
                    #node one wale left above it
                    if (course_id+1, wale_id-1) in self.node_to_course_and_wale.values():
                        left_above_node = self.course_and_wale_to_node[(course_id+1, wale_id-1)]
                        G1.add_edge(node, left_above_node, weight = -1)
                    #first node on next course
                    if course_id+1 in self._course_to_loop_ids.keys():
                        target_node = self._course_to_loop_ids[course_id+1][0]
                        G1.add_edge(node, target_node, weight = -1)
                # for node in beweetn on each course 
                else:
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
            print('all edges', G1.edges)

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
                    if (course_id+1, wale_id) in self.course_and_wale_to_node:
                        end_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                        if (source_node, end_node) in G1.edges:
                            visited_nodes.append(end_node)
                            reward += G1.edges[source_node, end_node]['weight']
                            source_node = end_node
                            continue
                        else:
                            print(f'edge {(source_node, end_node)} not in G1')
                            
                    else:
                        print(f"no node in expected position {(course_id+1, wale_id)} to begin a new course, visited nodes so far is {visited_nodes}")
                    # which can happen for decrease tube case, to make it solvable, search for the nearest neighbor that exist
                    # but below method does not work for the case where start node is the node at the end of the front side of fabric and  has the biggest wale already 
                    # , and even walk 5 wale away can not find a feasible node to add.
                    # solution: walk 5 wale away in the opposite direction
                    flag = 0
                    count = 0
                    while flag == 0 and count<=5:
                        wale_id += 1
                        if (course_id+1, wale_id) in self.course_and_wale_to_node:
                            end_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                            if (source_node, end_node) in G1.edges:
                                visited_nodes.append(end_node)
                                reward += G1.edges[source_node, end_node]['weight']
                                source_node = end_node
                                flag = 1
                                break
                            else:
                                print(f'edge {(source_node, end_node)} not in G1')
                        count+=1
                    if flag == 0:
                        print(f"search 5 nearest neighbor nodes (with bigger wale_id) but found nothing to begin a new course, visited nodes so far is {visited_nodes}")
                        count = 0
                        # re-initialize wale_id changed by above for loop
                        wale_id = self.node_to_course_and_wale[start_node_on_course][1]
                        while flag == 0 and count<=5:
                            wale_id -= 1
                            if (course_id+1, wale_id) in self.course_and_wale_to_node:
                                end_node = self.course_and_wale_to_node[(course_id+1, wale_id)]
                                if (source_node, end_node) in G1.edges:
                                    visited_nodes.append(end_node)
                                    reward += G1.edges[source_node, end_node]['weight']
                                    source_node = end_node
                                    flag = 1
                                    break
                                else:
                                    print(f'edge {(source_node, end_node)} not in G1')
                            count+=1
                    if flag == 0:
                        print(f"search 5 nearest neighbor nodes (with smaller wale_id) but found nothing to begin a new course, visited nodes so far is {visited_nodes}")
                        break
                    else:
                        continue
                else:
                    for edge in G1.out_edges(source_node):
                        reward_dict[edge] = G1.edges[edge[0], edge[1]]['weight']
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
        # perform preprocessing on the graph
        preprocessing_on_graph(G1)
        # remove hole nodes
        # the reason we preprocess the KnitGraph before remove the hole nodes is to avoid the the potential error "RuntimeError: dictionary changed size during iteration"
        # caused by "for node in G1.nodes: xxx"
        G1.remove_nodes_from(self._node_to_delete)
        # record all nodes excluding hole nodes
        all_nodes = set(G1.nodes)
        # perform path search algorithm on the graph of tube with a hole
        visited_nodes_old_yarn = path_search(G1, yarn = "old")
        # get the remain nodes that are not on old yarn
        remain_nodes = all_nodes.difference(visited_nodes_old_yarn)
        print('remain nodes', remain_nodes)
        if len(remain_nodes) != 0:
            # before searching for the path, first delete the nodes in the visited_nodes
            G1.remove_nodes_from(visited_nodes_old_yarn)
            # perform path search algorithm on the updated graph
            visited_nodes_new_yarn = path_search(G1, yarn = "new")
            # if visited_nodes_new_yarn == remain_nodes, meaning that new yarn can walk through all the remain nodes, thus two yarns are sufficient for establishing a
            # tube with a hole
            if set(visited_nodes_new_yarn) == remain_nodes:
                print(f'two yarns are sufficient for establishing this knit graph of a tube with a hole! Specifically, nodes on old yarn is {visited_nodes_old_yarn},\
                nodes on new yarn is {visited_nodes_new_yarn}')
                return visited_nodes_old_yarn, visited_nodes_new_yarn
        else:
            print(f'only old yarn is sufficient to walk through all nodes on the graph of a tube with a hole, and nodes on old yarn is {visited_nodes_old_yarn}')
            return visited_nodes_old_yarn
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
    
    def remove_old_and_add_new_yarn(self, real_old_yarn_nodes, hole_index_to_new_yarn_nodes):    
        """
        remove loop_ids from old yarn and add loop_ids to new yarn.
        """        
        self._old_yarn.yarn_graph.remove_nodes_from(real_old_yarn_nodes)
        for hole_index in hole_index_to_new_yarn_nodes.keys():
            new_yarn_nodes = hole_index_to_new_yarn_nodes[hole_index]
            new_yarn = self._new_yarns[hole_index]
            self._old_yarn.yarn_graph.remove_nodes_from(new_yarn_nodes)
            for loop_id in new_yarn_nodes:
                child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
            print(f'new yarn edges are {new_yarn.yarn_graph.edges}')
        # use this method makes it no need to invoke reconnect_old_yarn_at_margin()
        self._old_yarn.last_loop_id = None
        for loop_id in real_old_yarn_nodes:
            child_id, loop = self._old_yarn.add_loop_to_end(loop_id = loop_id)
        print(f'old yarn edges are {self._old_yarn.yarn_graph.edges}')
        
    # @deprecated
    def connect_bottom_nodes(self):
        """
        connect bottom nodes below the hole to the nearest top neighbor to prevent them from falling off the parent loops,
        leading the hole bigger and bigger.
        """
        hole_bottom_course_id = self._hole_start_course - 1
        connected_node_course_id = self._hole_start_course 
        connected_node_small_wale_id = self._hole_start_wale - 1
        connected_node_big_wale_id = self._hole_end_wale + 1
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
                connected_node_small_wale_position = (connected_node_course_id, connected_node_small_wale_id)
                connected_node_big_wale_position = (connected_node_course_id, connected_node_big_wale_id)
                connected_node_small_wale_predecessor_position = (connected_node_course_id - 1, connected_node_small_wale_id)
                connected_node_big_wale_predecessor_position = (connected_node_course_id - 1, connected_node_big_wale_id)
                assert connected_node_small_wale_position in self.course_and_wale_to_node.keys() or connected_node_big_wale_position in self.course_and_wale_to_node.keys(),\
                    f'both connected_node_small_wale and connected_node_big_wale do not exist'
                # only connect node that have no child, i.e., unstable
                if len(child_ids) == 0:
                    if connected_node_small_wale_position not in self.course_and_wale_to_node.keys():
                        print(f'connected_node_small_wale at position {connected_node_small_wale_position} not exist')
                    else:
                        connected_node_small_wale = self.course_and_wale_to_node[connected_node_small_wale_position]
                        if (wale_id - connected_node_small_wale_id) <= 3:
                            parent_offset = wale_id - connected_node_small_wale_id
                            if connected_node_small_wale_predecessor_position in self.course_and_wale_to_node.keys():
                                connected_node_small_wale_predeccessor = self.course_and_wale_to_node[connected_node_small_wale_predecessor_position]
                                if (connected_node_small_wale_predeccessor, connected_node_small_wale) in self._knit_graph.graph.edges:
                                    pull_direction = self._knit_graph.graph[connected_node_small_wale_predeccessor][connected_node_small_wale]["pull_direction"]
                                else: 
                                    pull_direction = Pull_Direction.BtF
                            self._knit_graph.connect_loops(node, connected_node_small_wale, parent_offset = parent_offset, pull_direction = pull_direction)
                            connected_flag = True
            
                    if connected_node_big_wale_position not in self.course_and_wale_to_node.keys():
                        print(f'connected_node_big_wale at position {connected_node_big_wale_position} not exist')
                    else:       
                        connected_node_big_wale = self.course_and_wale_to_node[connected_node_big_wale_position]
                        if (connected_node_big_wale_id - wale_id) <= 3 and connected_flag == False:
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

    def connect_hole_edge_nodes(self):
        for hole_index in [*self.holes_size.keys()]:
            if len(self._hole_course_to_wale_ids[hole_index].keys()) > 1:
                # since now we allow hole of different shapes, hole edge node can be unstable because of this, refer to node 21 on pp. 52 of the sldies,
                # thus besides hole bottom nodes, we also need to examine the hole edge node on the hole_start_course to see if any of them needs to be connected
                hole_start_course = self.holes_size[hole_index]['hole_start_course']
                hole_edge_node_small_wale_id =  min(self._hole_course_to_wale_ids[hole_index][hole_start_course]) - 1
                hole_edge_node_big_wale_id = max(self._hole_course_to_wale_ids[hole_index][hole_start_course]) + 1
                # for hole_edge_node_small_wale and hole_edge_node_big_wale, the connected node should be 
                connected_node_small_wale_id_for_hole_edge = min(self._hole_course_to_wale_ids[hole_index][hole_start_course+1]) - 1
                connected_node_big_wale_id_for_hole_edge = max(self._hole_course_to_wale_ids[hole_index][hole_start_course+1]) + 1
                # hole edge node work as node to connect for unstable node (hole bottom nodes). hole edge node refer to nodes sit immediately right next to the hole nodes on first
                # row. More details please refer to pp. 168 
                hole_edge_node_small_wale_position = (hole_start_course, hole_edge_node_small_wale_id)
                hole_edge_node_big_wale_position = (hole_start_course, hole_edge_node_big_wale_id)
                connected_node_small_wale_for_hole_edge_position = (hole_start_course+1, connected_node_small_wale_id_for_hole_edge)
                connected_node_big_wale_for_hole_edge_position =  (hole_start_course+1, connected_node_big_wale_id_for_hole_edge)
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
                            print(f'child_ids is {child_ids}, node is {node}, connected_node_big_wale_for_hole_edge is {connected_node_big_wale_for_hole_edge}') 
                            self._knit_graph.connect_loops(node, connected_node_big_wale_for_hole_edge, parent_offset = -parent_offset)
                        else:
                            print(f'no connected_node_big_wale_for_hole_edge is found at position {connected_node_big_wale_for_hole_edge}')   
                        

    # currently, we only apply bind-off on the hole bottom nodes to stabilize them
    def bind_off(self):
        for hole_index in [*self.holes_size.keys()]:
            # first search for nodes that have no child on the hole bottom course (the course immediately below the hole area)
            hole_bottom_course_id = self.holes_size[hole_index]['hole_start_course'] - 1
            if self.holes_size[hole_index]['hole_start_wale'] - self.course_id_to_start_wale_id[hole_bottom_course_id] > 2:
                bottom_node_start_wale = self.holes_size[hole_index]['hole_start_wale'] - 2
            else:
                bottom_node_start_wale = self.course_id_to_start_wale_id[hole_bottom_course_id]
            course_width = len(self._course_to_loop_ids[hole_bottom_course_id]) 
            remain_width = course_width - (self.holes_size[hole_index]['hole_end_wale'] - self.course_id_to_start_wale_id[hole_bottom_course_id]) - 1
            # here it is 3 rather than 2, because we need to consider connecting the last node (i.e. at wale id of self._hole_end_wale + 2) to its neighbor node if
            # it has no child, that's why we increase 2 by 1 to 3, just to collect the nearest node to connect to in bottom_nodes list below.
            if remain_width > 3:
                bottom_node_end_wale = self.holes_size[hole_index]['hole_end_wale'] + 3
            else:
                bottom_node_end_wale = self.holes_size[hole_index]['hole_end_wale'] + remain_width
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
            print(f'sorted_bottom_nodes is {sorted_bottom_nodes}')
            for i in range(len(sorted_bottom_nodes)-1):
                node = sorted_bottom_nodes[i]
                nearest_neighbor = sorted_bottom_nodes[i+1]
                if node not in self._knit_graph.graph.nodes or nearest_neighbor not in self._knit_graph.graph.nodes:
                    continue
                else:
                    child_ids = [*self._knit_graph.graph.successors(node)] 
                    # only connect node that have no child, i.e., unstable
                    if len(child_ids) == 0:
                        parent_wale_id = self.node_to_course_and_wale[node][1]
                        child_wale_id = self.node_to_course_and_wale[nearest_neighbor][1]
                        self._knit_graph.connect_loops(node, nearest_neighbor, parent_offset = parent_wale_id - child_wale_id) 
                    

    def add_hole(self, object_type: Optional[str]):
        if self.is_polygon == False:
            node_to_course_and_wale, course_and_wale_to_node = self.get_nodes_course_and_wale()
        #first determine the validity of the input hole
        # self.hole_shape_and_number_constraints()
        #return info including hole_start_wale, hole_end_wale, hole_start_course, hole_end_course, hole_height and hole_width.
        self.get_hole_size()
        #send out warning to user if special stitch might be broken or if hole node is set at places like top course.
        self.hole_location_errors()
        self.hole_location_warnings()
        # get course_to_wale_ids for hole area
        self.get_hole_course_to_wale_ids()
        #remove nodes for hole from both knit graph and yarn graph.
        self.remove_hole_nodes_from_graph()
        #get the start wale id and end wale id for each course, which can be used in get_new_yarn_loop_ids() to get new yarn loop ids.
        self.get_start_and_end_wale_id_per_course()
        #get new yarn loop ids
        real_old_yarn_nodes, hole_index_to_new_yarn_nodes = self.get_new_yarn_loop_ids_for_holes()
        #create a new yarn object.
        self.bring_new_yarn()
        # #reconnect nodes on old yarn margin (margin refers to the left wale and right wale around the hole).
        # self.reconnect_old_yarn_at_margin(old_yarn_course_to_margin_loop_ids)
        # #remove nodes in "new_yarn_course_to_loop_ids" from old yarn and add these nodes to the new yarn.
        self.remove_old_and_add_new_yarn(real_old_yarn_nodes, hole_index_to_new_yarn_nodes) 
        # #connect bottom nodes below the hole to the nearest top neighbor to prevent them from falling off the parent loops,
        # #leading the hole bigger and bigger.
        # if self._hole_start_course > 0:
        #     self.connect_bottom_nodes()
        self.connect_hole_edge_nodes()
        # to prevent hole deformation, we can also use the bind-off
        self.bind_off()
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = self.node_to_course_and_wale, yarn_start_direction = 'left to right', unmodified = False, is_polygon = self.is_polygon)
        return self._knit_graph



