from typing import Optional, List, Dict, Tuple
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from debugging_tools.polygon_knitgraphs import *
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
import warnings

class Pocket_Generator:
    def __init__(self, parent_knitgraph: Knit_Graph, old_carrier_id:int, new_carrier_id: int, left_keynodes_child_fabric, right_keynodes_child_fabric, spliting_nodes, parent_graph_course_to_loop_ids: Optional[Dict[int, List[int]]] = None, parent_graph_node_to_course_and_wale: Optional[Dict[int, Tuple[int, int]]] = None, parent_graph_course_and_wale_to_node: Optional[Dict[Tuple[int, int], int]] = None, parent_graph_is_polygon: bool = False, unmodified: bool = True, child_graph_is_polygon: bool = True):
        """
        :param left_keypoints: List of (course_id, wale_id) of the spiky points on the left side of the pattern.
        :param right_keypoints: List of (course_id, wale_id) of the spiky points on the right side of the pattern.
        (Note that the keypoints should be enter in order of from bottom to top for each side, and we assume the origin
        of the pattern is (0, 0). )
        """
        self.parent_knitgraph: Knit_Graph = parent_knitgraph
        self.child_knitgraph: Knit_Graph = Knit_Graph()
        self.parent_knitgraph_coors_connectivity: List[Tuple] = []
        self.child_knitgraph_coors_connectivity: List[Tuple] = []
        self.left_keynodes_child_fabric: List[Tuple[int, int]] = left_keynodes_child_fabric
        self.right_keynodes_child_fabric: List[Tuple[int, int]] = right_keynodes_child_fabric
        #self._knit_graph is pocket graph, the result of processing given child graph and parent graph.
        self._knit_graph: Knit_Graph = Knit_Graph()
        self.old_carrier_id: int = old_carrier_id
        self.old_yarn: Yarn = Yarn("old_yarn", self._knit_graph, carrier_id=self.old_carrier_id)
        self._knit_graph.add_yarn(self.old_yarn)
        self.new_carrier_id: int = new_carrier_id
        self.new_yarn: Yarn = Yarn("new_yarn", self._knit_graph, carrier_id=self.new_carrier_id)
        self._knit_graph.add_yarn(self.new_yarn)
        #
        self.child_knitgraph_demo_yarn: Yarn = Yarn("demo_yarn", self.child_knitgraph, carrier_id=2)
        self.child_knitgraph.add_yarn(self.child_knitgraph_demo_yarn)
        #
        self.parent_graph_loop_id_to_course: Dict[int, float] 
        self.parent_graph_course_to_loop_ids: Dict[float, List[int]]
        self.parent_graph_loop_id_to_wale: Dict[int, float] 
        self.parent_graph_wale_to_loop_ids: Dict[float, List[int]]
        self.parent_graph_node_to_course_and_wale: Dict[int, Tuple(int, int)]
        self.parent_graph_course_and_wale_to_node: Dict[Tuple[int, int], int] 
        self.parent_graph_course_id_to_wale_ids: Dict[int, List[int]] = {}
        # 
        self.child_graph_course_to_loop_ids: Dict[float, List[int]]
        self.child_graph_node_to_course_and_wale: Dict[int, Tuple(int, int)]
        self.child_graph_course_and_wale_to_node: Dict[Tuple[int, int], int] 
        self.child_graph_course_id_to_wale_ids: Dict[int, List[int]] = {}
        #
        self.pocket_graph_loop_id_to_course: Dict[int, float] 
        self.pocket_graph_loop_id_to_wale: Dict[int, float] 
        self.pocket_graph_course_to_loop_ids: Dict[float, List[int]]
        self.pocket_graph_wale_to_loop_ids: Dict[float, List[int]]
        self.pocket_graph_node_to_course_and_wale: Dict[int, Tuple(int, int)]
        self.pocket_graph_course_and_wale_to_node: Dict[Tuple[int, int], int]   
        # 
        if parent_graph_is_polygon == False: #then the input knit graph is a common retangle, it is safe to invoke knitgraph.get_course() to get correct info.
            self.parent_graph_loop_id_to_course, self.parent_graph_course_to_loop_ids, self.parent_graph_loop_id_to_wale, self.parent_graph_wale_to_loop_ids = self.parent_knitgraph.get_courses(unmodified)
            self.get_nodes_course_and_wale()
        elif parent_graph_is_polygon == True:
            assert parent_graph_course_to_loop_ids is not None
            assert parent_graph_node_to_course_and_wale is not None
            assert parent_graph_course_and_wale_to_node is not None
            self.parent_graph_course_to_loop_ids, self.parent_graph_node_to_course_and_wale, self.parent_graph_course_and_wale_to_node = parent_graph_course_to_loop_ids, parent_graph_node_to_course_and_wale, parent_graph_course_and_wale_to_node
        self.parent_graph_is_polygon: bool = parent_graph_is_polygon
        self._unmodified: bool = unmodified  
        # 
        assert child_graph_is_polygon == True
        self.child_graph_is_polygon: bool = child_graph_is_polygon
        #
        self.sorted_spliting_nodes: List[int] = sorted(spliting_nodes, reverse=True)
        # self.spliting_nodes[0] is to randomly pick a node from splitting nodes to get splitting course id.
        self.spliting_starting_course_id: int = self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[0]][0]

    def get_nodes_course_and_wale(self):
        """
        Get the [course, wale] coordinate of each node in the knit graph.
        """
        self.parent_graph_node_to_course_and_wale = {}
        for node in self.parent_knitgraph.graph.nodes:
            course = self.parent_graph_loop_id_to_course[node]
            wale = self.parent_graph_loop_id_to_wale[node]
            self.parent_graph_node_to_course_and_wale[node] = (course, wale)
        #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
        self.parent_graph_course_and_wale_to_node = {tuple(v): k for k, v in self.parent_graph_node_to_course_and_wale.items()}
        

    def check_keynodes_validity(self): 
        """
        non-symmetry is now allowable for the shape.
        check if keynodes are entered correctly: for any two neighbor keynodes to be valid, to make sure
        no other keynodes is mistakenly ingored bewtween this range, delta wale_id % delta course_id should
        == 0.
        """
        # first ensure even for situation where keynode on the left side and the right side turns out to be the same,
        # e.g, a bottom vertex of a triangle, users enter that special keynode into both self.left_keynodes_child_fabric and
        # self.right_keynodes_child_fabric keynodes lists.
        first_keynode_left =  self.left_keynodes_child_fabric[0]
        last_keynode_left = self.left_keynodes_child_fabric[-1]
        first_keynode_right =  self.right_keynodes_child_fabric[0]
        last_keynode_right = self.right_keynodes_child_fabric[-1]
        assert first_keynode_left[0] == first_keynode_right[0], f'first keynode on the left and right do not share the same course_id'
        assert last_keynode_left[0] == last_keynode_right[0], f'last keynode on the left and right do not share the same course_id'
        #
        assert self.spliting_starting_course_id + 1 == first_keynode_left[0] == first_keynode_right[0], f'start course id on child fabric \
            should be {self.spliting_starting_course_id + 1}'
        if self.spliting_starting_course_id % 2 == 0:
            assert first_keynode_left[1] == self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[-1]][1], \
                f'wale id of first keynode on the left: {first_keynode_left[1]} does not match the wale id of the splitting node: {self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[-1]][1]}'
            assert first_keynode_right[1] == self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[0]][1], \
                f'wale id of first keynode on the right: {first_keynode_right[1]} does not match the wale id of the splitting node: {self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[0]][1]}'
        elif self.spliting_starting_course_id % 2 == 1:
            assert first_keynode_left[1] == self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[0]][1], \
                f'wale id of first keynode on the left: {first_keynode_left[1]} does not match the wale id of the splitting node: {self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[0]][1]}'
            assert first_keynode_right[1] == self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[-1]][1], \
                f'wale id of first keynode on the right: {first_keynode_right[1]} does not match the wale id of the splitting node: {self.parent_graph_node_to_course_and_wale[self.sorted_spliting_nodes[-1]][1]}'
        #
        num_of_nodes_left_side = len(self.left_keynodes_child_fabric)
        num_of_nodes_right_side = len(self.right_keynodes_child_fabric)
        for i in range(1, num_of_nodes_left_side):
            curr_left_keynode = self.left_keynodes_child_fabric[i]
            last_left_keynode = self.left_keynodes_child_fabric[i-1] 
            width_change_left = curr_left_keynode[1] - last_left_keynode[1]
            increase_height_left = curr_left_keynode[0] - last_left_keynode[0]
            #check if any other keynodes might be missed in between 
            if width_change_left % increase_height_left != 0:
                print(f'some keynodes might exist bewtween given keynodes {last_left_keynode} and {curr_left_keynode} on the left side if these two keynodes are entered correctly')
                exit()
        for i in range(1, num_of_nodes_right_side):    
            curr_right_keynode = self.right_keynodes_child_fabric[i]
            last_right_keynode = self.right_keynodes_child_fabric[i-1]
            width_change_right = curr_right_keynode[1] - last_right_keynode[1]
            increase_height_right = curr_right_keynode[0] - last_right_keynode[0]
            if width_change_right % increase_height_right != 0:
                print(f'some keynodes might exist bewtween given keynodes {last_right_keynode} and {curr_right_keynode} on the right side if these two keynodes are entered correctly')
                exit()
                
    def generate_polygon_from_keynodes(self):
        self.check_keynodes_validity()
        # first process given keynodes on each side, to get starting node coordinate and ending node coordinate on each course.
        starting_nodes_coor = []
        ending_nodes_coor = []
        num_of_nodes_left_side = len(self.left_keynodes_child_fabric) 
        num_of_nodes_right_side = len(self.right_keynodes_child_fabric) 
        # for keynodes on the left side
        # before for loop, add the starting node on the first course
        starting_nodes_coor_on_first_course = ((self.left_keynodes_child_fabric[0][0], self.left_keynodes_child_fabric[0][1]))
        starting_nodes_coor.append(starting_nodes_coor_on_first_course)
        for i in range(1, num_of_nodes_left_side):
            curr_left_keynode = self.left_keynodes_child_fabric[i]
            last_left_keynode = self.left_keynodes_child_fabric[i-1]
            # if wale_id keeps the same between this course range, for courses in between, only need to increment the course_id for 
            # starting node 
            if curr_left_keynode[1] - last_left_keynode[1] == 0:
                wale_id = last_left_keynode[1]
                for course_id in range(last_left_keynode[0] + 1, curr_left_keynode[0] + 1):
                    starting_nodes_coor.append((course_id, wale_id))
            # if wale_id changes between this course range, for courses in between, also need to increment the wale_id by 
            # "wale_change_per_course" for starting node 
            elif curr_left_keynode[1] - last_left_keynode[1] != 0:
                wale_id = last_left_keynode[1]
                width_change_left = (curr_left_keynode[1] - last_left_keynode[1])
                height_increase_left = (curr_left_keynode[0] - last_left_keynode[0])
                wale_change_per_course = int(width_change_left / height_increase_left)
                for course_id in range(last_left_keynode[0] + 1, curr_left_keynode[0] + 1):
                    wale_id += wale_change_per_course
                    starting_nodes_coor.append((course_id, wale_id))
        # same for keynodes on the right side
        ending_nodes_coor_on_first_course = ((self.right_keynodes_child_fabric[0][0], self.right_keynodes_child_fabric[0][1]))
        ending_nodes_coor.append(ending_nodes_coor_on_first_course)
        for i in range(1, num_of_nodes_right_side):
            curr_right_keynode = self.right_keynodes_child_fabric[i]
            last_right_keynode = self.right_keynodes_child_fabric[i-1]
            if curr_right_keynode[1] - last_right_keynode[1] == 0:
                wale_id = last_right_keynode[1]
                for course_id in range(last_right_keynode[0] + 1, curr_right_keynode[0] + 1):
                    ending_nodes_coor.append((course_id, wale_id))
            elif curr_right_keynode[1] - last_right_keynode[1] != 0:
                wale_id = last_right_keynode[1]
                width_change_right = (curr_right_keynode[1] - last_right_keynode[1])
                height_increase_right = (curr_right_keynode[0] - last_right_keynode[0])
                wale_change_per_course = int(width_change_right / height_increase_right)
                for course_id in range(last_right_keynode[0] + 1, curr_right_keynode[0] + 1):
                    wale_id += wale_change_per_course
                    ending_nodes_coor.append((course_id, wale_id))
        print(f'starting_nodes_coor is {starting_nodes_coor}, ending_nodes_coor is {ending_nodes_coor}')

        #derive node_to_course_and_wale from above starting_nodes_coor and ending_nodes_coor
        node = 0
        node_to_course_and_wale = {}
        for i in range(len(starting_nodes_coor)):
            staring_node_wale_id = starting_nodes_coor[i][1]
            ending_node_wale_id = ending_nodes_coor[i][1]
            course_id = starting_nodes_coor[i][0]
            if course_id % 2 == 0:
                for wale_id in range(staring_node_wale_id, ending_node_wale_id + 1):
                    node_to_course_and_wale[node] = (course_id, wale_id)
                    node += 1
            elif course_id % 2 == 1:
                for wale_id in range(ending_node_wale_id, staring_node_wale_id - 1, -1):
                    node_to_course_and_wale[node] = (course_id, wale_id)
                    node += 1
        print(f'node_to_course_and_wale is {node_to_course_and_wale}')
        self.child_graph_node_to_course_and_wale = node_to_course_and_wale
        #connect nodes on yarn
        for node in node_to_course_and_wale.keys():
            loop_id, loop = self.child_knitgraph_demo_yarn.add_loop_to_end()
            self.child_knitgraph.add_loop(loop)
        #get course_to_loop_ids
        course_to_loop_ids = {}
        course_id_start = starting_nodes_coor_on_first_course[0]
        course_id_end = starting_nodes_coor[-1][0]
        for course_id in range(course_id_start, course_id_end + 1):
            course_to_loop_ids[course_id] = []
        for node in self.child_knitgraph.graph.nodes:
            course_id = node_to_course_and_wale[node][0]
            course_to_loop_ids[course_id].append(node)
        print(f'course_to_loop_ids is {course_to_loop_ids}')
        self.child_graph_course_to_loop_ids = course_to_loop_ids
        #reverse node_to_course_and_wale to get course_and_wale_to_node
        course_and_wale_to_node = {}
        course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
        self.child_graph_course_and_wale_to_node = course_and_wale_to_node
        #connect node stitches
        course_ids_before_final_course = [*course_to_loop_ids.keys()][:-1]
        for course_id in course_ids_before_final_course:
            for node in course_to_loop_ids[course_id]:
                wale_id = node_to_course_and_wale[node][1]
                #find upper neighbor node
                if (course_id + 1, wale_id) in course_and_wale_to_node.keys():
                    child_loop = course_and_wale_to_node[(course_id + 1, wale_id)]
                    self.child_knitgraph.connect_loops(node, child_loop)
        visualize_knitGraph(self.child_knitgraph, node_to_course_and_wale = node_to_course_and_wale, object_type = 'sheet', unmodified = False)
             
    def read_connectivity_from_knitgraph(self):
        """
        transform edge_data_list where connectivity is expressed in terms of node id into coor_connectivity where connectivity is
        expressed in terms of coordinate in formart of (course_id, wale_id). This transform is needed because we are going to 
        change the node order to represent the correct knitting operation order when knitting a pocket, thus at each coor, the node
        id would change, that's why we need to update node_to_course_and_wale for both parent graph and child graph.
        """
        parent_knitgraph_edge_data_list = self.parent_knitgraph.graph.edges(data=True)
        child_knitgraph_edge_data_list = self.child_knitgraph.graph.edges(data=True)
        for edge_data in parent_knitgraph_edge_data_list:
            node = edge_data[1]
            node_coor = self.parent_graph_node_to_course_and_wale[node]
            predecessor = edge_data[0]
            predecessor_coor = self.parent_graph_node_to_course_and_wale[predecessor]
            attr_dict = edge_data[2]
            self.parent_knitgraph_coors_connectivity.append([predecessor_coor, node_coor, attr_dict])
        for edge_data in child_knitgraph_edge_data_list:
            node = edge_data[1]
            node_coor = self.child_graph_node_to_course_and_wale[node]
            predecessor = edge_data[0]
            predecessor_coor = self.child_graph_node_to_course_and_wale[predecessor]
            attr_dict = edge_data[2]
            self.child_knitgraph_coors_connectivity.append([predecessor_coor, node_coor, attr_dict])
            
    def get_course_id_to_wale_ids(self):
        for course_id in [*self.parent_graph_course_to_loop_ids.keys()]:
            start_node = self.parent_graph_course_to_loop_ids[course_id][0]
            last_node = self.parent_graph_course_to_loop_ids[course_id][-1]
            start_wale_id = self.parent_graph_node_to_course_and_wale[start_node][1]
            last_wale_id = self.parent_graph_node_to_course_and_wale[last_node][1]
            self.parent_graph_course_id_to_wale_ids[course_id] = []
            if course_id % 2 == 0:
                for wale_id in range(start_wale_id, last_wale_id+1):
                    self.parent_graph_course_id_to_wale_ids[course_id].append(wale_id)
            if course_id % 2 == 1:
                for wale_id in range(start_wale_id, last_wale_id-1, -1):
                    self.parent_graph_course_id_to_wale_ids[course_id].append(wale_id)
        #for child graph
        for course_id in [*self.child_graph_course_to_loop_ids.keys()]:
            start_node = self.child_graph_course_to_loop_ids[course_id][0]
            last_node = self.child_graph_course_to_loop_ids[course_id][-1]
            start_wale_id = self.child_graph_node_to_course_and_wale[start_node][1]
            last_wale_id = self.child_graph_node_to_course_and_wale[last_node][1]
            self.child_graph_course_id_to_wale_ids[course_id] = []
            if course_id % 2 == 0:
                for wale_id in range(start_wale_id, last_wale_id+1):
                    self.child_graph_course_id_to_wale_ids[course_id].append(wale_id)
            if course_id % 2 == 1:
                for wale_id in range(start_wale_id, last_wale_id-1, -1):
                    self.child_graph_course_id_to_wale_ids[course_id].append(wale_id)

    def build_rows_on_parent_graph_just_above_splitting_course_id(self):
        #here we can clear old self.parent_graph_node_to_course_and_wale since we don't use it anymore hereafter
        self.parent_graph_node_to_course_and_wale = {}
        start_course_id = [*self.parent_graph_course_id_to_wale_ids.keys()][0]
        for course_id in range(start_course_id, self.spliting_starting_course_id + 2):
            for i in range(len(self.parent_graph_course_id_to_wale_ids[course_id])):
                loop_id, loop = self.old_yarn.add_loop_to_end()
                self._knit_graph.add_loop(loop)
                wale_id = self.parent_graph_course_id_to_wale_ids[course_id][i]
                self.parent_graph_node_to_course_and_wale[loop_id] = (course_id, wale_id)
    
    def grow_one_row(self, course_id, on_parent_graph: bool):
        if on_parent_graph == True:
            self.parent_graph_course_to_loop_ids[course_id] = []
            for i in range(len(self.parent_graph_course_id_to_wale_ids[course_id])):
                loop_id, loop = self.old_yarn.add_loop_to_end()
                self._knit_graph.add_loop(loop)
                wale_id = self.parent_graph_course_id_to_wale_ids[course_id][i]
                self.parent_graph_node_to_course_and_wale[loop_id] = (course_id, wale_id)
                self.parent_graph_course_to_loop_ids[course_id].append(loop_id)
        elif on_parent_graph == False:
            self.child_graph_course_to_loop_ids[course_id] = []
            for i in range(len(self.child_graph_course_id_to_wale_ids[course_id])):
                loop_id, loop = self.new_yarn.add_loop_to_end()
                self._knit_graph.add_loop(loop)
                wale_id = self.child_graph_course_id_to_wale_ids[course_id][i]
                self.child_graph_node_to_course_and_wale[loop_id] = (course_id, wale_id)
                self.child_graph_course_to_loop_ids[course_id].append(loop_id)
            #connect bottom row of child fabric to splitting row
            if course_id == [*self.child_graph_course_to_loop_ids.keys()][0]:
                self.spliting_width = len(self.sorted_spliting_nodes)
                for i in range(self.spliting_width):
                    parent_loop_id = self.sorted_spliting_nodes[i]
                    loop_id = self.child_graph_course_to_loop_ids[course_id][i]
                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
            # print('child', (course_id, wale_id), loop_id)

    # @deprecated("Deprecated because this simply divides edges into only left(smaller wale) and right side(bigger wale)")
    def deprecated_get_edge_nodes_on_child_fabric(self):
        smaller_wale_edge_nodes = []
        bigger_wale_edge_nodes = []
        for course_id in self.child_graph_course_to_loop_ids.keys():
            if course_id % 2 == 0:
                smaller_wale_edge_nodes.append(self.child_graph_course_to_loop_ids[course_id][0])
                bigger_wale_edge_nodes.append(self.child_graph_course_to_loop_ids[course_id][-1])
            elif course_id % 2 == 1:
                smaller_wale_edge_nodes.append(self.child_graph_course_to_loop_ids[course_id][-1])
                bigger_wale_edge_nodes.append(self.child_graph_course_to_loop_ids[course_id][0])
        print(f'smaller wale edge nodes on child knitgraph is {smaller_wale_edge_nodes}, bigger wale edge nodes on child knitgraph is {bigger_wale_edge_nodes}')
        return smaller_wale_edge_nodes, bigger_wale_edge_nodes
                 
    # @deprecated("Deprecated because this simply divides edges into only left(smaller wale) and right side(bigger wale)")
    def deprecated_get_target_edge_nodes_on_parent_fabric(self, bigger_wale_edge_nodes, smaller_wale_edge_nodes):
        bigger_wale_target_edge_nodes = []
        smaller_wale_target_edge_nodes = []
        for node in bigger_wale_edge_nodes:
            course_id = self.child_graph_node_to_course_and_wale[node][0]
            wale_id = self.child_graph_node_to_course_and_wale[node][1]
            bigger_wale_target_edge_nodes.append(self.parent_graph_course_and_wale_to_node[(course_id, wale_id + 1)])
        for node in smaller_wale_edge_nodes:
            course_id = self.child_graph_node_to_course_and_wale[node][0]
            wale_id = self.child_graph_node_to_course_and_wale[node][1]
            smaller_wale_target_edge_nodes.append(self.parent_graph_course_and_wale_to_node[(course_id, wale_id - 1)])
        print(f'bigger_wale_target_edge_nodes on parent knitgraph is {bigger_wale_target_edge_nodes}, smaller_wale_target_edge_nodes on parent knitgraph is {smaller_wale_target_edge_nodes}')
        return smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes

    def connect_stitches_on_knitgraph(self):
        for (parent_coor, child_coor, attr_dict) in self.parent_knitgraph_coors_connectivity:
            parent_node = self.parent_graph_course_and_wale_to_node[parent_coor]
            child_node = self.parent_graph_course_and_wale_to_node[child_coor]
            pull_direction = attr_dict['pull_direction']
            depth = attr_dict['depth']
            parent_offset = attr_dict['parent_offset']
            self._knit_graph.connect_loops(parent_node, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
        for (parent_coor, child_coor, attr_dict) in self.child_knitgraph_coors_connectivity:
            parent_node = self.child_graph_course_and_wale_to_node[parent_coor]
            child_node = self.child_graph_course_and_wale_to_node[child_coor]
            pull_direction = attr_dict['pull_direction']
            depth = attr_dict['depth']
            parent_offset = attr_dict['parent_offset']
            self._knit_graph.connect_loops(parent_node, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)

    # @deprecated("Deprecated because this uses edges simply divided into left(smaller wale) and right side(bigger wale), while there might be case such as 
    #  a zipper jacket pocket where we connect only two edges on the right side as well as the left edge")
    def deprecated_actions_around_target_edge_node(self, smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes, smaller_wale_edge_connected: bool, bigger_wale_edge_connected: bool):
        # no need to remove target edge node on parent fabric because we do not lose any node
        if bigger_wale_edge_connected == True:
            for node in bigger_wale_target_edge_nodes:
                course_id = self.parent_graph_node_to_course_and_wale[node][0]
                wale_id = self.parent_graph_node_to_course_and_wale[node][1]
                target_node_on_child_fabric = self.child_graph_course_and_wale_to_node[(course_id, wale_id - 1)]
                if (course_id-1, wale_id) in self.parent_graph_course_and_wale_to_node:
                    edge_split_node = self.parent_graph_course_and_wale_to_node[(course_id-1, wale_id)]
                    self._knit_graph.connect_loops(edge_split_node, target_node_on_child_fabric)

        if smaller_wale_edge_connected == True:
            for node in smaller_wale_target_edge_nodes:
                course_id = self.parent_graph_node_to_course_and_wale[node][0]
                wale_id = self.parent_graph_node_to_course_and_wale[node][1]
                target_node_on_child_fabric = self.child_graph_course_and_wale_to_node[(course_id, wale_id + 1)]
                if (course_id-1, wale_id) in self.parent_graph_course_and_wale_to_node:
                    edge_split_node = self.parent_graph_course_and_wale_to_node[(course_id-1, wale_id)]
                    self._knit_graph.connect_loops(edge_split_node, target_node_on_child_fabric)

    # @wrong("Deprecated because this is incorrect but quite deceptive knitgraph representation of a pocket")
    def wrong_actions_around_target_edge_node(self, smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes, smaller_wale_edge_connected: bool, bigger_wale_edge_connected: bool):
        #first transfer connections associated to nodes in bigger_wale_target_edge_nodes to target_node_on_child_fabric
        #then remove target edge node on parent fabric
        if bigger_wale_edge_connected == True:
            for node in bigger_wale_target_edge_nodes:
                # print('haha', self._knit_graph.graph.in_edges(node), len(self._knit_graph.graph.in_edges(node)), self._knit_graph.graph.get_edge_data(*[*self._knit_graph.graph.in_edges(node)][0]))
                course_id = self.parent_graph_node_to_course_and_wale[node][0]
                wale_id = self.parent_graph_node_to_course_and_wale[node][1]
                target_node_on_child_fabric = self.child_graph_course_and_wale_to_node[(course_id, wale_id - 1)]
                if len(self._knit_graph.graph.in_edges(node)) > 0:
                    in_edges = self._knit_graph.graph.in_edges(node)
                    for in_edge in in_edges:
                        parent_node = in_edge[0]
                        attr_dict = self._knit_graph.graph.get_edge_data(*in_edge)
                        pull_direction = attr_dict['pull_direction']
                        depth = attr_dict['depth']
                        parent_offset = attr_dict['parent_offset']
                        self._knit_graph.connect_loops(parent_node, target_node_on_child_fabric, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
                if len(self._knit_graph.graph.out_edges(node)) > 0:
                    out_edges = self._knit_graph.graph.out_edges(node)
                    for out_edge in out_edges:
                        child_node = out_edge[1]
                        attr_dict = self._knit_graph.graph.get_edge_data(*out_edge)
                        pull_direction = attr_dict['pull_direction']
                        depth = attr_dict['depth']
                        parent_offset = attr_dict['parent_offset']
                        self._knit_graph.connect_loops(target_node_on_child_fabric, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
                if len(self.old_yarn.yarn_graph.in_edges(node)) > 0:
                    in_edges = self.old_yarn.yarn_graph.in_edges(node)
                    for in_edge in in_edges:
                        parent_node = in_edge[0]
                        self.old_yarn.yarn_graph.add_edge(parent_node, target_node_on_child_fabric)
                if len(self.old_yarn.yarn_graph.out_edges(node)) > 0:
                    out_edges = self.old_yarn.yarn_graph.out_edges(node)
                    for out_edge in out_edges:
                        child_node = out_edge[1]
                        self.old_yarn.yarn_graph.add_edge(target_node_on_child_fabric, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
                self._knit_graph.graph.remove_node(node) 
                self.old_yarn.yarn_graph.remove_node(node)
                del self.parent_graph_course_and_wale_to_node[self.parent_graph_node_to_course_and_wale[node]]
                del self.pocket_graph_node_to_course_and_wale[node]
        if smaller_wale_edge_connected == True:
            for node in smaller_wale_target_edge_nodes:
                course_id = self.parent_graph_node_to_course_and_wale[node][0]
                wale_id = self.parent_graph_node_to_course_and_wale[node][1]
                target_node_on_child_fabric = self.child_graph_course_and_wale_to_node[(course_id, wale_id + 1)]
                if len(self._knit_graph.graph.in_edges(node)) > 0:
                    in_edges = self._knit_graph.graph.in_edges(node)
                    for in_edge in in_edges:
                        parent_node = in_edge[0]
                        attr_dict = self._knit_graph.graph.get_edge_data(*in_edge)
                        pull_direction = attr_dict['pull_direction']
                        depth = attr_dict['depth']
                        parent_offset = attr_dict['parent_offset']
                        self._knit_graph.connect_loops(parent_node, target_node_on_child_fabric, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
                if len(self._knit_graph.graph.out_edges(node)) > 0:
                    out_edges = self._knit_graph.graph.out_edges(node)
                    for out_edge in out_edges:
                        child_node = out_edge[1]
                        attr_dict = self._knit_graph.graph.get_edge_data(*out_edge)
                        pull_direction = attr_dict['pull_direction']
                        depth = attr_dict['depth']
                        parent_offset = attr_dict['parent_offset']
                        self._knit_graph.connect_loops(target_node_on_child_fabric, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
                if len(self.old_yarn.yarn_graph.in_edges(node)) > 0:
                    in_edges = self.old_yarn.yarn_graph.in_edges(node)
                    for in_edge in in_edges:
                        parent_node = in_edge[0]
                        self.old_yarn.yarn_graph.add_edge(parent_node, target_node_on_child_fabric)
                if len(self.old_yarn.yarn_graph.out_edges(node)) > 0:
                    out_edges = self.old_yarn.yarn_graph.out_edges(node)
                    for out_edge in out_edges:
                        child_node = out_edge[1]
                        self.old_yarn.yarn_graph.add_edge(target_node_on_child_fabric, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
                self._knit_graph.graph.remove_node(node)
                self.old_yarn.yarn_graph.remove_node(node)
                del self.parent_graph_course_and_wale_to_node[self.parent_graph_node_to_course_and_wale[node]]
                del self.pocket_graph_node_to_course_and_wale[node]
        print(f'updated node dict is {self.pocket_graph_node_to_course_and_wale}')
        # visualize_knitGraph(self._knit_graph, node_to_course_and_wale = self.pocket_graph_course_and_wale_to_node, object_type = 'pocket', unmodified = False) 
    
    # @deprecated("Deprecated because this uses edges simply divided into left(smaller wale) and right side(bigger wale). Besides, in rewritten version, parameters are
    # moved to "def __init__()".
    def deprecated_build_pocket_graph(self, close_top: bool = False, smaller_wale_edge_connected: bool = False, bigger_wale_edge_connected: bool = False) -> Knit_Graph:   
        self.generate_polygon_from_keynodes()
        self.read_connectivity_from_knitgraph()
        self.get_course_id_to_wale_ids()
        self.build_rows_on_parent_graph_just_above_splitting_course_id()
        #clear old self.child_graph_node_to_course_and_wale
        self.child_graph_node_to_course_and_wale = {}
        self.grow_one_row(course_id = [*self.child_graph_course_to_loop_ids.keys()][0], on_parent_graph = False)
        for course_id in [*self.child_graph_course_to_loop_ids.keys()][1:]:
            self.grow_one_row(course_id, on_parent_graph = True)
            self.grow_one_row(course_id, on_parent_graph = False)
        last_course_id_child_fabric = [*self.child_graph_course_to_loop_ids.keys()][-1]
        last_course_id_parent_fabric = [*self.parent_graph_course_to_loop_ids.keys()][-1]
        for course_id in range(last_course_id_child_fabric + 1, last_course_id_parent_fabric + 1):
            self.grow_one_row(course_id, on_parent_graph = True)
        #get updated course_and_wale_to_node on child knitgraph and parent knitgraph
        self.parent_graph_course_and_wale_to_node = {tuple(v): k for k, v in self.parent_graph_node_to_course_and_wale.items()}
        self.child_graph_course_and_wale_to_node = {tuple(v): k for k, v in self.child_graph_node_to_course_and_wale.items()}
        #merge node_to_course_and_wale on parent_knitgraph and child_knitgraph
        self.pocket_graph_node_to_course_and_wale = self.parent_graph_node_to_course_and_wale|self.child_graph_node_to_course_and_wale
        #see if close top
        if close_top == True:
            for node in self.child_graph_course_to_loop_ids[last_course_id_child_fabric]:
                course_and_wale = self.pocket_graph_node_to_course_and_wale[node]
                print(f'node to connect on child fabric is {node}')
                for key, value in self.pocket_graph_node_to_course_and_wale.items():
                    if course_and_wale == value and key != node:
                        print(f'node to connect on parent fabric is {key}')
                        self._knit_graph.connect_loops(node, key)
        #see if connect edges
        smaller_wale_edge_nodes, bigger_wale_edge_nodes = self.deprecated_get_edge_nodes_on_child_fabric()
        smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes = self.deprecated_get_target_edge_nodes_on_parent_fabric(bigger_wale_edge_nodes, smaller_wale_edge_nodes)
        self.connect_stitches_on_knitgraph()
        self.wrong_actions_around_target_edge_node(smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes, smaller_wale_edge_connected, bigger_wale_edge_connected)
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = self.pocket_graph_node_to_course_and_wale, object_type = 'pocket', unmodified = False) 
        return self._knit_graph

