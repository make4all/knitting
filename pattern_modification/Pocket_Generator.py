from typing import Optional, List, Dict, Tuple
from knit_graphs.Yarn import Yarn
from knit_graphs.Knit_Graph import Knit_Graph
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler
import warnings

class Pocket_Generator:
    def __init__(self, left_keynodes, right_keynodes):
        """
        :param left_keypoints: List of (course_id, wale_id) of the spiky points on the left side of the pattern.
        :param right_keypoints: List of (course_id, wale_id) of the spiky points on the right side of the pattern.
        (Note that the keypoints should be enter in order of from bottom to top for each side, and we assume the origin
        of the pattern is (0, 0). )
        """

        self.left_keynodes: List[Tuple[int, int]] = left_keynodes
        self.right_keynodes: List[Tuple[int, int]] = right_keynodes
        self.last_keynode: Tuple[int, int] 
        self.first_course_left_wale_id: int = self.left_keynodes[0][1]
        self.first_course_right_wale_id: int = self.right_keynodes[0][1]
        self.starting_width: int
        self.num_of_nodes_each_side: int
        self.shaping_trend: Dict[Tuple(int, int), str] = {}
        self._knit_graph: Knit_Graph
        self.yarn: Yarn
        self._loop_id_to_course: Dict[int, float] 
        self._loop_id_to_wale: Dict[int, float] 
        self._course_to_loop_ids: Dict[float, List[int]]
        self._wale_to_loop_ids: Dict[float, List[int]]


    def check_keynodes_validity(self):
        """
        currently, symmetry is required for the shape
        """
        assert len(self.left_keynodes) == len(self.right_keynodes), f'num of left keynodes is not equal to num of right keynodes'
        self.num_of_nodes_each_side = len(self.left_keynodes) 
        print('self.num_of_nodes_each_side', self.num_of_nodes_each_side)
        for i in range(1, self.num_of_nodes_each_side):
            curr_right_keynode = self.right_keynodes[i]
            last_right_keynode = self.right_keynodes[i-1]
            curr_left_keynode = self.left_keynodes[i]
            last_left_keynode = self.left_keynodes[i-1]
            #assume that if width is increased, then the width change should be equal to height increase. Otherwise, path 
            # along the edge can not be determined with more than one possible options.
            width_change_left = curr_left_keynode[1] - last_left_keynode[1]
            width_change_right = curr_right_keynode[1] - last_right_keynode[1]
            increase_height = curr_right_keynode[0] - last_right_keynode[0]
            if width_change_right != 0 or width_change_right != 0:
                assert -width_change_left == width_change_right and abs(width_change_right) == increase_height, f'width_change_left is {width_change_left}, while width_change_right is {width_change_right}, and increase_height is {increase_height}'
            else:
                assert width_change_right == width_change_right == 0, f'width change: {width_change_left} on the left side is not equal to width change: {width_change_right} on the right side'
        

    def extract_shaping_trend(self) -> List[str]:
        """
        return a list recording shaping trend of the pattern.
        shaping trend includes 'wider', 'narrower', 'unchanged'.
        """
        for i in range(1, self.num_of_nodes_each_side):
            curr_right_keynode = self.right_keynodes[i]
            last_right_keynode = self.right_keynodes[i-1]
            #if wale_id is increasing, then it is defined as 'wider'.
            if curr_right_keynode[1] - last_right_keynode[1] > 0:
                self.shaping_trend[(last_right_keynode[0], curr_right_keynode[0])] = 'wider' 

            elif curr_right_keynode[1] - last_right_keynode[1] < 0:
                self.shaping_trend[(last_right_keynode[0], curr_right_keynode[0])] = 'narrower'
            
            else:
                self.shaping_trend[(last_right_keynode[0], curr_right_keynode[0])] = 'unchanged'
                    
        
    def generate_host_fabric_graph(self, carrier: int = 3) -> Knit_Graph:
        self.check_keynodes_validity()
        self.extract_shaping_trend()
        self._knit_graph = Knit_Graph()
        self.yarn = Yarn("yarn", self._knit_graph, carrier_id=carrier)
        self._knit_graph.add_yarn(self.yarn)
        #add loops for first row
        first_row = []
        self.starting_width = self.first_course_right_wale_id - self.first_course_left_wale_id + 1
        for _ in range(0, self.starting_width):
            loop_id, loop = self.yarn.add_loop_to_end()
            first_row.append(loop_id)
            self._knit_graph.add_loop(loop)
        prior_row = first_row
        prior_width = self.starting_width
        for course_range in self.shaping_trend.keys():
            shaping = self.shaping_trend[course_range]
            if shaping == 'wider':
                cur_width = prior_width + 2
                for course_id in range(course_range[0]+1, course_range[1]+1):
                    next_row = []
                    i = 0
                    if course_id % 2 == 1:
                        for _ in range(cur_width):
                            loop_id, loop = self.yarn.add_loop_to_end()
                            # print('lo',loop_id)
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            if _ == 0:
                                print('prior', prior_row)
                                parent_loop_id = prior_row[-1]
                                parent_offset = -1 
                                self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                            elif _ == cur_width - 1:
                                parent_loop_id = prior_row[0]
                                parent_offset = 1
                                self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                            else:
                                parent_loop_id = [*reversed(prior_row)][i]
                                self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                i += 1
                                print('hit')
                            print('parent_loop_id', parent_loop_id)
                            print('i', i)
                            print('prior width', prior_width)
                    elif course_id % 2 == 0:
                        for _ in range(cur_width):
                            loop_id, loop = self.yarn.add_loop_to_end()
                            next_row.append(loop_id)
                            self._knit_graph.add_loop(loop)
                            if _ == 0:
                                parent_loop_id = prior_row[-1]
                                parent_offset = 1 
                                self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                            elif _ == cur_width - 1:
                                parent_loop_id = prior_row[0]
                                parent_offset = -1
                                self._knit_graph.connect_loops(parent_loop_id, loop_id, parent_offset = parent_offset)
                            else:
                                parent_loop_id = [*reversed(prior_row)][i]
                                self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                i += 1
                    print('haha', i, prior_width, next_row)
                    assert i == prior_width, f'loops in prior row has not been fully consumed' 
                    prior_row = next_row
                    prior_width = cur_width
                    cur_width = prior_width + 2

            elif shaping == 'unchanged':  
                cur_width = prior_width 
                for course_id in range(course_range[0]+1, course_range[1]+1):
                    next_row = []
                    for parent_loop_id in [*reversed(prior_row)]:
                        loop_id, loop = self.yarn.add_loop_to_end()
                        next_row.append(loop_id)
                        self._knit_graph.add_loop(loop)
                        self._knit_graph.connect_loops(parent_loop_id, loop_id)
                    prior_row = next_row
                    prior_width = cur_width

            elif shaping == 'narrower':
                cur_width = prior_width - 2
                for course_id in range(course_range[0]+1, course_range[1]+1):
                    next_row = []
                    i = 2
                    # when course_id % 2 == 1, the yarn walking direction is opposite to the yarn starting direction
                    if course_id % 2 == 1:
                        for _ in range(cur_width):
                            if cur_width == 1:
                                loop_id, loop = self.yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                #
                                parent_loop_id_1 = prior_row[-1]
                                parent_offset = 1 
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                #
                                parent_loop_id_2 = prior_row[0]
                                parent_offset = -1 
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                #
                                parent_loop_id_3 = prior_row[1]
                                self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                            else:
                                loop_id, loop = self.yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                if _ == 0:
                                    parent_loop_id_1 = prior_row[-1]
                                    parent_offset = 1 
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    parent_loop_id_2 = prior_row[-2]
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                elif _ == cur_width - 1:
                                    parent_loop_id_1 = prior_row[0]
                                    parent_offset = -1
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    parent_loop_id_2 = prior_row[1]
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                else:
                                    parent_loop_id = [*reversed(prior_row)][i]
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                    i += 1  
                    # when course_id % 2 == 0, the yarn walking direction is the same as the yarn starting direction
                    elif course_id % 2 == 0:
                        for _ in range(cur_width):
                            if cur_width == 1:
                                loop_id, loop = self.yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                #
                                parent_loop_id_1 = prior_row[-1]
                                parent_offset = -1 
                                self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                #
                                parent_loop_id_2 = prior_row[0]
                                parent_offset = 1 
                                self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                #
                                parent_loop_id_3 = prior_row[1]
                                self._knit_graph.connect_loops(parent_loop_id_3, loop_id)
                            else:
                                loop_id, loop = self.yarn.add_loop_to_end()
                                next_row.append(loop_id)
                                self._knit_graph.add_loop(loop)
                                if _ == 0:
                                    parent_loop_id_1 = prior_row[-1]
                                    parent_offset = -1 
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    parent_loop_id_2 = prior_row[-2]
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                elif _ == cur_width - 1:
                                    parent_loop_id_1 = prior_row[0]
                                    parent_offset = 1
                                    self._knit_graph.connect_loops(parent_loop_id_1, loop_id, parent_offset = parent_offset)
                                    parent_loop_id_2 = prior_row[1]
                                    self._knit_graph.connect_loops(parent_loop_id_2, loop_id, parent_offset = parent_offset)
                                else:
                                    parent_loop_id = [*reversed(prior_row)][i]
                                    self._knit_graph.connect_loops(parent_loop_id, loop_id)
                                    i += 1
                    # assert i == prior_width - 2, f'loops in prior row has not been fully consumed' 
                    prior_row = next_row
                    prior_width = cur_width
                    cur_width = prior_width - 2
        visualize_knitGraph(self._knit_graph, unmodified = True)
        # self.remove_nodes_to_make_graph_correct()
        self.remove_stitches_to_make_graph_correct()
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
            node_to_course_and_wale[node] = [course, wale]
        #reverse the keys and values of node_to_course_and_wale to build course_and_wale_to_node
        course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
        # print('loop_ids_to_course', loop_ids_to_course)
        print('course_and_wale_to_node', course_and_wale_to_node)
        print('node_to_course_and_wale', node_to_course_and_wale)
        return node_to_course_and_wale, course_and_wale_to_node

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
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = node_to_course_and_wale, unmodified = False)            

    def remove_stitches_to_make_graph_correct(self):
        node_to_course_and_wale, course_and_wale_to_node = self.get_nodes_course_and_wale()
        for course_range in self.shaping_trend.keys():
            shaping = self.shaping_trend[course_range]
            if shaping == 'wider':
                for course_id in range(course_range[0]+1, course_range[1]+1):
                    #remove first edge 
                    self._knit_graph.graph.remove_edge(self._course_to_loop_ids[course_id - 1][0], self._course_to_loop_ids[course_id][-1])
                    #remove second edge 
                    self._knit_graph.graph.remove_edge(self._course_to_loop_ids[course_id - 1][-1], self._course_to_loop_ids[course_id][0])
        print(f'yarn graph edges are {self.yarn.yarn_graph.edges}')
        print(f'knit graph edges are {self._knit_graph.graph.edges}')
        visualize_knitGraph(self._knit_graph, node_to_course_and_wale = node_to_course_and_wale, unmodified = False)            

                    

if __name__ == '__main__':
    #first unchanged, then narrower, followed by wider
    # generator = Pocket_Generator(left_keynodes = [(0, 0), (1, 0), (3, 2), (5, 0)], right_keynodes = [(0, 7), (1, 7), (3, 5), (5, 7)])
    #first wider, then narrower, followed by unchanged
    # generator = Pocket_Generator(left_keynodes = [(0, 0), (4, -4), (6, -2), (8, -2)], right_keynodes = [(0, 3), (4, 7), (6, 5), (8, 5)])
    #first unchanged, then wider, followed by narrower
    # generator = Pocket_Generator(left_keynodes = [(0, 0), (4, 0), (6, -2), (8, 0)], right_keynodes = [(0, 3), (4, 3), (6, 5), (8, 3)])
    #smaller spiky pyramid
    generator = Pocket_Generator(left_keynodes = [(0, 0), (2, 2)], right_keynodes = [(0, 4), (2, 2)])
    #bigger spiky pyramid
    # generator = Pocket_Generator(left_keynodes = [(0, 0), (4, 4)], right_keynodes = [(0, 8), (4, 4)])
    #pyramid
    # generator = Pocket_Generator(left_keynodes = [(0, 0), (1, 1)], right_keynodes = [(0, 4), (1, 3)])
    knit_graph = generator.generate_host_fabric_graph(carrier = 3)