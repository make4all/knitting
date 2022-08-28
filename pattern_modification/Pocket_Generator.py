from ipaddress import summarize_address_range
from turtle import left
from typing import Optional, List, Dict, Tuple
import xxlimited
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
import warnings

class Pocket_Generator:
    def __init__(self, left_keynodes_parent_fabric, right_keynodes_parent_fabric, left_keynodes_child_fabric, right_keynodes_child_fabric, split_starting_course_id, spliting_nodes):
        """
        :param left_keypoints: List of (course_id, wale_id) of the spiky points on the left side of the pattern.
        :param right_keypoints: List of (course_id, wale_id) of the spiky points on the right side of the pattern.
        (Note that the keypoints should be enter in order of from bottom to top for each side, and we assume the origin
        of the pattern is (0, 0). )
        """

        self.left_keynodes_child_fabric: List[Tuple[int, int]] = left_keynodes_child_fabric
        self.right_keynodes_child_fabric: List[Tuple[int, int]] = right_keynodes_child_fabric
        self.left_keynodes_parent_fabric: List[Tuple[int, int]] = left_keynodes_parent_fabric
        self.right_keynodes_parent_fabric: List[Tuple[int, int]] = right_keynodes_parent_fabric
        # self.first_course_left_wale_id: int 
        # self.first_course_right_wale_id: int
        self.child_fabric_starting_width: int 
        self.parent_fabric_starting_width: int 
        self.shaping_trend: Dict[str, Dict[Tuple(int, int), str]] = {}
        self.course_id_to_width: Dict[str, Dict[int, int]] = {}
        self.course_id_to_shaping: Dict[str, Dict[int, str]] = {}
        self._knit_graph: Knit_Graph = Knit_Graph()
        self.old_yarn: Yarn
        self.new_yarn: Yarn
        self._loop_id_to_course: Dict[int, float] 
        self._loop_id_to_wale: Dict[int, float] 
        self._course_to_loop_ids: Dict[float, List[int]]
        self._wale_to_loop_ids: Dict[float, List[int]]
        self._course_to_loop_ids_on_yarn: Dict[str, Dict[float, List[int]]] = {}

        self.spliting_nodes: List[int] = spliting_nodes
        self.spliting_width: int = len(self.spliting_nodes)
        self.split_starting_course_id: int = split_starting_course_id

        self.cur_width_parent_fabric: int
        self.prior_width_parent_fabric: int
        self.prior_row_parent_fabric: List[int]

        self.cur_width_child_fabric: int
        self.prior_width_child_fabric: int
        self.prior_row_parent_fabric: List[int]


    def check_keynodes_validity(self, is_parent_fabric: bool): #todo: allow non-symmetry
        """
        currently, symmetry is required for the shape
        """
        if is_parent_fabric == True:
            left_keynodes = self.left_keynodes_parent_fabric
            right_keynodes = self.right_keynodes_parent_fabric
            assert left_keynodes[0][0] == 0, f'course_id does not start from 0'
        elif is_parent_fabric == False:
            left_keynodes = self.left_keynodes_child_fabric
            right_keynodes = self.right_keynodes_child_fabric
        assert len(left_keynodes) == len(right_keynodes), f'num of left keynodes is not equal to num of right keynodes on parent fabric {is_parent_fabric}'
        num_of_nodes_each_side = len(left_keynodes) 
        # print('num_of_nodes_each_side', num_of_nodes_each_side)

        for i in range(1, num_of_nodes_each_side):
            curr_right_keynode = right_keynodes[i]
            last_right_keynode = right_keynodes[i-1]
            curr_left_keynode = left_keynodes[i]
            last_left_keynode = left_keynodes[i-1]
            #assume that if width is increased, then the width change should be equal to height increase. Otherwise, path 
            # along the edge can not be determined with more than one possible options.
            width_change_left = curr_left_keynode[1] - last_left_keynode[1]
            width_change_right = curr_right_keynode[1] - last_right_keynode[1]
            increase_height = curr_right_keynode[0] - last_right_keynode[0]
            if width_change_right != 0 or width_change_right != 0:
                assert -width_change_left == width_change_right and abs(width_change_right) == increase_height, f'width_change_left is {width_change_left}, while width_change_right is {width_change_right}, and increase_height is {increase_height}'
            else:
                assert width_change_right == width_change_right == 0, f'width change: {width_change_left} on the left side is not equal to width change: {width_change_right} on the right side'

    def generate_polygon_from_keynodes(self, old_carrier):
        # first process given keynodes on each side, to get starting node coordinate and ending node coordinate on each course.
        starting_nodes_coor = []
        ending_nodes_coor = []
        num_of_nodes_left_side = len(self.left_keynodes_child_fabric) 
        num_of_nodes_right_side = len(self.right_keynodes_child_fabric) 
        # for keynodes on the left side
        starting_nodes_coor_on_first_course = ((self.left_keynodes_child_fabric[0][0], self.left_keynodes_child_fabric[0][1]))
        starting_nodes_coor.append(starting_nodes_coor_on_first_course)
        for i in range(1, num_of_nodes_left_side):
            curr_left_keynode = self.left_keynodes_child_fabric[i]
            last_left_keynode = self.left_keynodes_child_fabric[i-1]
            # if 
            if curr_left_keynode[1] - last_left_keynode[1] == 0:
                #wale_id keeps the same between this course range
                wale_id = last_left_keynode[1]
                for course_id in range(last_left_keynode[0] + 1, curr_left_keynode[0] + 1):
                    starting_nodes_coor.append((course_id, wale_id))
            elif curr_left_keynode[1] - last_left_keynode[1] != 0:
                wale_id = last_left_keynode[1]
                wale_change_per_course = int((curr_left_keynode[1] - last_left_keynode[1]) / (curr_left_keynode[0] - last_left_keynode[0]))
                for course_id in range(last_left_keynode[0] + 1, curr_left_keynode[0] + 1):
                    wale_id += wale_change_per_course
                    starting_nodes_coor.append((course_id, wale_id))
        # for keynodes on the right side
        ending_nodes_coor_on_first_course = ((self.right_keynodes_child_fabric[0][0], self.right_keynodes_child_fabric[0][1]))
        ending_nodes_coor.append(ending_nodes_coor_on_first_course)
        for i in range(1, num_of_nodes_right_side):
            curr_right_keynode = self.right_keynodes_child_fabric[i]
            last_right_keynode = self.right_keynodes_child_fabric[i-1]
            # if 
            if curr_right_keynode[1] - last_right_keynode[1] == 0:
                #wale_id keeps the same between this course range
                wale_id = last_right_keynode[1]
                for course_id in range(last_right_keynode[0] + 1, curr_right_keynode[0] + 1):
                    ending_nodes_coor.append((course_id, wale_id))
            elif curr_right_keynode[1] - last_right_keynode[1] != 0:
                wale_id = last_right_keynode[1]
                wale_change_per_course = int((curr_right_keynode[1] - last_right_keynode[1]) / (curr_right_keynode[0] - last_right_keynode[0]))
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

        #connect nodes on yarn
        self.old_yarn = Yarn("old_yarn", self._knit_graph, carrier_id=old_carrier)
        self._knit_graph.add_yarn(self.old_yarn)
        for node in node_to_course_and_wale.keys():
            loop_id, loop = self.old_yarn.add_loop_to_end()
            self._knit_graph.add_loop(loop)
        #get course_to_loop_ids
        course_to_loop_ids = {}
        for course_id in range(starting_nodes_coor_on_first_course[0], starting_nodes_coor[-1][0]+1):
            course_to_loop_ids[course_id] = []
        for node in self._knit_graph.graph.nodes:
            course_id = node_to_course_and_wale[node][0]
            course_to_loop_ids[course_id].append(node)
        #reverse node_to_course_and_wale to get course_and_wale_to_node
        course_and_wale_to_node = {}
        course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
        #connect node stitches
        print(f'course_to_loop_ids is {course_to_loop_ids}')
        for course_id in [*course_to_loop_ids.keys()][:-1]:
            for node in course_to_loop_ids[course_id]:
                wale_id = node_to_course_and_wale[node][1]
                #find upper neighbor node
                if (course_id + 1, wale_id) in course_and_wale_to_node.keys():
                    child_loop = course_and_wale_to_node[(course_id + 1, wale_id)]
                    self._knit_graph.connect_loops(node, child_loop)
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = node_to_course_and_wale, object_type = 'sheet', unmodified = False)
        
    def extract_shaping_trend(self, is_parent_fabric: bool) -> List[str]:
        """
        return a list recording shaping trend of the pattern.
        shaping trend includes 'wider', 'narrower', 'unchanged'.
        """
        if is_parent_fabric == True:
            self.shaping_trend['parent_fabric'] = {}
            num_of_nodes_each_side = len(self.left_keynodes_parent_fabric) 
            for i in range(1, num_of_nodes_each_side):
                curr_right_keynode = self.right_keynodes_parent_fabric[i]
                last_right_keynode = self.right_keynodes_parent_fabric[i-1]
                #if wale_id is increasing, then it is defined as 'wider'.
                if curr_right_keynode[1] - last_right_keynode[1] > 0:
                    self.shaping_trend['parent_fabric'][(last_right_keynode[0], curr_right_keynode[0])] = 'wider' 

                elif curr_right_keynode[1] - last_right_keynode[1] < 0:
                    self.shaping_trend['parent_fabric'][(last_right_keynode[0], curr_right_keynode[0])] = 'narrower'
                
                else:
                    self.shaping_trend['parent_fabric'][(last_right_keynode[0], curr_right_keynode[0])] = 'unchanged'
            print('self.shaping_trend[parent_fabric] is:', self.shaping_trend['parent_fabric'])

        elif is_parent_fabric == False:
            self.shaping_trend['child_fabric'] = {}
            num_of_nodes_each_side = len(self.left_keynodes_child_fabric) 
            for i in range(1, num_of_nodes_each_side):
                curr_right_keynode = self.right_keynodes_child_fabric[i]
                last_right_keynode = self.right_keynodes_child_fabric[i-1]
                #if wale_id is increasing, then it is defined as 'wider'.
                if curr_right_keynode[1] - last_right_keynode[1] > 0:
                    self.shaping_trend['child_fabric'][(last_right_keynode[0], curr_right_keynode[0])] = 'wider' 

                elif curr_right_keynode[1] - last_right_keynode[1] < 0:
                    self.shaping_trend['child_fabric'][(last_right_keynode[0], curr_right_keynode[0])] = 'narrower'
                
                else:
                    self.shaping_trend['child_fabric'][(last_right_keynode[0], curr_right_keynode[0])] = 'unchanged'
            print('self.shaping_trend[child_fabric] is:', self.shaping_trend['child_fabric'])
    
    #extract shaping for parent fabric before splitting course_id + 1 to build the graph first
    def shaping_before_course_id(self):
        shaping_trend_before_splitting = {}
        last_course_id = 0
        for course_range in self.shaping_trend['parent_fabric'].keys():
            if (self.split_starting_course_id + 1) in range(course_range[0], course_range[1]):
                # print('haha', (last_course_id, self.split_starting_course_id + 1))
                shaping_trend_before_splitting[(last_course_id, self.split_starting_course_id + 1)] = self.shaping_trend['parent_fabric'][course_range]
                break
            else:
                shaping_trend_before_splitting[course_range] = self.shaping_trend['parent_fabric'][course_range]
                last_course_id = course_range[1]
        print('shaping_trend_before_splitting is:', shaping_trend_before_splitting)
        return shaping_trend_before_splitting

    def get_course_id_to_shaping(self, is_parent_fabric: bool):
        if is_parent_fabric == True:
            shaping_trend = self.shaping_trend['parent_fabric']
            self.course_id_to_shaping['parent_fabric'] = {}
            for course_range in shaping_trend.keys():
                shaping = shaping_trend[course_range]
                if shaping == 'wider':
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        self.course_id_to_shaping['parent_fabric'][course_id] = 'wider'
                elif shaping == 'unchanged':  
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        self.course_id_to_shaping['parent_fabric'][course_id] = 'unchanged'
                elif shaping == 'narrower':
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        self.course_id_to_shaping['parent_fabric'][course_id] = 'narrower'
            print('self.course_id_to_shaping[parent_fabric] is', self.course_id_to_shaping['parent_fabric'])
                
        elif is_parent_fabric == False:
            shaping_trend = self.shaping_trend['child_fabric']
            self.course_id_to_shaping['child_fabric'] = {}
            for course_range in shaping_trend.keys():
                shaping = shaping_trend[course_range]
                if shaping == 'wider':
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        self.course_id_to_shaping['child_fabric'][course_id] = 'wider'
                elif shaping == 'unchanged':  
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        self.course_id_to_shaping['child_fabric'][course_id] = 'unchanged'
                elif shaping == 'narrower':
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        self.course_id_to_shaping['child_fabric'][course_id] = 'narrower'
            print('self.course_id_to_shaping[child_fabric] is', self.course_id_to_shaping['child_fabric'])
        return self.course_id_to_shaping

    def generate_pocket_graph(self, old_carrier: int = 3, new_carrier: int = 4, close_top: bool = False, smaller_wale_edge_connected: bool = False, bigger_wale_edge_connected: bool = False) -> Knit_Graph:
        self.check_keynodes_validity(is_parent_fabric = False)
        self.check_keynodes_validity(is_parent_fabric = True)
        self.extract_shaping_trend(is_parent_fabric = False)
        self.extract_shaping_trend(is_parent_fabric = True)
        #extract shaping info for parent fabric before splitting course_id + 1 to build the graph first
        shaping_trend_before_splitting = self.shaping_before_course_id()
        self.old_yarn = Yarn("old_yarn", self._knit_graph, carrier_id=old_carrier)
        self._knit_graph.add_yarn(self.old_yarn)
        #for parent fabric, add rows for old yarns until reaching the row just above the splitting row
        first_row_parent_fabric = []
        parent_fabric_first_course_left_wale_id: int = self.left_keynodes_parent_fabric[0][1]
        parent_fabric_first_course_right_wale_id: int = self.right_keynodes_parent_fabric[0][1]
        self.parent_fabric_starting_width = parent_fabric_first_course_right_wale_id - parent_fabric_first_course_left_wale_id + 1
        #build first row 
        for _ in range(0, self.parent_fabric_starting_width):
            loop_id, loop = self.old_yarn.add_loop_to_end()
            first_row_parent_fabric.append(loop_id)
            self._knit_graph.add_loop(loop)
        self.prior_row_parent_fabric = first_row_parent_fabric
        self.prior_width_parent_fabric = self.parent_fabric_starting_width
        #continue to build rows until reaching the row just above the splitting row
        knitgraph = self.build_rows(shaping_trend = shaping_trend_before_splitting, is_parent_fabric = True)
        # visualize_knitGraph(knitgraph, unmodified = True)
        #for child fabric
        first_row_child_fabric = []
        child_fabric_first_course_left_wale_id: int = self.left_keynodes_child_fabric[0][1]
        child_fabric_first_course_right_wale_id: int = self.right_keynodes_child_fabric[0][1]
        self.child_fabric_starting_width = child_fabric_first_course_right_wale_id - child_fabric_first_course_left_wale_id + 1
        #bring in new yarn
        self.new_yarn = Yarn("new_yarn", self._knit_graph, carrier_id=new_carrier)
        self._knit_graph.add_yarn(self.new_yarn)
        #add loops for first row on new yarn
        for _ in range(0, self.child_fabric_starting_width):
            loop_id, loop = self.new_yarn.add_loop_to_end()
            first_row_child_fabric.append(loop_id)
            self._knit_graph.add_loop(loop)
        self.prior_row_child_fabric = first_row_child_fabric
        self.prior_width_child_fabric = self.child_fabric_starting_width
        #connect first row in the child_fabric to the spliting nodes in the parent_fabric
        #assume first row in the child_fabric start from left to right, too, same as the order of nodes listed in "spliting_nodes"
        self.spliting_width = self.child_fabric_starting_width
        for i in range(self.spliting_width):
            parent_loop_id = self.spliting_nodes[i]
            loop_id = self.prior_row_child_fabric[i]
            self._knit_graph.connect_loops(parent_loop_id, loop_id)
        #each time we grow old yarn, we grow new yarn as well
        generator.get_course_id_to_shaping(is_parent_fabric = True)
        generator.get_course_id_to_shaping(is_parent_fabric = False)
        for course_id in self.course_id_to_shaping['child_fabric'].keys():
            self.grow_one_row(course_id, is_parent_fabric = True)
            self.grow_one_row(course_id, is_parent_fabric = False)
            #child fabric width constraint
            assert self.cur_width_parent_fabric - self.cur_width_child_fabric >= 2, f'width of child fabric should be at least \
                two nodes larger than parent fabric, while cur_width_parent_fabric is {self.cur_width_parent_fabric} and \
                    cur_width_child_fabric is {self.cur_width_child_fabric}'  
        #build remaining rows on old yarn if any
        last_course_id_child_fabric = [*self.course_id_to_shaping['child_fabric'].keys()][-1]
        last_course_id_parent_fabric = [*self.course_id_to_shaping['parent_fabric'].keys()][-1]
        for course_id in range(last_course_id_child_fabric + 1, last_course_id_parent_fabric + 1):
            self.grow_one_row(course_id, is_parent_fabric = True)
        # visualize_knitGraph(self._knit_graph,  object_type = 'pocket', unmodified = True)  

        #connect nodes to close the top opening of the pocket
        self._loop_id_to_course, self._course_to_loop_ids, self._loop_id_to_wale, self._wale_to_loop_ids = self._knit_graph.get_courses(unmodified = True)
        node_to_course_and_wale, course_and_wale_to_node = self.get_nodes_course_and_wale()
        if close_top == True:
            for node in self.prior_row_child_fabric:
                course_and_wale = node_to_course_and_wale[node]
                print(f'node to connect on child fabric is {node}')
                for key, value in node_to_course_and_wale.items():
                    if course_and_wale == value and key != node:
                        print(f'node to connect on parent fabric is {key}')
                        self._knit_graph.connect_loops(node, key)
        #remove incorrect stitch edges
        node_to_course_and_wale_on_yarn, course_and_wale_to_node_on_yarn, course_to_loop_ids_on_yarn = self.get_yarn_graph_nodes_course_and_wale(node_to_course_and_wale)
        self.remove_stitches_to_make_graph_correct(course_to_loop_ids_on_yarn)
        #
        smaller_wale_edge_nodes, bigger_wale_edge_nodes = self.get_edge_nodes_on_child_fabric(course_to_loop_ids_on_yarn)
        #
        smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes = self.get_target_edge_nodes_on_parent_fabric(bigger_wale_edge_nodes, smaller_wale_edge_nodes, node_to_course_and_wale, course_and_wale_to_node_on_yarn)
        #
        #connect edge nodes: need to use wale and course id info of node
        self.actions_around_target_edge_node(smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes, node_to_course_and_wale, course_and_wale_to_node_on_yarn, smaller_wale_edge_connected, bigger_wale_edge_connected)
        # visualize_knitGraph(self._knit_graph, node_to_course_and_wale = node_to_course_and_wale, object_type = 'pocket', unmodified = False)    
    
    def grow_one_row(self, course_id, is_parent_fabric: bool):
        """
        given course_id, grow a row with specific yarn on specific knitgraph
        """
        if is_parent_fabric == True:
            yarn = self.old_yarn
            shaping = self.course_id_to_shaping['parent_fabric'][course_id]
            if shaping == 'wider':
                self.cur_width_parent_fabric = self.prior_width_parent_fabric + 2
                next_row = []
                i = 0
                if course_id % 2 == 1:
                    for _ in range(self.cur_width_parent_fabric):
                        loop_id, loop = yarn.add_loop_to_end()
                        next_row.append(loop_id)
                        self._knit_graph.add_loop(loop)
                        if _ == 0:
                            parent_loop_id = self.prior_row_parent_fabric[-1]
                            parent_offset = -1 
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        elif _ == self.cur_width_parent_fabric - 1:
                            parent_loop_id = self.prior_row_parent_fabric[0]
                            parent_offset = 1
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        else:
                            parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                            self._knit_graph.connect_loops(parent_loop_id, loop_id)
                            i += 1
                elif course_id % 2 == 0:
                    for _ in range(self.cur_width_parent_fabric):
                        loop_id, loop = yarn.add_loop_to_end()
                        next_row.append(loop_id)
                        self._knit_graph.add_loop(loop)
                        if _ == 0:
                            parent_loop_id = self.prior_row_parent_fabric[-1]
                            parent_offset = 1 
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        elif _ == self.cur_width_parent_fabric - 1:
                            parent_loop_id = self.prior_row_parent_fabric[0]
                            parent_offset = -1
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        else:
                            parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                            self._knit_graph.connect_loops(parent_loop_id, loop_id)
                            i += 1
                assert i == self.prior_width_parent_fabric, f'loops in prior row has not been fully consumed' 
                self.prior_row_parent_fabric = next_row
                self.prior_width_parent_fabric = self.cur_width_parent_fabric
                #everytime we build a new course on new knitgraph with new yarn, 
                #we should build a new course on the old knitgraph with old yarn, so that the info like course_to_loop_ids 
                #returned by knitgraph.get_course() will be correct.
                    
            elif shaping == 'unchanged':  
                self.cur_width_parent_fabric = self.prior_width_parent_fabric 
                next_row = []
                for parent_loop_id in [*reversed(self.prior_row_parent_fabric)]:
                    loop_id, loop = yarn.add_loop_to_end()
                    next_row.append(loop_id)
                    self._knit_graph.add_loop(loop)
                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                self.prior_row_parent_fabric = next_row
                self.prior_width_parent_fabric = self.cur_width_parent_fabric
                
            elif shaping == 'narrower':
                self.cur_width_parent_fabric = self.prior_width_parent_fabric - 2
                next_row = []
                i = 2
                # when course_id % 2 == 1, the yarn walking direction is opposite to the yarn starting direction
                if course_id % 2 == 1:
                    for _ in range(self.cur_width_parent_fabric):
                        if self.cur_width_parent_fabric == 1:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            #
                            parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                            parent_offset = 1 
                            self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_2 = self.prior_row_parent_fabric[0]
                            parent_offset = -1 
                            self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_3 = self.prior_row_parent_fabric[1]
                            self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                        else:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            if _ == 0:
                                parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                                parent_offset = 1 
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_parent_fabric[-2]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            elif _ == self.cur_width_parent_fabric - 1:
                                parent_loop_id_1 = self.prior_row_parent_fabric[0]
                                parent_offset = -1
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_parent_fabric[1]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            else:
                                parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                                self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                i += 1  
                # when course_id % 2 == 0, the yarn walking direction is the same as the yarn starting direction
                elif course_id % 2 == 0:
                    for _ in range(self.cur_width_parent_fabric):
                        if self.cur_width_parent_fabric == 1:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            #
                            parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                            parent_offset = -1 
                            self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_2 = self.prior_row_parent_fabric[0]
                            parent_offset = 1 
                            self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_3 = self.prior_row_parent_fabric[1]
                            self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                        else:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            if _ == 0:
                                parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                                parent_offset = -1 
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_parent_fabric[-2]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            elif _ == self.cur_width_parent_fabric - 1:
                                parent_loop_id_1 = self.prior_row_parent_fabric[0]
                                parent_offset = 1
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_parent_fabric[1]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            else:
                                parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                                self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                i += 1
                # assert i == prior_width - 2, f'loops in prior row has not been fully consumed' 
                self.prior_row_parent_fabric = next_row
                self.prior_width_parent_fabric = self.cur_width_parent_fabric

        elif is_parent_fabric == False:
            yarn = self.new_yarn
            shaping = self.course_id_to_shaping['child_fabric'][course_id]
            if shaping == 'wider':
                self.cur_width_child_fabric = self.prior_width_child_fabric + 2
                next_row = []
                i = 0
                if course_id % 2 == 1:
                    for _ in range(self.cur_width_child_fabric):
                        loop_id, loop = yarn.add_loop_to_end()
                        next_row.append(loop_id)
                        self._knit_graph.add_loop(loop)
                        if _ == 0:
                            parent_loop_id = self.prior_row_child_fabric[-1]
                            parent_offset = -1 
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        elif _ == self.cur_width_child_fabric - 1:
                            parent_loop_id = self.prior_row_child_fabric[0]
                            parent_offset = 1
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        else:
                            parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                            self._knit_graph.connect_loops(parent_loop_id, loop_id)
                            i += 1
                elif course_id % 2 == 0:
                    for _ in range(self.cur_width_child_fabric):
                        loop_id, loop = yarn.add_loop_to_end()
                        next_row.append(loop_id)
                        self._knit_graph.add_loop(loop)
                        if _ == 0:
                            parent_loop_id = self.prior_row_child_fabric[-1]
                            parent_offset = 1 
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        elif _ == self.cur_width_child_fabric - 1:
                            parent_loop_id = self.prior_row_child_fabric[0]
                            parent_offset = -1
                            self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                        else:
                            parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                            self._knit_graph.connect_loops(parent_loop_id, loop_id)
                            i += 1
                assert i == self.prior_width_child_fabric, f'loops in prior row has not been fully consumed' 
                self.prior_row_child_fabric = next_row
                self.prior_width_child_fabric = self.cur_width_child_fabric
                #everytime we build a new course on new knitgraph with new yarn, 
                #we should build a new course on the old knitgraph with old yarn, so that the info like course_to_loop_ids 
                #returned by knitgraph.get_course() will be correct.
                    
            elif shaping == 'unchanged':  
                self.cur_width_child_fabric = self.prior_width_child_fabric 
                next_row = []
                for parent_loop_id in [*reversed(self.prior_row_child_fabric)]:
                    loop_id, loop = yarn.add_loop_to_end()
                    next_row.append(loop_id)
                    self._knit_graph.add_loop(loop)
                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                self.prior_row_child_fabric = next_row
                self.prior_width_child_fabric = self.cur_width_child_fabric
                
            elif shaping == 'narrower':
                self.cur_width_child_fabric = self.prior_width_child_fabric - 2
                next_row = []
                i = 2
                # when course_id % 2 == 1, the yarn walking direction is opposite to the yarn starting direction
                if course_id % 2 == 1:
                    for _ in range(self.cur_width_child_fabric):
                        if self.cur_width_child_fabric == 1:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            #
                            parent_loop_id_1 = self.prior_row_child_fabric[-1]
                            parent_offset = 1 
                            self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_2 = self.prior_row_child_fabric[0]
                            parent_offset = -1 
                            self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_3 = self.prior_row_child_fabric[1]
                            self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                        else:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            if _ == 0:
                                parent_loop_id_1 = self.prior_row_child_fabric[-1]
                                parent_offset = 1 
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_child_fabric[-2]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            elif _ == self.cur_width_child_fabric - 1:
                                parent_loop_id_1 = self.prior_row_child_fabric[0]
                                parent_offset = -1
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_child_fabric[1]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            else:
                                parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                                self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                i += 1  
                # when course_id % 2 == 0, the yarn walking direction is the same as the yarn starting direction
                elif course_id % 2 == 0:
                    for _ in range(self.cur_width_child_fabric):
                        if self.cur_width_child_fabric == 1:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            #
                            parent_loop_id_1 = self.prior_row_child_fabric[-1]
                            parent_offset = -1 
                            self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_2 = self.prior_row_child_fabric[0]
                            parent_offset = 1 
                            self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            #
                            parent_loop_id_3 = self.prior_row_child_fabric[1]
                            self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                        else:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            if _ == 0:
                                parent_loop_id_1 = self.prior_row_child_fabric[-1]
                                parent_offset = -1 
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_child_fabric[-2]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            elif _ == self.cur_width_child_fabric - 1:
                                parent_loop_id_1 = self.prior_row_child_fabric[0]
                                parent_offset = 1
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                parent_loop_id_2 = self.prior_row_child_fabric[1]
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                            else:
                                parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                                self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                i += 1
                # assert i == prior_width - 2, f'loops in prior row has not been fully consumed' 
                self.prior_row_child_fabric = next_row
                self.prior_width_child_fabric = self.cur_width_child_fabric

    def build_rows(self, shaping_trend, is_parent_fabric: bool):
        if is_parent_fabric == True:
            yarn = self.old_yarn
            for course_range in shaping_trend.keys():
                shaping = shaping_trend[course_range]
                if shaping == 'wider':
                    self.cur_width_parent_fabric = self.prior_width_parent_fabric + 2
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        next_row = []
                        i = 0
                        if course_id % 2 == 1:
                            for _ in range(self.cur_width_parent_fabric):
                                loop_id, loop = yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                if _ == 0:
                                    parent_loop_id = self.prior_row_parent_fabric[-1]
                                    parent_offset = -1 
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                elif _ == self.cur_width_parent_fabric - 1:
                                    parent_loop_id = self.prior_row_parent_fabric[0]
                                    parent_offset = 1
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                else:
                                    parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                    i += 1
                        elif course_id % 2 == 0:
                            for _ in range(self.cur_width_parent_fabric):
                                loop_id, loop = yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                if _ == 0:
                                    parent_loop_id = self.prior_row_parent_fabric[-1]
                                    parent_offset = 1 
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                elif _ == self.cur_width_parent_fabric - 1:
                                    parent_loop_id = self.prior_row_parent_fabric[0]
                                    parent_offset = -1
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                else:
                                    parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                    i += 1
                        assert i == self.prior_width_parent_fabric, f'loops in prior row has not been fully consumed' 
                        self.prior_row_parent_fabric = next_row
                        self.prior_width_parent_fabric = self.cur_width_parent_fabric
                        self.cur_width_parent_fabric = self.prior_width_parent_fabric + 2
                        #everytime we build a new course on new knitgraph with new yarn, 
                        #we should build a new course on the old knitgraph with old yarn, so that the info like course_to_loop_ids 
                        #returned by knitgraph.get_course() will be correct.
                    
                elif shaping == 'unchanged':  
                    self.cur_width_parent_fabric = self.prior_width_parent_fabric 
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        next_row = []
                        for parent_loop_id in [*reversed(self.prior_row_parent_fabric)]:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            self._knit_graph.connect_loops(parent_loop_id, loop_id)
                        self.prior_row_parent_fabric = next_row
                        self.prior_width_parent_fabric = self.cur_width_parent_fabric
                        

                elif shaping == 'narrower':
                    self.cur_width_parent_fabric = self.prior_width_parent_fabric - 2
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        next_row = []
                        i = 2
                        # when course_id % 2 == 1, the yarn walking direction is opposite to the yarn starting direction
                        if course_id % 2 == 1:
                            for _ in range(self.cur_width_parent_fabric):
                                if self.cur_width_parent_fabric == 1:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    #
                                    parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                                    parent_offset = 1 
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_2 = self.prior_row_parent_fabric[0]
                                    parent_offset = -1 
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_3 = self.prior_row_parent_fabric[1]
                                    self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                                else:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    if _ == 0:
                                        parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                                        parent_offset = 1 
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_parent_fabric[-2]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    elif _ == self.cur_width_parent_fabric - 1:
                                        parent_loop_id_1 = self.prior_row_parent_fabric[0]
                                        parent_offset = -1
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_parent_fabric[1]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    else:
                                        parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                                        self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                        i += 1  
                        # when course_id % 2 == 0, the yarn walking direction is the same as the yarn starting direction
                        elif course_id % 2 == 0:
                            for _ in range(self.cur_width_parent_fabric):
                                if self.cur_width_parent_fabric == 1:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    #
                                    parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                                    parent_offset = -1 
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_2 = self.prior_row_parent_fabric[0]
                                    parent_offset = 1 
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_3 = self.prior_row_parent_fabric[1]
                                    self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                                else:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    if _ == 0:
                                        parent_loop_id_1 = self.prior_row_parent_fabric[-1]
                                        parent_offset = -1 
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_parent_fabric[-2]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    elif _ == self.cur_width_parent_fabric - 1:
                                        parent_loop_id_1 = self.prior_row_parent_fabric[0]
                                        parent_offset = 1
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_parent_fabric[1]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    else:
                                        parent_loop_id = [*reversed(self.prior_row_parent_fabric)][i]
                                        self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                        i += 1
                        # assert i == prior_width - 2, f'loops in prior row has not been fully consumed' 
                        self.prior_row_parent_fabric = next_row
                        self.prior_width_parent_fabric = self.cur_width_parent_fabric
                        self.cur_width_parent_fabric = self.prior_width_parent_fabric - 2

        elif is_parent_fabric == False:
            yarn = self.new_yarn
            for course_range in shaping_trend.keys():
                shaping = shaping_trend[course_range]
                if shaping == 'wider':
                    self.cur_width_child_fabric = self.prior_width_child_fabric + 2
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        next_row = []
                        i = 0
                        if course_id % 2 == 1:
                            for _ in range(self.cur_width_child_fabric):
                                loop_id, loop = yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                if _ == 0:
                                    parent_loop_id = self.prior_row_child_fabric[-1]
                                    parent_offset = -1 
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                elif _ == self.cur_width_child_fabric - 1:
                                    parent_loop_id = self.prior_row_child_fabric[0]
                                    parent_offset = 1
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                else:
                                    parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                    i += 1
                        elif course_id % 2 == 0:
                            for _ in range(self.cur_width_child_fabric):
                                loop_id, loop = yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                if _ == 0:
                                    parent_loop_id = self.prior_row_child_fabric[-1]
                                    parent_offset = 1 
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                elif _ == self.cur_width_child_fabric - 1:
                                    parent_loop_id = self.prior_row_child_fabric[0]
                                    parent_offset = -1
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                                else:
                                    parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                    i += 1
                        assert i == self.prior_width_child_fabric, f'loops in prior row has not been fully consumed' 
                        self.prior_row_child_fabric = next_row
                        self.prior_width_child_fabric = self.cur_width_child_fabric
                        self.cur_width_child_fabric =self.prior_width_child_fabric + 2
                        #everytime we build a new course on new knitgraph with new yarn, 
                        #we should build a new course on the old knitgraph with old yarn, so that the info like course_to_loop_ids 
                        #returned by knitgraph.get_course() will be correct.
                    
                elif shaping == 'unchanged':  
                    self.cur_width_child_fabric = self.prior_width_child_fabric
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        next_row = []
                        for parent_loop_id in [*reversed(self.prior_row_child_fabric)]:
                            loop_id, loop = yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            self._knit_graph.connect_loops(parent_loop_id, loop_id)
                        self.prior_row_child_fabric = next_row
                        self.prior_width_child_fabric = self.cur_width_child_fabric

                elif shaping == 'narrower':
                    self.cur_width_child_fabric = self.prior_width_child_fabric - 2
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        next_row = []
                        i = 2
                        # when course_id % 2 == 1, the yarn walking direction is opposite to the yarn starting direction
                        if course_id % 2 == 1:
                            for _ in range(self.cur_width_child_fabric):
                                if self.cur_width_child_fabric == 1:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    #
                                    parent_loop_id_1 = self.prior_row_child_fabric[-1]
                                    parent_offset = 1 
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_2 = self.prior_row_child_fabric[0]
                                    parent_offset = -1 
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_3 = self.prior_row_child_fabric[1]
                                    self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                                else:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    if _ == 0:
                                        parent_loop_id_1 = self.prior_row_child_fabric[-1]
                                        parent_offset = 1 
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_child_fabric[-2]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    elif _ == self.cur_width_child_fabric - 1:
                                        parent_loop_id_1 = self.prior_row_child_fabric[0]
                                        parent_offset = -1
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_child_fabric[1]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    else:
                                        parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                                        self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                        i += 1  
                        # when course_id % 2 == 0, the yarn walking direction is the same as the yarn starting direction
                        elif course_id % 2 == 0:
                            for _ in range(self.cur_width_child_fabric):
                                if self.cur_width_child_fabric == 1:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    #
                                    parent_loop_id_1 = self.prior_row_child_fabric[-1]
                                    parent_offset = -1 
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_2 = self.prior_row_child_fabric[0]
                                    parent_offset = 1 
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    #
                                    parent_loop_id_3 = self.prior_row_child_fabric[1]
                                    self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                                else:
                                    loop_id, loop = yarn.add_loop_to_end()
                                    next_row.append(loop_id)
                                    self._knit_graph.add_loop(loop)
                                    if _ == 0:
                                        parent_loop_id_1 = self.prior_row_child_fabric[-1]
                                        parent_offset = -1 
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_child_fabric[-2]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    elif _ == self.cur_width_child_fabric - 1:
                                        parent_loop_id_1 = self.prior_row_child_fabric[0]
                                        parent_offset = 1
                                        self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                        parent_loop_id_2 = self.prior_row_child_fabric[1]
                                        self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                    else:
                                        parent_loop_id = [*reversed(self.prior_row_child_fabric)][i]
                                        self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                        i += 1
                        # assert i == prior_width - 2, f'loops in prior row has not been fully consumed' 
                        self.prior_row_child_fabric = next_row
                        self.prior_width_child_fabric = self.cur_width_child_fabric
                        self.cur_width_child_fabric = self.prior_width_child_fabric - 2
        
        return self._knit_graph
    
    def get_nodes_course_and_wale(self):
        """
        Get the [course, wale] coordinate of each node in the knit graph.
        """
        self._loop_id_to_course, self._course_to_loop_ids, self._loop_id_to_wale, self._wale_to_loop_ids = self._knit_graph.get_courses(unmodified = True)
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
        return node_to_course_and_wale, course_and_wale_to_node

    def get_yarn_graph_nodes_course_and_wale(self, node_to_course_and_wale):
        """
        Get the [course, wale] coordinate of each node on each yarn graph.
        """ 
        node_to_course_and_wale_on_yarn = {}
        yarns = [*self._knit_graph.yarns.values()]
        course_to_loop_ids_on_yarn = {}
        for yarn in yarns:
            carrier_id = yarn.carrier.carrier_ids
            node_to_course_and_wale_on_yarn['yarn on carrier' + str(carrier_id)] = {}
            course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)] = {}
            if carrier_id == self.old_yarn.carrier.carrier_ids:
                for course_id in range(0, [*self.course_id_to_shaping['parent_fabric'].keys()][-1] + 1):
                    course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id] = []
            elif carrier_id == self.new_yarn.carrier.carrier_ids:
                for course_id in range([*self.course_id_to_shaping['child_fabric'].keys()][0] - 1, [*self.course_id_to_shaping['child_fabric'].keys()][-1] + 1):
                    course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id] = []
    
        for node in self._knit_graph.graph.nodes:
            for yarn in yarns:
                if node in yarn:
                    carrier_id = yarn.carrier.carrier_ids
                    course_id = node_to_course_and_wale[node][0]
                    course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id].append(node)
                    node_to_course_and_wale_on_yarn['yarn on carrier' + str(carrier_id)][node] = node_to_course_and_wale[node]
                    break
        #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
        course_and_wale_to_node_on_yarn = {}
        for yarn in yarns:
            carrier_id = yarn.carrier.carrier_ids
            course_and_wale_to_node_on_yarn['yarn on carrier' + str(carrier_id)] = {}
            course_and_wale_to_node_on_yarn['yarn on carrier' + str(carrier_id)] = {tuple(v): k for k, v in node_to_course_and_wale_on_yarn['yarn on carrier' + str(carrier_id)].items()}
        # print('loop_ids_to_course', loop_ids_to_course)
        print('course_and_wale_to_node_on_yarn', course_and_wale_to_node_on_yarn)
        print('node_to_course_and_wale_on_yarn', node_to_course_and_wale_on_yarn)
        print('course_to_loop_ids_on_yarn', course_to_loop_ids_on_yarn)
        return node_to_course_and_wale_on_yarn, course_and_wale_to_node_on_yarn, course_to_loop_ids_on_yarn

    def get_edge_nodes_on_child_fabric(self, course_to_loop_ids_on_yarn):
        carrier_id = self.new_yarn.carrier.carrier_ids
        course_to_loop_ids_on_new_yarn = course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)]
        smaller_wale_edge_nodes = []
        bigger_wale_edge_nodes = []
        for course_id in course_to_loop_ids_on_new_yarn.keys():
            if course_id % 2 == 0:
                smaller_wale_edge_nodes.append(course_to_loop_ids_on_new_yarn[course_id][0])
                bigger_wale_edge_nodes.append(course_to_loop_ids_on_new_yarn[course_id][-1])
            elif course_id % 2 == 1:
                smaller_wale_edge_nodes.append(course_to_loop_ids_on_new_yarn[course_id][-1])
                bigger_wale_edge_nodes.append(course_to_loop_ids_on_new_yarn[course_id][0])
        return smaller_wale_edge_nodes, bigger_wale_edge_nodes
        print(f'one_edge_node is {smaller_wale_edge_nodes}, another_edge_nodes is {bigger_wale_edge_nodes}')

    def get_target_edge_nodes_on_parent_fabric(self, bigger_wale_edge_nodes, smaller_wale_edge_nodes, node_to_course_and_wale, course_and_wale_to_node_on_yarn):
        bigger_wale_target_edge_nodes = []
        smaller_wale_target_edge_nodes = []
        carrier_id = self.old_yarn.carrier.carrier_ids
        for node in bigger_wale_edge_nodes:
            course_id = node_to_course_and_wale[node][0]
            wale_id = node_to_course_and_wale[node][1]
            bigger_wale_target_edge_nodes.append(course_and_wale_to_node_on_yarn['yarn on carrier' + str(carrier_id)][(course_id, wale_id + 1)])
        for node in smaller_wale_edge_nodes:
            course_id = node_to_course_and_wale[node][0]
            wale_id = node_to_course_and_wale[node][1]
            smaller_wale_target_edge_nodes.append(course_and_wale_to_node_on_yarn['yarn on carrier' + str(carrier_id)][(course_id, wale_id - 1)])
        print(f'bigger_wale_target_edge_nodes is {bigger_wale_target_edge_nodes}, smaller_wale_target_edge_nodes is {smaller_wale_target_edge_nodes}')
        return smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes

    def actions_around_target_edge_node(self, smaller_wale_target_edge_nodes, bigger_wale_target_edge_nodes, smaller_wale_edge_connected: bool, bigger_wale_edge_connected: bool):
        #first remove target edge node
        #then operate connections involving surrounding five nodes
        if bigger_wale_edge_connected == True:
            for node in bigger_wale_target_edge_nodes:
                self._knit_graph.graph.remove_node(node) 
                self.old_yarn.yarn_graph.remove_node(node)
                del self.parent_graph_course_and_wale_to_node[self.parent_graph_node_to_course_and_wale[node]]
                course_id = self.parent_graph_node_to_course_and_wale[node][0]
                wale_id = self.parent_graph_node_to_course_and_wale[node][1]
                target_node_on_child_fabric = self.child_graph_course_and_wale_to_node[(course_id, wale_id - 1)]
                #see if in_neighbor_node_horizontal exists
                if (course_id, wale_id - 1) in self.parent_graph_course_and_wale_to_node:
                    in_neighbor_node_horizontal = self.parent_graph_course_and_wale_to_node[(course_id, wale_id - 1)]
                    if self._knit_graph.graph.has_edge(in_neighbor_node_horizontal, node):
                        if course_id % 2 == 0:
                            self._knit_graph.connect_loops(in_neighbor_node_horizontal, target_node_on_child_fabric)
                        elif course_id % 2 == 1:
                            self._knit_graph.connect_loops(target_node_on_child_fabric, in_neighbor_node_horizontal)
                    else:
                        print(f'in_neighbor_node_horizontal: {in_neighbor_node_horizontal} exists but not connected to node: {node}')
                else:
                    print(f'in_neighbor_node_horizontal does not exist at position {(course_id, wale_id - 1)}')
                #see if out_neighbor_node_horizontal exists
                if (course_id, wale_id + 1) in self.parent_graph_course_and_wale_to_node:
                    out_neighbor_node_horizontal = self.parent_graph_course_and_wale_to_node[(course_id, wale_id + 1)]
                    if self._knit_graph.graph.has_edge(node, out_neighbor_node_horizontal):
                        if course_id % 2 == 0:
                            self._knit_graph.connect_loops(target_node_on_child_fabric, out_neighbor_node_horizontal)
                        elif course_id % 2 == 1:
                            self._knit_graph.connect_loops(out_neighbor_node_horizontal, target_node_on_child_fabric)
                    else:
                        print(f'out_neighbor_node_horizontal: {out_neighbor_node_horizontal} exists but not connected from node: {node}')
                else:
                    print(f'out_neighbor_node_horizontal does not exist at position {(course_id, wale_id + 1)}')
                #see if lower neighbor node exists
                if (course_id - 1, wale_id) in self.parent_graph_course_and_wale_to_node:
                    lower_neighbor = self.parent_graph_course_and_wale_to_node[(course_id - 1, wale_id)]
                    self._knit_graph.connect_loops(lower_neighbor, target_node_on_child_fabric, parent_offset = 1)
                else:
                    print(f'lower_neighbor does not exist at position {(course_id - 1, wale_id)}')
                #see if upper_neighbor node exists
                upper_neighbor = self.parent_graph_course_and_wale_to_node[(course_id + 1, wale_id)]
                self._knit_graph.connect_loops(target_node_on_child_fabric, upper_neighbor, parent_offset = -1)

                # print('nodes need action on include', in_neighbor_node_horizontal, out_neighbor_node_horizontal, upper_neighbor, lower_neighbor, target_node_on_child_fabric)
                #update dictionary that stores nodes for visualization
                del self.pocket_graph_node_to_course_and_wale[node]
        if smaller_wale_edge_connected == True:
            for node in smaller_wale_target_edge_nodes:
                self._knit_graph.graph.remove_node(node)
                self.old_yarn.yarn_graph.remove_node(node)
                del self.parent_graph_course_and_wale_to_node[self.parent_graph_node_to_course_and_wale[node]]
                course_id = self.parent_graph_node_to_course_and_wale[node][0]
                wale_id = self.parent_graph_node_to_course_and_wale[node][1]
                target_node_on_child_fabric = self.child_graph_course_and_wale_to_node[(course_id, wale_id + 1)]
                if (course_id, wale_id - 1) in self.parent_graph_course_and_wale_to_node:
                    in_neighbor_node_horizontal = self.parent_graph_course_and_wale_to_node[(course_id, wale_id - 1)]
                    if course_id % 2 == 0:
                        self._knit_graph.connect_loops(in_neighbor_node_horizontal, target_node_on_child_fabric)
                    elif course_id % 2 == 1:
                        self._knit_graph.connect_loops(target_node_on_child_fabric, in_neighbor_node_horizontal)
                else:
                    print(f'in_neighbor_node_horizontal does not exist at position {(course_id, wale_id - 1)}')
                out_neighbor_node_horizontal = self.parent_graph_course_and_wale_to_node[(course_id, wale_id + 1)]
                upper_neighbor = self.parent_graph_course_and_wale_to_node[(course_id + 1, wale_id)]
                if course_id % 2 == 0:
                    self._knit_graph.connect_loops(target_node_on_child_fabric, out_neighbor_node_horizontal)
                elif course_id % 2 == 1:
                    self._knit_graph.connect_loops(out_neighbor_node_horizontal, target_node_on_child_fabric)
                #see if lower node exists
                if (course_id - 1, wale_id) in self.parent_graph_course_and_wale_to_node:
                    lower_neighbor = self.parent_graph_course_and_wale_to_node[(course_id - 1, wale_id)]
                    self._knit_graph.connect_loops(lower_neighbor, target_node_on_child_fabric, parent_offset = -1)
                else:
                    print(f'lower_neighbor does not exist at position {(course_id - 1, wale_id)}')
                self._knit_graph.connect_loops(target_node_on_child_fabric, upper_neighbor, parent_offset = 1)
                del self.pocket_graph_node_to_course_and_wale[node]
        print(f'updated node dict is {self.pocket_graph_node_to_course_and_wale}')
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = node_to_course_and_wale, object_type = 'pocket', unmodified = False)      
        

    def remove_nodes_to_make_graph_correct(self):
        node_to_course_and_wale, course_and_wale_to_node = self.get_nodes_course_and_wale()
        for course_range in self.shaping_trend.keys():
            shaping = self.shaping_trend[course_range]
            if shaping == 'wider':
                for course_id in range(course_range[0]+1, course_range[1]+1):
                    nodes_to_delete = [self._course_to_loop_ids[course_id][1], self._course_to_loop_ids[course_id][-2]]
                    self._knit_graph.graph.remove_nodes_from(nodes_to_delete)
                    self.yarn.yarn_graph.remove_nodes_from(nodes_to_delete)
                    #for course_to_loop_ids[1], find neightbor nodes
                    start_loop_id = self._course_to_loop_ids[course_id][0]
                    next_loop_id = self._course_to_loop_ids[course_id][2]
                    self.yarn.yarn_graph.add_edge(start_loop_id, next_loop_id)
                    #for course_to_loop_ids[-2], find neightbor nodes
                    start_loop_id = self._course_to_loop_ids[course_id][-3]
                    next_loop_id = self._course_to_loop_ids[course_id][-1]
                    self.yarn.yarn_graph.add_edge(start_loop_id, next_loop_id)
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = node_to_course_and_wale, object_type = 'pocket', unmodified = False)            
    
    def remove_stitches_to_make_graph_correct(self, course_to_loop_ids_on_yarn):
        node_to_course_and_wale, course_and_wale_to_node = self.get_nodes_course_and_wale()
        for fabric, shaping_trend in self.shaping_trend.items():
            if fabric == 'parent_fabric':
                carrier_id = self.old_yarn.carrier.carrier_ids
            elif fabric == 'child_fabric':
                carrier_id = self.new_yarn.carrier.carrier_ids
            for course_range in shaping_trend.keys():
                shaping = shaping_trend[course_range]
                if shaping == 'wider':
                    for course_id in range(course_range[0]+1, course_range[1]+1):
                        #remove first edge 
                        print('cc', course_id)
                        print(course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id - 1][0], course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id][-1], course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id - 1][-1], course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id][0])
                        self._knit_graph.graph.remove_edge(course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id - 1][0], course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id][-1])
                        #remove second edge 
                        self._knit_graph.graph.remove_edge(course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id - 1][-1], course_to_loop_ids_on_yarn['yarn on carrier' + str(carrier_id)][course_id][0])
        # print(f'yarn graph edges on old yarn are {self.old_yarn.yarn_graph.edges}')
        # print(f'yarn graph edges on new yarn are {self.new_yarn.yarn_graph.edges}')
        print(f'knit graph edges are {self._knit_graph.graph.edges}')
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = node_to_course_and_wale, object_type = 'pocket', unmodified = False)            
                    

if __name__ == '__main__':
    #rectangle for both parent fabric and child fabric
    generator = Pocket_Generator(left_keynodes_parent_fabric = [(0, 0), (6, 0)], right_keynodes_parent_fabric = [(0, 7), (6, 7)], left_keynodes_child_fabric = [(2, 2), (5, 2)], right_keynodes_child_fabric = [(2, 5), (5, 5)], split_starting_course_id = 1, spliting_nodes = [13, 12, 11, 10])
    #wider for child fabric, rectangle for parent fabric
    # generator = Pocket_Generator(left_keynodes_parent_fabric = [(0, -5), (5, -5)], right_keynodes_parent_fabric = [(0, 5), (5, 5)], left_keynodes_child_fabric = [(2, 2), (4, 0)], right_keynodes_child_fabric = [(2, 5), (4, 7)], split_starting_course_id = 1, spliting_nodes = [18, 17, 16, 15])
    #wider for child fabric, rectangle then wider for parent fabric
    # generator = Pocket_Generator(left_keynodes_parent_fabric = [(0, -5), (5, -5), (7, -7)], right_keynodes_parent_fabric = [(0, 5), (5, 5), (7, 7)], left_keynodes_child_fabric = [(2, 2), (4, 0)], right_keynodes_child_fabric = [(2, 5), (4, 7)], split_starting_course_id = 1, spliting_nodes = [18, 17, 16, 15])
    #change spliting_course_id
    # generator = Pocket_Generator(left_keynodes_parent_fabric = [(0, -5), (5, -5)], right_keynodes_parent_fabric = [(0, 5), (5, 5)], left_keynodes_child_fabric = [(1, 2), (3, 0)], right_keynodes_child_fabric = [(1, 5), (3, 7)], split_starting_course_id = 0, spliting_nodes = [6, 5, 4, 3]) #[3, 4, 5, 6]
    
    generator.generate_pocket_graph(old_carrier = 3, new_carrier = 4, close_top = False, smaller_wale_edge_connected = True, bigger_wale_edge_connected = True)
    
    # generator = Pocket_Generator(left_keynodes_parent_fabric = [(0, 0), (6, 0)], right_keynodes_parent_fabric = [(0, 7), (6, 7)], left_keynodes_child_fabric = [(0, 0), (2, 4), (3, 4)], right_keynodes_child_fabric = [(0, 6), (1, 5), (3, 5)], split_starting_course_id = 1, spliting_nodes = [13, 12, 11, 10])
    # generator = Pocket_Generator(left_keynodes_parent_fabric = [(0, 0), (6, 0)], right_keynodes_parent_fabric = [(0, 7), (6, 7)], left_keynodes_child_fabric = [(0, 0), (3, 3)], right_keynodes_child_fabric = [(0, 5), (1, 4), (2, 4), (3, 3)], split_starting_course_id = 1, spliting_nodes = [13, 12, 11, 10])
    # generator = Pocket_Generator(left_keynodes_parent_fabric = [(0, 0), (6, 0)], right_keynodes_parent_fabric = [(0, 7), (6, 7)], left_keynodes_child_fabric = [(0, 0), (9, 0)], right_keynodes_child_fabric = [(0, 3), (3, 6), (6, 6), (9, 3)], split_starting_course_id = 1, spliting_nodes = [13, 12, 11, 10])

