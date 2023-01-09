from typing import Optional, List, Dict, Tuple, Union
import networkx as nx
import random
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph, Pull_Direction
from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from debugging_tools.polygon_generator import Polygon_Generator
from debugging_tools.simple_knitgraph_generator import Simple_Knitgraph_Generator
import warnings

class Hole_Generator_on_Tube:
    """
    This is Hole_Generator works for tube, we have a separate Hole_Generator used for tube.
    Compared to "Hole_Generator" version, this version can work on polygon shaped fabric rather then only a rectangle.
    Biggest assumption: the function currently only apply for hole that are rectagular and only one hole. More yarns are needed if 
    the above condition is not satisfied.
    """
    def __init__(self, hole_index_to_holes: Dict[int, List[int]], knitgraph, simple_knitgraph_generator: Simple_Knitgraph_Generator = None):
        # print(f'simple_knitgraph_generator.pattern is {simple_knitgraph_generator.pattern}')
        # if simple_knitgraph_generator != None:
        #     self._knit_graph: Knit_Graph = simple_knitgraph_generator.generate_knitgraph()
        #     self._knit_graph.node_to_course_and_wale =  simple_knitgraph_generator.node_to_course_and_wale
        #     self._knit_graph.node_on_front_or_back = simple_knitgraph_generator.node_on_front_or_back
        #     self._knit_graph.course_and_wale_and_bed_to_node: Dict[((int, int), str), int] = simple_knitgraph_generator.course_and_wale_and_bed_to_node
        #     # reverse to retrieve bed info, which would be used in rebuild_yarn_graph()
        #     self._knit_graph.node_to_course_and_wale_and_bed: Dict[int, ((int, int), str)] = {v: k for k, v in self._knit_graph.course_and_wale_and_bed_to_node.items()}
        #     self._knit_graph.loop_id_to_course: Dict[int, float]
        #     self._knit_graph.loop_id_to_course, self._knit_graph.course_to_loop_ids = self._knit_graph.get_courses()
        #     self._knit_graph = simple_knitgraph_generator.gauge
        # else:
        self._knit_graph: Knit_Graph = knitgraph
        self._knit_graph.node_to_course_and_wale =  knitgraph.node_to_course_and_wale
        self._knit_graph.node_on_front_or_back = knitgraph.node_on_front_or_back
        self._knit_graph.course_and_wale_and_bed_to_node = knitgraph.course_and_wale_and_bed_to_node
        self._knit_graph.node_to_course_and_wale_and_bed: Dict[int, ((int, int), str)] = {v: k for k, v in self._knit_graph.course_and_wale_and_bed_to_node.items()}
        self._knit_graph.loop_id_to_course: Dict[int, float] = self._knit_graph.loop_ids_to_course
        self._knit_graph.course_to_loop_ids: Dict[int, List[int]] = self._knit_graph.course_to_loop_ids
        self._knit_graph.gauge = knitgraph.gauge
        assert self._knit_graph.object_type == 'tube', f'wrong object type of parent knitgraph'
        self._knit_graph.object_type = 'tube'
        self.hole_index_to_holes = hole_index_to_holes
        self.float_length = int(1/self._knit_graph.gauge) - 1
        self.wale_dist = int(1/self._knit_graph.gauge)
        self.graph_nodes: set[int] = set(self._knit_graph.graph.nodes)
        assert len(self._knit_graph.yarns) == 1, "This only supports modifying graphs that has only one yarn as input"
        #since given knit graph has only one yarn before being modified
        self._old_yarn: Yarn = [*self._knit_graph.yarns.values()][0]
        self._new_yarns: Union[Yarn, List[Yarn]] = []
        #pattern_height is the total number of courses 
        self._pattern_height: int = len(self._knit_graph.course_to_loop_ids)
        self.holes_size: Dict[int, Dict[str, int]] = {}
        self._hole_course_to_wale_ids: Dict[int, Dict[int, List[int]]] = {}      
        self.course_id_to_wale_ids: Dict[int, List[int]] = {}
        # what's store in self.knitgraph_coors_connectivity is like[[(0, 0), 'f', (1, 0), 'f', {'pull_direction': BtF, 'depth': 0, 'parent_offset': 0}], ...]
        self.knitgraph_coors_connectivity: List[List[Tuple[int, int], str, Tuple[int, int], str, Dict[str, Union[Pull_Direction, int]]]] = [] 

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
        for hole_index, hole in self.hole_index_to_holes.items():
            self._hole_start_course: int = self._pattern_height - 1
            self._hole_end_course: int = 0
            self._hole_start_wale: int = 10000
            # since the smallest wale id can be less than 0, thus we update the initialization of hole_end_wale from 0 to -10000
            self._hole_end_wale: int = -10000
            self._hole_height: int = None
            self._hole_width: int = None
            # 
            self.holes_size[hole_index] = {}
            self.holes_size[hole_index]['hole_nodes'] = hole
            for node in hole:
                wale_id = self._knit_graph.node_to_course_and_wale[node][1]
                # wale_involved.add(wale_id)
                course_id = self._knit_graph.node_to_course_and_wale[node][0]
                if course_id > self._hole_end_course:
                    self._hole_end_course = course_id
                if course_id < self._hole_start_course:
                    self._hole_start_course = course_id
                if wale_id < self._hole_start_wale:
                    self._hole_start_wale = wale_id
                if wale_id > self._hole_end_wale:
                    self._hole_end_wale = wale_id
            # number of unique wale id can not exceed 6 to make it a feasible to knit on knittimg machine taking into account racking constraint
            # deprecated because now turn to bind-off on unstable hole nodes
            # assert len(wale_involved) <= 5, f'hole width is too large to achieve the racking bound by 2 on the machine'
            assert self._hole_start_course > 1, f'bind-off would fail if hole_start_course <= 1'
            assert self._hole_end_course < self._pattern_height - 1, f'hole height is too large that it is exceeding the knit graph border'
            self._hole_height = self._hole_end_course - self._hole_start_course + 1
            self._hole_width = self._hole_end_wale - self._hole_start_wale + self.wale_dist
            self.holes_size[hole_index]['hole_start_course'] = self._hole_start_course
            self.holes_size[hole_index]['hole_end_course'] = self._hole_end_course
            self.holes_size[hole_index]['hole_start_wale'] = self._hole_start_wale
            self.holes_size[hole_index]['hole_end_wale'] = self._hole_end_wale
            self.holes_size[hole_index]['hole_height'] = self._hole_height
            self.holes_size[hole_index]['hole_width'] = self._hole_width
            print(f'hole_start_course is {self._hole_start_course}, hole_end_course is {self._hole_end_course}, hole_start_wale is {self._hole_start_wale}, hole_end_wale is {self._hole_end_wale}')
        print(f'holes_size is {self.holes_size}')
    
    # use self._hole_course_to_wale_ids inside the get_new_yarn_loop_ids()
    def get_hole_course_to_wale_ids(self):
        for hole_index, hole in self.hole_index_to_holes.items():
            self._hole_course_to_wale_ids[hole_index] = {}
            for node in hole:
                course_id = self._knit_graph.node_to_course_and_wale[node][0]
                wale_id = self._knit_graph.node_to_course_and_wale[node][1]
                # print(f'node is {node}, course_id is {course_id}, wale_id is {wale_id}')
                if course_id not in self._hole_course_to_wale_ids[hole_index]:
                    self._hole_course_to_wale_ids[hole_index][course_id] = [wale_id]
                else:
                    self._hole_course_to_wale_ids[hole_index][course_id].append(wale_id)
        # print(f'hole_course_to_wale_ids is {self._hole_course_to_wale_ids}')

    def hole_location_warnings(self):
        """
        check if any ready-to-be-hole node might break any special stitch or suspicious for lacking some property,
        signaling something might go wrong with the given knit graph.
        """
        for hole in self.hole_index_to_holes.values():
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
                    print(f'Error: node {node} is suspicious or is a node on border for for having {len(child_ids)} child')
                    exit()
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
                    if self._knit_graph.node_to_course_and_wale[parent_id][0] != self._knit_graph.node_to_course_and_wale[child_id][0]:
                        print(f'Error: node {node} might break a special stitch or a node on border for having parent node and child node on yarn graph that are not on the same course')
                        exit()

    def hole_location_errors(self):
        for hole in self.hole_index_to_holes.values():
            for node in hole:
                #First, if a node has no child and is not a node on top course/top border 
                #it would be an error/unstable node in the knit graph signaling something wrong with the given knitgraph.
                parent_ids = [*self._knit_graph.graph.predecessors(node)]
                child_ids = [*self._knit_graph.graph.successors(node)]
                course_id = self._knit_graph.node_to_course_and_wale[node][0]
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
    
    def get_course_id_to_wale_ids(self):
        for course_id in self._knit_graph.course_to_loop_ids.keys():
            self.course_id_to_wale_ids[course_id] = []
            # for tube case, the first wale_id on each course in self.course_id_to_wale_ids is always the smallest one, and vice versa. 
            for loop_id in self._knit_graph.course_to_loop_ids[course_id]:
                wale_id = self._knit_graph.node_to_course_and_wale[loop_id][1]
                self.course_id_to_wale_ids[course_id].append(wale_id)
        # print(f'self.course_id_to_wale_ids is {self.course_id_to_wale_ids}')

    # First, preprocessing: add more edges to the graph to make the path searching problem solvable
    def preprocessing_on_graph(self, G1):
        # 1. add yarn paths of opposite direction in addition to the original direction for any neighbor nodes on the same course
        for prior_node, next_node in self._old_yarn.yarn_graph.edges:
            # different from sheet, for a tube, the yarn edge/yarn path needs to be walkable in both left and right direction, otherwise the problem tend to be
            # have no solution
            G1.add_edge(prior_node, next_node, weight = -10)
            # add an edge that is exactly of opposite direction again if they are on the same course
            if self._knit_graph.node_to_course_and_wale[prior_node][0] == self._knit_graph.node_to_course_and_wale[next_node][0]:
                G1.add_edge(next_node, prior_node, weight = -10)
        # 2. add edge of two opposite direction between the start node and end node on each course
        for course_id in self._knit_graph.course_to_loop_ids.keys():
            start_node = self._knit_graph.course_to_loop_ids[course_id][0]
            end_node = self._knit_graph.course_to_loop_ids[course_id][-1]
            if abs(self._knit_graph.node_to_course_and_wale[start_node][1] - self._knit_graph.node_to_course_and_wale[end_node][1]) <= self.wale_dist:
                G1.add_edge(start_node, end_node, weight = -10)
                G1.add_edge(end_node, start_node, weight = -10)
        # 3. add stitch paths, for each node, it should have three stitch edges, one is connected with node right above it, one is one wale left above it, and one
        # is one wale right above it. first node and last node on each course is special node, thus need separate discussion as below.
        for node in G1.nodes:
            wale_id = self._knit_graph.node_to_course_and_wale[node][1]
            course_id = self._knit_graph.node_to_course_and_wale[node][0]
            max_wale_id_on_the_course = max(self.course_id_to_wale_ids[course_id])
            min_wale_id_on_the_course = min(self.course_id_to_wale_ids[course_id])
            wale_of_bigger_nearest_neighbor = 0 #random initialization
            wale_of_smaller_nearest_neighbor = 0 #random initialization
            # min_wale_difference_for_smaller_wale = min_wale_difference_for_bigger_wale = 10000
            min_wale_difference = 10000
            bed = self._knit_graph.node_on_front_or_back[node]
            opposite_bed = 'f' if bed == 'b' else 'b'
            # wale_dist = self.float_length+1
            # connect until the second highest course
            if course_id < max([*self._knit_graph.course_to_loop_ids.keys()]):
                wale_ids_on_above_course = self.course_id_to_wale_ids[course_id+1]
                # 3.1 for node on left edge
                if wale_id == min_wale_id_on_the_course:
                    #node right above it
                    if ((course_id+1, wale_id), bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_id), bed)]
                        G1.add_edge(node, above_node, weight = -1)   
                    min_wale_difference = 10000
                    # find bigger_wale_neighbor_node
                    for wale_id_above_course in wale_ids_on_above_course:
                        wale_difference = wale_id_above_course - wale_id 
                        if wale_difference > 0 and wale_difference < min_wale_difference:
                            min_wale_difference = wale_difference
                            wale_of_bigger_nearest_neighbor = wale_id_above_course
                    if ((course_id+1, wale_of_bigger_nearest_neighbor), bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        big_wale_above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_of_bigger_nearest_neighbor), bed)]
                        G1.add_edge(node, big_wale_above_node, weight = -1)
                    # find the other neighbor node (that must be on the opposite bed with wale id that is either the same or bigger but closest to the node)
                    min_wale_difference = 10000
                    for wale_id_above_course in wale_ids_on_above_course:
                        wale_difference = wale_id_above_course - wale_id 
                        if wale_difference >= 0 and wale_difference < min_wale_difference: #>= instead of > is because for consistent tube it is the same wale
                            min_wale_difference = wale_difference
                            wale_of_bigger_nearest_neighbor = wale_id_above_course
                    if ((course_id+1, wale_of_bigger_nearest_neighbor), opposite_bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        big_wale_above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_of_bigger_nearest_neighbor), opposite_bed)]
                        G1.add_edge(node, big_wale_above_node, weight = -1)
                # for node in between on each course 
                elif min_wale_id_on_the_course < wale_id < max_wale_id_on_the_course:
                    # find node right above it
                    if ((course_id+1, wale_id), bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_id), bed)]
                        G1.add_edge(node, above_node, weight = -1)
                        # if node == 76:
                        #     print(f'above_node is {above_node}')
                    # find small_wale_neighbor_node (the nearest neighbor with smaller wale)
                    min_wale_difference = 10000
                    for wale_id_above_course in wale_ids_on_above_course:
                        wale_difference = wale_id -  wale_id_above_course
                        if wale_difference > 0 and wale_difference < min_wale_difference:
                            min_wale_difference = wale_difference
                            wale_of_smaller_nearest_neighbor = wale_id_above_course
                    if min_wale_difference == self.wale_dist and ((course_id+1, wale_of_smaller_nearest_neighbor), bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        small_wale_above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_of_smaller_nearest_neighbor), bed)]
                        G1.add_edge(node, small_wale_above_node, weight = -1)
                        # if node == 76:
                        #     print(f'small_wale_above_node is {small_wale_above_node}')
                    # find big_wale_neighbor_node (the nearest neighbor with bigger wale)
                    min_wale_difference = 10000
                    for wale_id_above_course in wale_ids_on_above_course:
                        wale_difference = wale_id_above_course - wale_id 
                        if wale_difference > 0 and wale_difference < min_wale_difference: 
                            min_wale_difference = wale_difference
                            wale_of_bigger_nearest_neighbor = wale_id_above_course
                    if min_wale_difference == self.wale_dist and ((course_id+1, wale_of_bigger_nearest_neighbor), bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        big_wale_above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_of_bigger_nearest_neighbor), bed)]
                        G1.add_edge(node, big_wale_above_node, weight = -1) 
                        # if node == 76:
                        #     print(f'big_wale_above_node is {big_wale_above_node}')
                elif wale_id == max_wale_id_on_the_course:
                    #node right above it
                    if ((course_id+1, wale_id), bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_id), bed)]
                        G1.add_edge(node, above_node, weight = -1)   
                    min_wale_difference = 10000
                    # find small_wale_neighbor_node
                    for wale_id_above_course in wale_ids_on_above_course:
                        wale_difference = wale_id -  wale_id_above_course
                        if wale_difference > 0 and wale_difference < min_wale_difference:
                            min_wale_difference = wale_difference
                            wale_of_smaller_nearest_neighbor = wale_id_above_course
                    if ((course_id+1, wale_of_smaller_nearest_neighbor), bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        small_wale_above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_of_smaller_nearest_neighbor), bed)]
                        G1.add_edge(node, small_wale_above_node, weight = -1)
                    # find the other neighbor node (that must be on the opposite bed with wale id that is either the same or smaller but closest to the node)
                    min_wale_difference = 10000
                    for wale_id_above_course in wale_ids_on_above_course:
                        wale_difference = wale_id -  wale_id_above_course
                        if wale_difference >= 0 and wale_difference < min_wale_difference: #>= instead of > is because for consistent tube it is the same wale
                            min_wale_difference = wale_difference
                            wale_of_smaller_nearest_neighbor = wale_id_above_course
                    if ((course_id+1, wale_of_smaller_nearest_neighbor), opposite_bed) in self._knit_graph.course_and_wale_and_bed_to_node.keys():
                        small_wale_above_node = self._knit_graph.course_and_wale_and_bed_to_node[((course_id+1, wale_of_smaller_nearest_neighbor), opposite_bed)]
                        G1.add_edge(node, small_wale_above_node, weight = -1)

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
            curr_course_id = self._knit_graph.node_to_course_and_wale[source_node][0]
        reward = 0
        course_nodes = []
        
        while source_node != None:
            # print('source_node', source_node)
            reward_dict = {}
            course_id = self._knit_graph.node_to_course_and_wale[source_node][0]
            # print('course_id', course_id)
            total_num_of_nodes_each_course = len(self._knit_graph.course_to_loop_ids[course_id])
            if course_id != curr_course_id:
                course_nodes = []
                # course_nodes.append(source_node)
                curr_course_id = course_id
            course_nodes.append(source_node)
            # print('course_nodes', course_nodes)
            
            for edge in G.out_edges(source_node):
                reward_dict[edge] = G.edges[edge[0], edge[1]]['weight']
            # print('reward_dict', reward_dict)
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
                    # print('end_node', edge_end_node)
                    break
            if flag == 0:
                print(f"no next node available due to all have been visited before, visited nodes so far is {visited_nodes}") 
                break
        remain_nodes = set(G.nodes).difference(visited_nodes)
        return visited_nodes, remain_nodes
    """ 
    #back up prior version
    def path_search(self, G, yarn: Optional[str] = None):
        # for old yarn, source node always starts from 0
        if yarn == 'old':
            source_node = 0
            visited_nodes = [0]
            curr_course_id = 0
        else:
            source_node = min(set(G.nodes))
            visited_nodes = [source_node]
            curr_course_id = self._knit_graph.node_to_course_and_wale[source_node][0]
        reward = 0
        course_nodes = []
        
        while source_node != None:
            print('source_node', source_node)
            reward_dict = {}
            course_id = self._knit_graph.node_to_course_and_wale[source_node][0]
            print('course_id', course_id)
            total_num_of_nodes_each_course = len(self._knit_graph.course_to_loop_ids[course_id])
            if course_id != curr_course_id:
                course_nodes = []
                # course_nodes.append(source_node)
                curr_course_id = course_id
            course_nodes.append(source_node)
            print('course_nodes', course_nodes)
            if len(course_nodes) == total_num_of_nodes_each_course:
                start_node_on_course = course_nodes[0]
                wale_id = self._knit_graph.node_to_course_and_wale[start_node_on_course][1]
                flag = 0
                print(f'start_node_on_course is {start_node_on_course}, out edges are {G.out_edges(start_node_on_course)}')
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
    """

    def find_shortest_path_for_tube(self):
            G1 = nx.DiGraph()   
            # perform preprocessing on the graph
            self.preprocessing_on_graph(G1)
            # print('all edges', G1.edges)
            # remove hole nodes
            # the reason we preprocess the KnitGraph before remove the hole nodes is to avoid the the potential error "RuntimeError: dictionary changed size during iteration"
            # caused by "for node in G1.nodes: xxx"
            for hole in self.hole_index_to_holes.values():
                G1.remove_nodes_from(hole)
            # record all nodes excluding hole nodes
            # all_nodes = set(G1.nodes)
            # perform path search algorithm on the graph of tube with a hole
            visited_nodes_old_yarn, remain_nodes = self.path_search(G1, yarn = "old")
            # get the remain nodes that are not on old yarn
            ## remain_nodes = all_nodes.difference(visited_nodes_old_yarn)
            # print('remain nodes', remain_nodes)
            G1.remove_nodes_from(visited_nodes_old_yarn)
            # print(f'separate subgraphs in find_shortest_path_for_tube() are {list(nx.weakly_connected_components(G1))}')
            return visited_nodes_old_yarn, list(nx.weakly_connected_components(G1)), G1

    def remove_hole_nodes_from_graph(self):
        """
        remove the nodes for hole from both knit graph and yarn
        """
        print(f'self._knit_graph.node_to_course_and_wale_and_bed is {self._knit_graph.node_to_course_and_wale_and_bed}')
        for hole in self.hole_index_to_holes.values():
            self._knit_graph.graph.remove_nodes_from(hole)
            self._old_yarn.yarn_graph.remove_nodes_from(hole)
            for hole_node in hole:
                del self._knit_graph.node_to_course_and_wale[hole_node]
                del self._knit_graph.node_on_front_or_back[hole_node] 
                del self._knit_graph.node_to_course_and_wale_and_bed[hole_node]
        # then use the updated self._knit_graph.node_to_course_and_wale_and_bed to get updated self._knit_graph.course_and_wale_and_bed_to_node
        self._knit_graph.course_and_wale_and_bed_to_node = {v: k for k, v in self._knit_graph.node_to_course_and_wale_and_bed.items()}

    def get_start_and_end_wale_id_per_course(self):
        ''' 
        abandoned because unlike sheet, for tube, the start_node for each course is always self._knit_graph.course_to_loop_ids[course_id][0] 
        no matther whether course_id is an odd or even number.
        '''
    def remove_old_and_add_new_yarn(self, path: List[int], remain_subgraphs, G1):    
        """
        remove loop_ids from old yarn and add loop_ids to new yarn.
        """
        # print(f'old yarn carrier id is {self._old_yarn.yarn_id}, carrier id is {self._old_yarn.carrier.carrier_ids}')
        visited_nodes_old_yarn = path
        # delete all nodes on old yarn and use the visited_nodes_old_yarn to walk the old yarn to form the new old yarn graph
        # original 
        # self._old_yarn.yarn_graph.remove_nodes_from(visited_nodes_old_yarn)
        # updated for debugging
        self._old_yarn.yarn_graph.remove_nodes_from(self._knit_graph.graph.nodes)
        # remain_nodes = set(self._knit_graph.graph.nodes).difference(set(visited_nodes_old_yarn))
        # self._knit_graph.graph.remove_nodes_from(remain_nodes)
        self._old_yarn.last_loop_id = None
        for loop_id in visited_nodes_old_yarn:
            child_id, loop = self._old_yarn.add_loop_to_end(loop_id = loop_id)
        new_yarns = []
        # walk new yarns on remain subgraphs
        remain_nodes = [0]
        for i in range(len(remain_subgraphs)):
            G2 = G1.copy()
            subgraph = remain_subgraphs[i]
            while True:
                yarn_carrier_id = random.randint(1,10)
                if yarn_carrier_id!=self._old_yarn.carrier.carrier_ids and yarn_carrier_id not in new_yarns:
                    new_yarns.append(yarn_carrier_id)
                    break
            new_yarn_id = str(yarn_carrier_id)
            new_yarn = Yarn(new_yarn_id, self._knit_graph, carrier_id=yarn_carrier_id)
            self._knit_graph.add_yarn(new_yarn)
            self._new_yarns.append(new_yarn)  
            other_subgraphs = []
            for other_subgraph in remain_subgraphs:
                if other_subgraph != subgraph:
                    # print(f'other_subgraph is {other_subgraph}')
                    other_subgraphs = other_subgraphs+list(other_subgraph)
            # print(f'other_subgraphs is {other_subgraphs}, subgraph is {subgraph}, remain_subgraphs is {remain_subgraphs}')
            G2.remove_nodes_from(other_subgraphs)
            # print(f'G2 is {G2}, subgraph is {subgraph}')
            # bellman-ford algorithm below does not work because negative weighted cycle is introduced in the pre-processing phase
            # shortest_paths = nx.shortest_path(G2, source=min(subgraph), weight='weight', method = 'bellman-ford')
            path, remain_nodes = self.path_search(G2)
            # print(f'path is {path}')
            for loop_id in path:
                child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
            while len(remain_nodes) > 0:
                while True:
                    yarn_carrier_id = random.randint(1,10)
                    if yarn_carrier_id!=self._old_yarn.carrier.carrier_ids and yarn_carrier_id not in new_yarns:
                        new_yarns.append(yarn_carrier_id)
                        break
                new_yarn_id = str(yarn_carrier_id)
                new_yarn = Yarn(new_yarn_id, self._knit_graph, carrier_id=yarn_carrier_id)
                self._knit_graph.add_yarn(new_yarn)
                self._new_yarns.append(new_yarn)  
                G2.remove_nodes_from(path)
                path, remain_nodes = self.path_search(G2)
                # print(f'path is {path}')
                for loop_id in path:
                    child_id, loop = new_yarn.add_loop_to_end(loop_id = loop_id)
        
    def connect_hole_edge_nodes(self):
        for hole_index in [*self.holes_size.keys()]:
            if len(self._hole_course_to_wale_ids[hole_index].keys()) > 1:
                # since now we allow hole of different shapes, hole edge node can be unstable because of this, refer to node 21 on pp. 52 of the sldies,
                # thus besides hole bottom nodes, we also need to examine the hole edge node on the hole_start_course to see if any of them needs to be connected
                hole_start_course = self.holes_size[hole_index]['hole_start_course']
                hole_edge_node_small_wale_id =  min(self._hole_course_to_wale_ids[hole_index][hole_start_course]) - self.wale_dist
                hole_edge_node_big_wale_id = max(self._hole_course_to_wale_ids[hole_index][hole_start_course]) + self.wale_dist
                # for hole_edge_node_small_wale and hole_edge_node_big_wale, the connected node should be 
                connected_node_small_wale_id_for_hole_edge = min(self._hole_course_to_wale_ids[hole_index][hole_start_course+1]) - self.wale_dist
                connected_node_big_wale_id_for_hole_edge = max(self._hole_course_to_wale_ids[hole_index][hole_start_course+1]) + self.wale_dist
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
            # current version relaxing the racking constraint of up to 2 needle on beds
            hole_bottom_course_id = self.holes_size[hole_index]['hole_start_course'] - 1
            # then, connect them end to end, consistent with the yarn walking direction for that course
            bottom_nodes = self._knit_graph.course_to_loop_ids[hole_bottom_course_id]
            # then connect nodes that have no child to its nearest neighbor node
            # we sorted the nodes so that we can guarantee that small nodes is connected to the bigger nodes, which is consistent with bind-off. it can be reverted.
            sorted_bottom_nodes = sorted(bottom_nodes)
            # print(f'sorted_bottom_nodes is {sorted_bottom_nodes}')
            for i in range(len(sorted_bottom_nodes)-1):
                node = sorted_bottom_nodes[i]
                nearest_neighbor = sorted_bottom_nodes[i+1]
                if node not in self._knit_graph.graph.nodes or nearest_neighbor not in self._knit_graph.graph.nodes:
                    continue
                else:
                    child_ids = [*self._knit_graph.graph.successors(node)] 
                    # only connect node that have no child, i.e., unstable
                    if len(child_ids) == 0:
                        parent_wale_id = self._knit_graph.node_to_course_and_wale[node][1]
                        child_wale_id = self._knit_graph.node_to_course_and_wale[nearest_neighbor][1]
                        # todo: if the parent offset of bind_off is larger than 2, we will consider using connect_hole_edge_node(). But if the parent offset in connect_\
                        # hole_edge_node is also larger than 2, we will send out a error and exit.
                        if self._knit_graph.node_on_front_or_back[node] == 'f':
                            pull_direction = Pull_Direction.BtF
                        else:
                            pull_direction = Pull_Direction.FtB
                        self._knit_graph.connect_loops(node, nearest_neighbor, parent_offset = parent_wale_id - child_wale_id, pull_direction = pull_direction) 

    def read_connectivity_from_knitgraph(self):
        """
        transform edge_data_list where connectivity is expressed in terms of node id into coor_connectivity where connectivity is
        expressed in terms of coordinate in formart of (course_id, wale_id). This transform is needed because we are going to 
        change the node order to represent the correct knitting operation order when knitting a pocket, thus at each coor, the node
        id would change, that's why we need to update node_to_course_and_wale for both parent graph and child graph.
        """
        # for tube, we will need additional info, bed, though which is not needed for sheet as no two node with same course and wale id appear on the two opposite bed.
        knitgraph_edge_data_list = self._knit_graph.graph.edges(data=True)
        for edge_data in knitgraph_edge_data_list:
            node = edge_data[1]
            node_coor = self._knit_graph.node_to_course_and_wale[node]
            node_bed = self._knit_graph.node_on_front_or_back[node]
            predecessor = edge_data[0]
            predecessor_coor = self._knit_graph.node_to_course_and_wale[predecessor]
            predecessor_bed = self._knit_graph.node_on_front_or_back[predecessor]
            attr_dict = edge_data[2]
            self.knitgraph_coors_connectivity.append([predecessor_coor, predecessor_bed, node_coor, node_bed, attr_dict])
        # print(f'self.knitgraph_coors_connectivity is {self.knitgraph_coors_connectivity}')

    def rebuild_yarn_graph(self):
        yarns = [*self._knit_graph.yarns.values()]
        for yarn in yarns:
            # node_coor_order = []
            course_to_wale_ids = {}
            course_to_bed_info = {}
            if len(yarn.yarn_graph.nodes) > 0:
                nodes_on_yarn = [*yarn.yarn_graph.nodes]
                for node in nodes_on_yarn:
                    course_id = self._knit_graph.node_to_course_and_wale[node][0]
                    if course_id not in course_to_wale_ids:
                        course_to_wale_ids[course_id] = [self._knit_graph.node_to_course_and_wale[node][1]]
                        course_to_bed_info[course_id] = [self._knit_graph.node_to_course_and_wale_and_bed[node][1]]
                    else:
                        course_to_wale_ids[course_id].append(self._knit_graph.node_to_course_and_wale[node][1])
                        course_to_bed_info[course_id].append(self._knit_graph.node_to_course_and_wale_and_bed[node][1])
                    # del self._knit_graph.node_to_course_and_wale[node] 
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
                    bed_info = course_to_bed_info[course_id]
                    sorted_nodes_on_yarn = sorted(nodes_on_yarn)
                    # print(f'wale_ids is {wale_ids}')
                    for wale_id, bed in zip(wale_ids, bed_info):
                        # print(f'nodes_on_yarn[i] is {nodes_on_yarn[i]}')
                        loop_id, loop = yarn.add_loop_to_end(loop_id = sorted_nodes_on_yarn[i])
                        # print(f'wale_id is {wale_id}, loop_id is {loop_id}')
                        self._knit_graph.add_loop(loop)        
                        # update because change incurred 
                        self._knit_graph.node_to_course_and_wale[loop_id] = (course_id, wale_id)
                        # update node bed info
                        self._knit_graph.node_on_front_or_back[loop_id] = bed
                        self._knit_graph.course_and_wale_and_bed_to_node[((course_id, wale_id), bed)] = loop_id
                        self._knit_graph.node_to_course_and_wale_and_bed[loop_id] = ((course_id, wale_id), bed)
                        i+=1
            # print(f'nodes on yarn {yarn.yarn_id} is {yarn.yarn_graph.nodes}')
            # print(f'yarn_edges is {yarn.yarn_graph.edges}')
        # print(f'self._knit_graph.node_to_course_and_wale is {self._knit_graph.node_to_course_and_wale}')
        
    def connect_stitches_on_knitgraph(self):
        # print(f'self._knit_graph.graph.edges before reconnect stitch is {self._knit_graph.graph.edges}')
        self._knit_graph.graph.remove_edges_from([*self._knit_graph.graph.edges])
        for (parent_coor, parent_bed, child_coor, child_bed, attr_dict) in self.knitgraph_coors_connectivity:
            parent_node = self._knit_graph.course_and_wale_and_bed_to_node[(parent_coor, parent_bed)]
            child_node = self._knit_graph.course_and_wale_and_bed_to_node[(child_coor, child_bed)]
            pull_direction = attr_dict['pull_direction']
            depth = attr_dict['depth']
            parent_offset = attr_dict['parent_offset']
            self._knit_graph.connect_loops(parent_node, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
        # print(f'self._knit_graph.graph.edges after reconnect stitch is {self._knit_graph.graph.edges}')

    def add_hole(self):
        #first determine the validity of the input hole
        # self.hole_shape_and_number_constraints()
        #return info including hole_start_wale, hole_end_wale, hole_start_course, hole_end_course, hole_height and hole_width.
        self.get_hole_size()
        #send out warning to user if special stitch might be broken or if hole node is set at places like top course.
        self.hole_location_errors()
        self.hole_location_warnings()
        # get course_to_wale_ids for hole area
        self.get_hole_course_to_wale_ids()
        self.get_course_id_to_wale_ids()
        path_result, remain_subgraphs, G1 = self.find_shortest_path_for_tube()
        #remove nodes for hole from both knit graph and yarn graph.
        self.remove_hole_nodes_from_graph()
        if path_result == None:
            print('can not find feasible solution to walk through the nodes on the graph')
            exit()
        self.remove_old_and_add_new_yarn(path = path_result, remain_subgraphs = remain_subgraphs, G1 = G1)
        #connect unstable (have no child loops) nodes on the edge of the hole to the nearest top neighbor to prevent them from falling off the parent loops,
        #leading the hole bigger and bigger.
        # self.connect_hole_edge_nodes()
        # # to prevent hole deformation, we can also use the bind-off
        self.bind_off()
        # 
        self.read_connectivity_from_knitgraph()
        # 
        self.rebuild_yarn_graph()
        # 
        self.connect_stitches_on_knitgraph()
        # # note that we only update (delete hole nodes on the self._knit_graph, we do not correspondingly update nodes in both self._knit_graph.node_on_front_or_back and self._knit_graph.node_to_course_and_wale)
        # KnitGraph_Visualizer = knitGraph_visualizer(self._knit_graph,  object_type = 'tube')
        # KnitGraph_Visualizer.visualize()
        return self._knit_graph



