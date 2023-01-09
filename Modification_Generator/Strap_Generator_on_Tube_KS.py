from typing import Optional, List, Dict, Tuple
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph, Pull_Direction
from debugging_tools.final_knit_graph_viz import knitGraph_visualizer
from debugging_tools.simple_knitgraph_generator import Simple_Knitgraph_Generator
from debugging_tools.polygon_generator import Polygon_Generator
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler

class Strap_Generator_on_Tube:
    def __init__(self, parent_knitgraph: Knit_Graph, tube_yarn_carrier_id: int, straps_coor_info: Dict[int, Dict[str, Tuple[int, int]]], strap_height: int):
        """
        note that we do not use left_keynodes and right_keynodes here anymore for strap case, because we assume straps are all rectangular
        shape, we do not support polygon-shaped strap here.
        """
        # strap dict info: strap_info = 
        # {1:{'front':(small_wale_front, big_wale_front), 'back':(small_wale_back, big_wale_back)},
        #  2:{'front':(small_wale_front, big_wale_front), 'back':(small_wale_back, big_wale_back)}}
        # similarly, we would need course_to_loop_ids for different straps
        # {1:{'front':(small_wale_front, big_wale_front), 'back':(small_wale_back, big_wale_back)},
        #  2:{'front':(small_wale_front, big_wale_front), 'back':(small_wale_back, big_wale_back)}}

        #self.strap_graph is strap graph, the result of processing given child graph and parent graph.
        self.strap_graph: Knit_Graph = Knit_Graph()
        self.parent_knitgraph: Knit_Graph = parent_knitgraph
        assert self.parent_knitgraph.object_type == 'tube', f'wrong object type of parent knitgraph'
        self.strap_graph.object_type = 'tube'
        self.child_knitgraph: Knit_Graph = Knit_Graph()
        self.child_knitgraph.object_type = 'sheet'
        self.straps_coor_info = straps_coor_info
        self.ordered_strap_coor: List[Tuple(int, int)] = []
        self.ordered_straps_yarns: List[Yarn] = []
        self.ordered_straps_node_to_course_and_wale: List[Dict[int, Tuple(int, int)]] = []
        self.front_straps_top_course_wale_ids: Dict[int, List[int]] = {} #used in bind_off()
        self.back_straps_top_course_wale_ids: Dict[int, List[int]] = {}
        self.straps_top_course_wale_ids: Dict[int, List[int]] = {}
        self.strap_height = strap_height
        self.child_knitgraph_coors_connectivity: List[Tuple] = []
        self.parent_knitgraph_coors_connectivity: List[Tuple] = []
        # assert 1/3 <= self.parent_knitgraph.gauge <= 0.5, f'the gauge of given parent knitgraph has to be less than 0.5, and suggested gauge should be larger than 1/3 to avoid racking over +-2.' #otherwise it will mess up because xfers involved.
        assert self.parent_knitgraph.gauge == 0.5, f'the gauge of given parent knitgraph has to be less than 0.5, and we set it to 0.5 which is sufficient to keep texture for strap on tube case' #otherwise it will mess up because xfers involved.
        self.strap_graph.gauge = self.child_knitgraph.gauge = self.parent_knitgraph.gauge #this is true for adding strap on sheet case
        self.wale_dist = int(1/self.parent_knitgraph.gauge)
        #
        self.parent_knitgraph.loop_ids_to_course: Dict[int, float] = parent_knitgraph.loop_ids_to_course
        self.parent_knitgraph.course_to_loop_ids: Dict[float, List[int]] = parent_knitgraph.course_to_loop_ids
        self.parent_knitgraph.loop_ids_to_wale: Dict[int, float] = parent_knitgraph.loop_ids_to_wale
        self.parent_knitgraph.wale_to_loop_ids: Dict[float, List[int]] = parent_knitgraph.wale_to_loop_ids
        self.parent_knitgraph.node_to_course_and_wale: Dict[int, Tuple(int, int)] = parent_knitgraph.node_to_course_and_wale
        self.parent_knitgraph.node_on_front_or_back: Dict[int, str] = parent_knitgraph.node_on_front_or_back
        self.parent_knitgraph_course_and_wale_to_node: Dict[Tuple[int, int], int] = {tuple(v): k for k, v in parent_knitgraph.node_to_course_and_wale.items()}
        self.parent_knitgraph_course_id_to_wale_ids: Dict[int, List[int]] = {} 
        self.parent_knitgraph_course_and_wale_to_bed: Dict[Tuple(int, int), str] = {} 
        self.parent_knitgraph_bed_to_course_id_to_wale_ids: Dict[str, Dict[int, List[int]]] = {}
        # 
        self.child_knitgraph.course_to_loop_ids: Dict[float, List[int]]
        self.child_knitgraph.node_to_course_and_wale: Dict[int, Tuple(int, int)]
        self.child_knitgraph_course_and_wale_to_node: Dict[Tuple[int, int], int] 
        self.child_knitgraph_course_id_to_wale_ids: Dict[int, List[int]] = {}
        self.child_knitgraph.node_on_front_or_back: Dict[int, str] = {}
        #     
        self.tube_yarn_carrier_id: int = tube_yarn_carrier_id
        self.tube_yarn: Yarn = Yarn("tube_yarn", self.strap_graph, carrier_id=self.tube_yarn_carrier_id)
        self.strap_graph.add_yarn(self.tube_yarn) 
        # note that here we haven't added yarns used for straps into self.strap_graph yet, we will do this in order_strap_coor_for_graph_building() below.
        self.strap_graph.node_to_course_and_wale: Dict[int, Tuple(int, int)]
        self.strap_graph.node_on_front_or_back: Dict[int, str] = {}

    def check_strap_coor_validity(self):
        for strap_coor_info in self.straps_coor_info.values():
            front_strap_coor = strap_coor_info['front']
            back_strap_coor = strap_coor_info['back']
            for front_strap_wale, back_strap_wale in zip(front_strap_coor, back_strap_coor):
                # both front_strap_left_wale and front_strap_right_wale need to be one wale larger than back_strap_left_wale and back_strap_right_wale.
                # (because in Knit_Graph file we set back node wale is always one wale smaller (check "adjusted_wale = max_wale - wale -1" in knit_graph file))
                assert (front_strap_wale - back_strap_wale) == 1, f'given strap coor info is wrong'

    # we would need to build front halves first before starting to build the back halves. so separate front ones and back ones from the
    # strap coor info.
    def order_strap_coor_for_graph_building(self):
        i = 1
        for strap_coor_info in self.straps_coor_info.values():
            front_strap_coor = strap_coor_info['front']
            self.ordered_strap_coor.append(front_strap_coor)
            # 
            yarn = Yarn("front_strap_yarn"+str(i), self.strap_graph, carrier_id=i)
            self.ordered_straps_yarns.append(yarn)
            self.strap_graph.add_yarn(yarn) 
            i+=1
        for strap_coor_info in self.straps_coor_info.values():
            back_strap_coor = strap_coor_info['back']
            self.ordered_strap_coor.append(back_strap_coor)
            # 
            yarn = Yarn("back_strap_yarn"+str(i), self.strap_graph, carrier_id=i)
            self.ordered_straps_yarns.append(yarn)
            self.strap_graph.add_yarn(yarn) 
            i+=1
     
    def generate_polygon_from_keynodes(self):
        #derive node_to_course_and_wale from above starting_nodes_coor and ending_nodes_coor
        node_to_course_and_wale = {}
        node = 0
        strap_starting_course = max([*self.parent_knitgraph.course_to_loop_ids.keys()])
        #normally we would need a different yarn for each half of a straps, i.e., 1 strap would need 2 yarns.
        print(f'self.ordered_strap_coor is {self.ordered_strap_coor}')
        for i, strap_coor in enumerate(self.ordered_strap_coor):
            strap_to_node_to_course_and_wale = {}
            if i<int(len(self.ordered_strap_coor)/2):
                self.front_straps_top_course_wale_ids[i] = []
                self.child_knitgraph_demo_strap_yarn = Yarn("demo_yarn"+'front_strap'+str(i), self.child_knitgraph, carrier_id=i+1)
                self.child_knitgraph.add_yarn(self.child_knitgraph_demo_strap_yarn)
            else:
                self.back_straps_top_course_wale_ids[i] = []
                self.child_knitgraph_demo_strap_yarn = Yarn("demo_yarn"+'back_strap'+str(i), self.child_knitgraph, carrier_id=i+1)
                self.child_knitgraph.add_yarn(self.child_knitgraph_demo_strap_yarn)
            j = 0
            for course_id in range(strap_starting_course, strap_starting_course+self.strap_height):
                staring_node_wale_id = strap_coor[0]
                ending_node_wale_id = strap_coor[1]
                #unlike sheet case,here we change from course_id % 2 to i % 2 because we want the first course in in the direction of 
                # left to right to make it consistent with machine in direction.
                if j % 2 == 0: 
                    for wale_id in range(staring_node_wale_id, ending_node_wale_id + self.wale_dist, self.wale_dist):
                        strap_to_node_to_course_and_wale[node] = (course_id, wale_id)
                        node_to_course_and_wale[node] = (course_id, wale_id)
                        if course_id == strap_starting_course+self.strap_height - 1:
                            if i<int(len(self.ordered_strap_coor)/2):
                                self.front_straps_top_course_wale_ids[i].append(wale_id)
                            else:
                                self.back_straps_top_course_wale_ids[i].append(wale_id)
                        node += 1            
                elif j % 2 == 1:
                    for wale_id in range(ending_node_wale_id, staring_node_wale_id - self.wale_dist, -self.wale_dist):
                        strap_to_node_to_course_and_wale[node] = (course_id, wale_id)
                        node_to_course_and_wale[node] = (course_id, wale_id)
                        if course_id == strap_starting_course+self.strap_height - 1:
                            if i<int(len(self.ordered_strap_coor)/2):
                                self.front_straps_top_course_wale_ids.append(wale_id)
                            else:
                                self.back_straps_top_course_wale_ids.append(wale_id)
                        node += 1      
                j+=1
            self.ordered_straps_node_to_course_and_wale.append(strap_to_node_to_course_and_wale)
            #connect nodes on yarn
            # Note that if use "for node in strap_to_node_to_course_and_wale.keys():", we will get a bug related to node id in strap_to_node_to_course_and_wale.
            for n in strap_to_node_to_course_and_wale.keys():
                loop_id, loop = self.child_knitgraph_demo_strap_yarn.add_loop_to_end()
                if i<int(len(self.ordered_strap_coor)/2):
                    self.child_knitgraph.node_on_front_or_back[loop_id] = 'f'
                else:
                    self.child_knitgraph.node_on_front_or_back[loop_id] = 'b'
                self.child_knitgraph.add_loop(loop)
        # print(f'self.ordered_straps_node_to_course_and_wale is {self.ordered_straps_node_to_course_and_wale}, node_to_course_and_wale is {node_to_course_and_wale}')
        # print(f'self.child_knitgraph.graph.nodes is {self.child_knitgraph.graph.nodes}')
        print(f'self.front_straps_top_course_wale_ids is {self.front_straps_top_course_wale_ids}, self.back_straps_top_course_wale_ids is {self.back_straps_top_course_wale_ids}')
        self.child_knitgraph.node_to_course_and_wale = node_to_course_and_wale
        #get course_to_loop_ids
        course_to_loop_ids = {}
        course_id_start = strap_starting_course
        course_id_end = strap_starting_course+self.strap_height-1
        for course_id in range(course_id_start, course_id_end + 1):
            course_to_loop_ids[course_id] = []
        for node in self.child_knitgraph.graph.nodes:
            course_id = node_to_course_and_wale[node][0]
            course_to_loop_ids[course_id].append(node)
        print(f'course_to_loop_ids is {course_to_loop_ids}')
        self.child_knitgraph.course_to_loop_ids = course_to_loop_ids
        #reverse node_to_course_and_wale to get course_and_wale_to_node
        course_and_wale_to_node = {}
        course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
        self.child_knitgraph_course_and_wale_to_node = course_and_wale_to_node
        #connect node stitches
        course_ids_before_final_course = [*course_to_loop_ids.keys()][:-1]
        for course_id in course_ids_before_final_course:
            for node in course_to_loop_ids[course_id]:
                wale_id = node_to_course_and_wale[node][1]
                #find upper neighbor node
                if (course_id + 1, wale_id) in course_and_wale_to_node.keys():
                    child_loop = course_and_wale_to_node[(course_id + 1, wale_id)]
                    if self.child_knitgraph.node_on_front_or_back[node] == self.child_knitgraph.node_on_front_or_back[child_loop] == 'b':
                        self.child_knitgraph.connect_loops(node, child_loop, pull_direction = Pull_Direction.BtF)
                    else:
                        self.child_knitgraph.connect_loops(node, child_loop, pull_direction = Pull_Direction.BtF)
        KnitGraph_Visualizer = knitGraph_visualizer(knit_graph = self.child_knitgraph)
        KnitGraph_Visualizer.visualize()
             
    def read_connectivity_from_knitgraph(self):
        """
        transform edge_data_list where connectivity is expressed in terms of node id into coor_connectivity where connectivity is
        expressed in terms of coordinate in formart of (course_id, wale_id). This transform is needed because we are going to 
        change the node order to represent the correct knitting operation order when knitting a strap, thus at each coor, the node
        id would change, that's why we need to update node_to_course_and_wale for both parent graph and child graph.
        """
        parent_knitgraph_edge_data_list = self.parent_knitgraph.graph.edges(data=True)
        child_knitgraph_edge_data_list = self.child_knitgraph.graph.edges(data=True)
        for edge_data in parent_knitgraph_edge_data_list:
            node = edge_data[1]
            node_coor = self.parent_knitgraph.node_to_course_and_wale[node]
            predecessor = edge_data[0]
            predecessor_coor = self.parent_knitgraph.node_to_course_and_wale[predecessor]
            attr_dict = edge_data[2]
            self.parent_knitgraph_coors_connectivity.append([predecessor_coor, node_coor, attr_dict])
        for edge_data in child_knitgraph_edge_data_list:
            node = edge_data[1]
            node_coor = self.child_knitgraph.node_to_course_and_wale[node]
            predecessor = edge_data[0]
            predecessor_coor = self.child_knitgraph.node_to_course_and_wale[predecessor]
            attr_dict = edge_data[2]
            self.child_knitgraph_coors_connectivity.append([predecessor_coor, node_coor, attr_dict])
    
    def get_course_id_to_wale_ids(self):
        #for parent graph (a tube)
        for course_id in [*self.parent_knitgraph.course_to_loop_ids.keys()]:
            loops = self.parent_knitgraph.course_to_loop_ids[course_id]
            self.parent_knitgraph_course_id_to_wale_ids[course_id] = []
            for loop in loops: #we can do this because for a tube, loops in each course is always ordered from small to large
                wale_id = self.parent_knitgraph.node_to_course_and_wale[loop][1]
                self.parent_knitgraph_course_id_to_wale_ids[course_id].append(wale_id)

    def get_course_and_wale_to_bed(self):
        """
        we need this for mapping coor to bed. Nodes will be updated as we rebuild the graph to add strap, as well as node_on_front_or_back.
        """
        for coor in self.parent_knitgraph_course_and_wale_to_node:
            node = self.parent_knitgraph_course_and_wale_to_node[coor]
            bed = self.parent_knitgraph.node_on_front_or_back[node]
            self.parent_knitgraph_course_and_wale_to_bed[coor] = bed

    def get_bed_to_course_id_to_wale_ids(self):
        """
        we need this to grow only one half of the row (i.e., on a particular bed). This function is needed for strap case and 
        pocket/handle on tube case.
        """
        #this function is designed exclusively for parent_knitgraph
        self.parent_knitgraph_bed_to_course_id_to_wale_ids['f'] = {}
        self.parent_knitgraph_bed_to_course_id_to_wale_ids['b'] = {}
        for course_id in [*self.parent_knitgraph.course_to_loop_ids.keys()]:
            loops = self.parent_knitgraph.course_to_loop_ids[course_id]
            for loop in loops: #we can do this because for a tube, loops in each course is always ordered from small to large
                wale_id = self.parent_knitgraph.node_to_course_and_wale[loop][1]
                bed = self.parent_knitgraph.node_on_front_or_back[loop] 
                if course_id not in self.parent_knitgraph_bed_to_course_id_to_wale_ids[bed]:
                    self.parent_knitgraph_bed_to_course_id_to_wale_ids[bed][course_id] = [wale_id]
                else:
                    self.parent_knitgraph_bed_to_course_id_to_wale_ids[bed][course_id].append(wale_id)
        print(f'self.parent_knitgraph_bed_to_course_id_to_wale_ids is {self.parent_knitgraph_bed_to_course_id_to_wale_ids}')

    def build_rows_on_parent_graph_just_above_splitting_course_id(self):
        #here we can clear old self.parent_knitgraph._node_to_course_and_wale since we don't use it anymore hereafter and start 
        #rebuilding the graph needs to have this info updated as well since nodes will change as we rebuild by introducing strap patch.
        self.parent_knitgraph.node_to_course_and_wale = {}
        start_course_id = [*self.parent_knitgraph_course_id_to_wale_ids.keys()][0]
        # note that differ from pocket case, below it is [*self.child_knitgraph.course_to_loop_ids.keys()][0] - 1 not [*self.child_knitgraph.course_to_loop_ids.keys()][0].
        stop_course_id = [*self.child_knitgraph.course_to_loop_ids.keys()][0] - 1
        for course_id in range(start_course_id, stop_course_id + 1):
            for i in range(len(self.parent_knitgraph_course_id_to_wale_ids[course_id])):
                loop_id, loop = self.tube_yarn.add_loop_to_end()
                self.strap_graph.add_loop(loop)
                wale_id = self.parent_knitgraph_course_id_to_wale_ids[course_id][i]
                self.parent_knitgraph.node_to_course_and_wale[loop_id] = (course_id, wale_id)
                self.parent_knitgraph_course_and_wale_to_node[(course_id, wale_id)] = loop_id
                self.strap_graph.node_on_front_or_back[loop_id] = self.parent_knitgraph_course_and_wale_to_bed[(course_id, wale_id)]
       
    def grow_row_on_one_bed_parent_graph(self, bed):
        grow_course_id = [*self.parent_knitgraph_course_id_to_wale_ids.keys()][-1]
        self.parent_knitgraph.course_to_loop_ids[grow_course_id] = []
        for wale_id in self.parent_knitgraph_bed_to_course_id_to_wale_ids[bed][grow_course_id]:
            loop_id, loop = self.tube_yarn.add_loop_to_end()
            self.strap_graph.add_loop(loop)
            self.parent_knitgraph.node_to_course_and_wale[loop_id] = (grow_course_id, wale_id)
            self.parent_knitgraph_course_and_wale_to_node[(grow_course_id, wale_id)] = loop_id
            self.parent_knitgraph.course_to_loop_ids[grow_course_id].append(loop_id)
            self.strap_graph.node_on_front_or_back[loop_id] = 'f' if bed == 'b' else 'b'

    def build_front_straps(self):
        assert len(self.ordered_straps_node_to_course_and_wale)%2==0, f'suspicious number of straps in given strap info'
        half = int(len(self.ordered_straps_node_to_course_and_wale)/2)
        strap_starting_course = [*self.parent_knitgraph_course_id_to_wale_ids.keys()][-1]
        bottom_course_wale_ids = []
        #reinitialize self.child_knitgraph.course_to_loop_ids
        for course_id in range(strap_starting_course, strap_starting_course+self.strap_height):
            self.child_knitgraph.course_to_loop_ids[course_id] = []
        for i in range(half):
            nodes_info = self.ordered_straps_node_to_course_and_wale[i]
            for node in nodes_info:
                course_id = nodes_info[node][0]
                wale_id = nodes_info[node][1]
                loop_id, loop = self.ordered_straps_yarns[i].add_loop_to_end()
                self.strap_graph.add_loop(loop)
                self.strap_graph.node_on_front_or_back[loop_id] = 'f'
                self.child_knitgraph.node_to_course_and_wale[loop_id] = (course_id, wale_id)
                self.child_knitgraph_course_and_wale_to_node[(course_id, wale_id)] = loop_id
                self.child_knitgraph.course_to_loop_ids[course_id].append(loop_id)
                if course_id == strap_starting_course:
                    bottom_course_wale_ids.append(wale_id)
        #connect bottom row of child fabric to splitting row
        # print(f'self.child_knitgraph_course_and_wale_to_node is {self.child_knitgraph_course_and_wale_to_node}')
        for wale_id in bottom_course_wale_ids:
            parent_loop_id = self.parent_knitgraph_course_and_wale_to_node[(strap_starting_course-1, wale_id)] 
            loop_id = self.child_knitgraph_course_and_wale_to_node[(strap_starting_course, wale_id)]
            # print(f'parent_loop_id is {parent_loop_id}, loop_id is {loop_id}')
            self.strap_graph.connect_loops(parent_loop_id, loop_id, pull_direction = Pull_Direction.BtF)    

    def build_back_straps(self):
        half = int(len(self.ordered_straps_node_to_course_and_wale)/2)
        strap_starting_course = [*self.parent_knitgraph_course_id_to_wale_ids.keys()][-1]
        bottom_course_wale_ids = []
        for i in range(half, 2*half):
            nodes_info = self.ordered_straps_node_to_course_and_wale[i]
            for node in nodes_info.keys():
                course_id = nodes_info[node][0]
                wale_id = nodes_info[node][1]
                loop_id, loop = self.ordered_straps_yarns[i].add_loop_to_end()
                self.strap_graph.add_loop(loop)
                self.strap_graph.node_on_front_or_back[loop_id] = 'b'
                self.child_knitgraph.node_to_course_and_wale[loop_id] = (course_id, wale_id)
                self.child_knitgraph_course_and_wale_to_node[(course_id, wale_id)] = loop_id
                self.child_knitgraph.course_to_loop_ids[course_id].append(loop_id)
                if course_id == strap_starting_course:
                    bottom_course_wale_ids.append(wale_id)
        #connect bottom row of child fabric to splitting row
        # print(f'self.child_knitgraph_course_and_wale_to_node is {self.child_knitgraph_course_and_wale_to_node}')
        for wale_id in bottom_course_wale_ids:
            parent_loop_id = self.parent_knitgraph_course_and_wale_to_node[(strap_starting_course-1, wale_id)] 
            loop_id = self.child_knitgraph_course_and_wale_to_node[(strap_starting_course, wale_id)]
            # print(f'parent_loop_id is {parent_loop_id}, loop_id is {loop_id}')
            self.strap_graph.connect_loops(parent_loop_id, loop_id, pull_direction = Pull_Direction.BtF) 

    def connect_stitches_on_knitgraph(self):
        grow_course_id = [*self.parent_knitgraph_course_id_to_wale_ids.keys()][-1]
        for (parent_coor, child_coor, attr_dict) in self.parent_knitgraph_coors_connectivity:
            parent_node = self.parent_knitgraph_course_and_wale_to_node[parent_coor]
            child_node = self.parent_knitgraph_course_and_wale_to_node[child_coor]
            pull_direction = attr_dict['pull_direction']
            if self.parent_knitgraph.node_to_course_and_wale[child_node][0] == grow_course_id:
                pull_direction = Pull_Direction.BtF
                # if self.strap_graph.node_on_front_or_back[child_node] == 'b':
                #     pull_direction = Pull_Direction.FtB
                # else:
                #     pull_direction = Pull_Direction.BtF
            depth = attr_dict['depth']
            parent_offset = attr_dict['parent_offset']
            self.strap_graph.connect_loops(parent_node, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
        for (parent_coor, child_coor, attr_dict) in self.child_knitgraph_coors_connectivity:
            parent_node = self.child_knitgraph_course_and_wale_to_node[parent_coor]
            child_node = self.child_knitgraph_course_and_wale_to_node[child_coor]
            pull_direction = attr_dict['pull_direction']
            depth = attr_dict['depth']
            parent_offset = attr_dict['parent_offset']
            # pull_direction = pull_direction.opposite() since when we view the knitgraph created, we view from the back side of the child fabric.
            self.strap_graph.connect_loops(parent_node, child_node, pull_direction = pull_direction, depth = depth, parent_offset = parent_offset)
    
    def bind_off(self):
        wale_ids = []
        course_id = max([*self.child_knitgraph.course_to_loop_ids.keys()])
        # for loop_id in self.child_knitgraph.course_to_loop_ids[course_id]:
        #     wale_id = self.child_knitgraph.node_to_course_and_wale[loop_id][1]
        #     wale_ids.append(wale_id)
        self.child_knitgraph.course_to_loop_ids[course_id+1] = []
        # organize wale_ids for each pair of strap (a front and back strap makes a pair)
        front_strap_wales = list(self.front_straps_top_course_wale_ids.values())
        back_strap_wales = list(self.back_straps_top_course_wale_ids.values())
        for strap_index in range(len(self.front_straps_top_course_wale_ids)):
            self.straps_top_course_wale_ids[strap_index] = front_strap_wales[strap_index] + back_strap_wales[strap_index]
        print(f'self.straps_top_course_wale_ids is {self.straps_top_course_wale_ids}')
        if self.strap_height%2 == 0:
            # then bind-off starts from right to left
            # first sort the loops based on the wale_ids
            for wale_ids in self.straps_top_course_wale_ids.values():
                loops_to_bind_off = []
                wale_ids = sorted(wale_ids)
                # identify the yarn used to bind off 
                parent_loop = self.child_knitgraph_course_and_wale_to_node[(course_id, wale_ids[0])]
                self.ordered_straps_yarns
                for yarn in self.ordered_straps_yarns:
                    if parent_loop in yarn:
                        bind_off_yarn = yarn
                        break
                for wale_id in wale_ids:
                    parent_loop = self.child_knitgraph_course_and_wale_to_node[(course_id, wale_id)]
                    loop_id, loop = bind_off_yarn.add_loop_to_end()
                    loops_to_bind_off.append(loop_id)
                    bed = self.strap_graph.node_on_front_or_back[parent_loop]
                    self.strap_graph.add_loop(loop)
                    self.strap_graph.node_on_front_or_back[loop_id] = bed
                    self.child_knitgraph.node_to_course_and_wale[loop_id] = (course_id+1, wale_id)
                    self.child_knitgraph_course_and_wale_to_node[(course_id+1, wale_id)] = loop_id
                    self.child_knitgraph.course_to_loop_ids[course_id+1].append(loop_id)
                    grandparent_loop = [*self.strap_graph.graph.predecessors(parent_loop)][0]
                    pull_direction = self.strap_graph.graph[grandparent_loop][parent_loop]['pull_direction']
                    self.strap_graph.connect_loops(parent_loop, loop_id, pull_direction = pull_direction) 
                # connect horizontal stitch to represent bind-off
                for i in range(len(loops_to_bind_off)-1):
                    node = loops_to_bind_off[i]
                    nearest_neighbor = loops_to_bind_off[i+1]
                    print(f'node is {node}, nearest_neighbor is {nearest_neighbor}')
                    parent_wale_id = self.child_knitgraph.node_to_course_and_wale[node][1]
                    child_wale_id = self.child_knitgraph.node_to_course_and_wale[nearest_neighbor][1]
                    pull_direction = Pull_Direction.BtF
                    # pull_direction = Pull_Direction.BtF if self.strap_graph.node_on_front_or_back[nearest_neighbor] == 'f' else Pull_Direction.FtB
                    self.strap_graph.connect_loops(node, nearest_neighbor, pull_direction = pull_direction, parent_offset = parent_wale_id - child_wale_id) 
        else:
            # then bind-off starts from left to right
            for wale_ids in self.straps_top_course_wale_ids.values():
                loops_to_bind_off = []
                wale_ids = sorted(wale_ids, reverse=True)   
                # identify the yarn used to bind off 
                parent_loop = self.child_knitgraph_course_and_wale_to_node[(course_id, wale_ids[0])]
                self.ordered_straps_yarns
                for yarn in self.ordered_straps_yarns:
                    if parent_loop in yarn:
                        bind_off_yarn = yarn
                        break
                for wale_id in wale_ids:
                    parent_loop = self.child_knitgraph_course_and_wale_to_node[(course_id, wale_id)]
                    loop_id, loop = bind_off_yarn.add_loop_to_end()
                    loops_to_bind_off.append(loop_id)
                    bed = self.strap_graph.node_on_front_or_back[parent_loop]
                    self.strap_graph.add_loop(loop)
                    self.strap_graph.node_on_front_or_back[loop_id] = bed
                    self.child_knitgraph.node_to_course_and_wale[loop_id] = (course_id+1, wale_id)
                    self.child_knitgraph_course_and_wale_to_node[(course_id+1, wale_id)] = loop_id
                    self.child_knitgraph.course_to_loop_ids[course_id+1].append(loop_id)
                    grandparent_loop =  [*self.strap_graph.graph.predecessors(parent_loop)][0]
                    pull_direction = self.strap_graph.graph[grandparent_loop][parent_loop]['pull_direction']
                    self.strap_graph.connect_loops(parent_loop, loop_id, pull_direction = pull_direction) 
                # connect horizontal stitch to represent bind-off
                for i in range(len(loops_to_bind_off)-1):
                    node = loops_to_bind_off[i]
                    nearest_neighbor = loops_to_bind_off[i+1]
                    print(f'node is {node}, nearest_neighbor is {nearest_neighbor}')
                    parent_wale_id = self.child_knitgraph.node_to_course_and_wale[node][1]
                    child_wale_id = self.child_knitgraph.node_to_course_and_wale[nearest_neighbor][1]
                    pull_direction = Pull_Direction.BtF
                    # pull_direction = Pull_Direction.BtF if self.strap_graph.node_on_front_or_back[nearest_neighbor] == 'f' else Pull_Direction.FtB
                    self.strap_graph.connect_loops(node, nearest_neighbor, pull_direction = pull_direction, parent_offset = parent_wale_id - child_wale_id) 
        

    def build_strap_graph(self) -> Knit_Graph:  
        self.check_strap_coor_validity() 
        self.order_strap_coor_for_graph_building()
        self.generate_polygon_from_keynodes()
        self.read_connectivity_from_knitgraph()
        self.get_course_id_to_wale_ids()
        #first grow rows just above splitting_course_id on parent fabric
        self.get_course_and_wale_to_bed()
        self.get_bed_to_course_id_to_wale_ids()
        self.build_rows_on_parent_graph_just_above_splitting_course_id()
        self.child_knitgraph.node_to_course_and_wale = {}
        #grow the whole graph by adding one row to parent fabric, then adding one row to child fabric, until reaching the end of child fabric
        self.grow_row_on_one_bed_parent_graph(bed = 'f')
        self.build_front_straps()
        self.grow_row_on_one_bed_parent_graph(bed = 'b')
        self.build_back_straps()
        #merge node_to_course_and_wale on parent_knitgraph and child_knitgraph
        self.connect_stitches_on_knitgraph()
        self.bind_off()
        self.strap_graph.node_to_course_and_wale = self.parent_knitgraph.node_to_course_and_wale|self.child_knitgraph.node_to_course_and_wale
        # KnitGraph_Visualizer = knitGraph_visualizer(knit_graph = self.strap_graph, object_type = 'strap')
        # KnitGraph_Visualizer.visualize()
        return self.strap_graph
  