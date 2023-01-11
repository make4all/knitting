"""A method for visualizing KnitGraphs as a graph structure, mostly for debugging"""
from typing import Optional, Dict, List, Union, Tuple
import networkx as nx
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn #just for the draw_rebulit_graph(), which we afterwards will move to New_Hole_Generator Module
import matplotlib.pyplot as plt

from pyvis import network as nw


class knitGraph_visualizer:
    """
    :param knit_graph: the knit graph to visualize
    :param yarn_start_direction: the starting direction of the yarn, value include 'left to right' or 'right to left'.
    """
    def __init__(self, knit_graph: Knit_Graph):
        self.knit_graph: Knit_Graph = knit_graph
        self.object_type = knit_graph.object_type
        # self.yarn_start_direction = yarn_start_direction
        self.yarn_start_direction =  knit_graph.yarn_start_direction
        self.node_to_course_and_wale: Dict[int, (int, int)] = knit_graph.node_to_course_and_wale
        self.node_on_front_or_back: Dict[int, str] = knit_graph.node_on_front_or_back
        # commented out below because we have not yet used "self.course_and_wale_and_bed_to_node" here.
        # self.course_and_wale_and_bed_to_node: Dict[((int, int), str), int] = {}
        # for node in self.node_on_front_or_back.keys():
        #     course_and_wale = self.node_to_course_and_wale[node]
        #     front_or_back = self.node_on_front_or_back[node]
        #     self.course_and_wale_and_bed_to_node[(course_and_wale, front_or_back)] = node
        print('node_to_course_and_wale viz', self.node_to_course_and_wale)
        print('node_on_front_or_back viz', self.node_on_front_or_back)
        # print('course_and_wale_and_bed_to_node viz', self.course_and_wale_and_bed_to_node)
        self.nodes_to_positions: Dict[int, Dict[str, float]] = {} 
        # we assume different carrier carry yarns of differnt color, though practically they can be the same.
        self.carrier_id_to_color = {1:'black', 2:'skyblue', 3:'orange', 4:'green', 5: 'yellow', 6:'blue', 7: 'pink', 8: 'purple', 9:'cyan', 10:'red'}
        self.cable_depth_to_color = {1:'grey', -1:'magenta'}
        self.alpha_front = 1
        self.alpha_back = 0.6
        self.node_color_property = {}
        self.edge_color_property = {}
        self.stitch_labels = {}
        self.yarns = [*knit_graph.yarns.values()]
        # if len(self.yarns) == 1:
        #     print(f'yarn edges is {self.yarns[0].yarn_graph.edges}')
        # print('yarns', self.yarns)
        #distance related param for tube
        self.h_back2front, self.w_back2front, self.w_between_node, self.h_course = 0.4, 0.1, 0.5, 1
    #below are skeletal functions to complete visualization
    #set node postion 
    def get_nodes_position(self):
        x0 = 0
        y0 = 0
        for node in self.knit_graph.graph.nodes:
            self.nodes_to_positions[node] = {}
            self.node_color_property[node] = {}
            course = self.node_to_course_and_wale[node][0]
            wale = self.node_to_course_and_wale[node][1]
            if self.node_on_front_or_back[node] == 'f':
                x0 = 0 #initialize x0 from 0.3 to 0
                if self.yarn_start_direction == 'left to right':
                    self.nodes_to_positions[node]['x'] = x0 + wale * self.w_between_node       
                elif self.yarn_start_direction == 'right to left':
                    self.nodes_to_positions[node]['x'] = x0 - wale * self.w_between_node
                self.nodes_to_positions[node]['y'] = y0 + course * self.h_course
            elif self.node_on_front_or_back[node] == 'b':
                # if self.object_type == 'pocket' or self.object_type == 'handle':
                if self.object_type == 'tube':
                    x0 = 0  #0.6
                    h_course =  1*self.h_course 
                    if self.yarn_start_direction == 'left to right':
                        self.nodes_to_positions[node]['x'] = x0 + wale * self.w_between_node 
                    elif self.yarn_start_direction == 'right to left':
                        self.nodes_to_positions[node]['x'] = x0 - wale * self.w_between_node 
                    # self.nodes_to_positions[node]['y'] = y0 + course * h_course
                    self.nodes_to_positions[node]['y'] = y0 + course * self.h_course + self.h_back2front
                else:
                    if self.yarn_start_direction == 'left to right':
                        self.nodes_to_positions[node]['x'] = x0 + wale * self.w_between_node + self.w_back2front
                    elif self.yarn_start_direction == 'right to left':
                        self.nodes_to_positions[node]['x'] = x0 - wale * self.w_between_node + self.w_back2front
                    self.nodes_to_positions[node]['y'] = y0 + course * self.h_course + self.h_back2front
        # print(f'nodes_to_positions is {self.nodes_to_positions}')
    #set node color
    def get_nodes_color(self):
        for node in self.knit_graph.graph.nodes:
            #find carrier_id of the node
            #first identify the yarn of the node
            for yarn in self.yarns:
                if node in yarn:
                    carrier_id = yarn.carrier.carrier_ids
                    break
            #store node color property
            self.node_color_property[node]['color'] = self.carrier_id_to_color[carrier_id]
            self.node_color_property[node]['alpha'] = self.alpha_front if self.node_on_front_or_back[node] == 'f' else self.alpha_back
    #get yarn edges color
    def get_yarn_edges(self):
        #add yarn edges and set edge color
        for yarn in self.yarns:
            for prior_node, next_node in yarn.yarn_graph.edges:
                self.edge_color_property[(prior_node, next_node)] = {}
                carrier_id = yarn.carrier.carrier_ids
                self.edge_color_property[(prior_node, next_node)]['color'] = self.carrier_id_to_color[carrier_id]
                #As long as either node on the edge is on the front, then the edge is regarded as on the front and will be colored brighter
                self.edge_color_property[(prior_node, next_node)]['alpha'] = self.alpha_front if self.node_on_front_or_back[prior_node] == 'f' and self.node_on_front_or_back[next_node] == 'f' else self.alpha_back
    #get stitch edges color
    def get_stitch_edges(self):
        #add stitch edges and set edge color
        for parent_id, child_id in self.knit_graph.graph.edges:
            self.edge_color_property[(parent_id, child_id)] = {}
            self.edge_color_property[(parent_id, child_id)]['alpha'] = self.alpha_front if self.node_on_front_or_back[parent_id] == 'f' and self.node_on_front_or_back[child_id] == 'f' else self.alpha_back
            self.stitch_labels[(parent_id, child_id)] = self.knit_graph.graph[parent_id][child_id]["pull_direction"].opposite() if self.node_on_front_or_back[child_id] == 'b' else self.knit_graph.graph[parent_id][child_id]["pull_direction"]
            flag_for_on_yarn = False
            for yarn in self.yarns:
                #if stitch edge color is determined by child_id, use below one
                # if child_id in yarn:
                #if stitch edge color is determined by parent_id, use below one
                if parent_id in yarn:
                    flag_for_on_yarn = True
                    carrier_id = yarn.carrier.carrier_ids
                    self.edge_color_property[(parent_id, child_id)]['color'] = self.carrier_id_to_color[carrier_id]
                    break
            if self.knit_graph.graph[parent_id][child_id]["depth"] < 0:
                depth = -1
                self.edge_color_property[(parent_id, child_id)]['color'] = self.cable_depth_to_color[depth]
            elif self.knit_graph.graph[parent_id][child_id]["depth"] > 0:
                depth = 1
                self.edge_color_property[(parent_id, child_id)]['color'] = self.cable_depth_to_color[depth]
                        #if nodes not on any yarns, then it will be colored 'maroon'
            if flag_for_on_yarn == False:
                self.edge_color_property[(parent_id, child_id)]['color'] = 'maroon'
        print(f'self.stitch_labels is {self.stitch_labels}')
    # draw the graph
    def draw_graph(self):
        #create a graph
        G = nx.DiGraph()
        #derive position of nodes
        pos ={}
        for node in self.nodes_to_positions:
            pos[node] = [*self.nodes_to_positions[node].values()]
        #add nodes
        G.add_nodes_from(pos.keys())
        #draw nodes
        for node in G.nodes():
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_size = 400, node_color = self.node_color_property[node]['color'], alpha = self.node_color_property[node]['alpha'])
        #draw edges
        for edge in [*self.edge_color_property.keys()]:
            nx.draw_networkx_edges(G, pos, edgelist=[edge], width=5.0, edge_color = self.edge_color_property[edge]['color'], style = 'solid', alpha = self.edge_color_property[edge]['alpha'])
        #draw node labels
        node_labels = {x: x for x in G.nodes}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_color='w')
        #draw edge labels
        nx.draw_networkx_edge_labels(G, pos, edge_labels = self.stitch_labels, label_pos=0.5, font_size=10, font_color='k', rotate=False)
        plt.show()

        # nt = nw.Network('1000px', '1000px')
        # nt.from_nx(G)
        # nt.show('nx.html')
    
    def visualize(self):
        self.get_nodes_position()
        self.get_nodes_color()
        self.get_yarn_edges()
        self.get_stitch_edges()
        self.draw_graph()
        
    

    
    