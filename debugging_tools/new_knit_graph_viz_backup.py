"""A method for visualizing KnitGraphs as a graph structure, mostly for debugging"""
from turtle import distance
from typing import Optional, Dict, List, Union, Tuple
import networkx as nx
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn #just for the draw_rebulit_graph(), which we afterwards will move to New_Hole_Generator Module
import matplotlib.pyplot as plt


def visualize_knitGraph(knit_graph: Knit_Graph, unmodified: bool = True, is_polygon: bool = False, object_type: str = 'sheet', yarn_start_direction: str = 'left to right', node_to_course_and_wale: Optional[Dict] = None):
    """
    Runs an html file in browser to visualize the given knitgraph
    :param display_name: The html file name to display from
    :param knit_graph: the knit graph to visualize
    :param height: the height of the html window
    :param width: the width of the html window
    :param yarn_start_direction: the starting direction of the yarn, value include 'left to right' or 'right to left'.
    """
    # print('knit_graph.edges(data=True)', knit_graph.graph.edges(data=True))
    if unmodified == False or is_polygon == True:
        assert node_to_course_and_wale is not None
    loop_ids_to_course, course_to_loop_ids, loop_ids_to_wale, wale_to_loop_ids = knit_graph.get_courses(unmodified)
    if node_to_course_and_wale == None:
        # get the [course, wale] coordinate of each node in the knit graph
        node_to_course_and_wale = {}
        for node in knit_graph.graph.nodes:
            course = loop_ids_to_course[node]
            wale = loop_ids_to_wale[node]
            node_to_course_and_wale[node] = (course, wale)
    course_and_wale_to_node = {tuple(v): k for k, v in node_to_course_and_wale.items()}
    print('loop_ids_to_wale in viz', loop_ids_to_wale)
    print('wale_to_loop_ids in viz', wale_to_loop_ids)
    print('course_to_loop_ids in viz', course_to_loop_ids)
    print('node_to_course_and_wale viz', node_to_course_and_wale)
    print('course_and_wale_to_node viz', course_and_wale_to_node)
    #make the yarn_start_direction consistent with actual machines setting
    # if object_type == 'tube':
    #     yarn_start_direction = 'right to left'
    # 
    nodes_to_positions = {} 
    # we assume different carrier carry yarns of differnt color, though practically they can be the same.
    carrier_id_to_color = {1:'black', 2:'skyblue', 3:'orange', 4:'green', 5: 'yellow', 6:'blue', 7: 'pink', 8: 'purple', 9:'cyan', 10:'red'}
    cable_depth_to_color = {1:'grey', -1:'magenta'}
    alpha_front = 1
    alpha_back = 0.6
    front_side_x_pos = []
    node_color_property = {}
    edge_color_property = {}
    stitch_labels = {}
    yarns = [*knit_graph.yarns.values()]
    print('yarns', yarns)
    #distance related param for tube
    h_back2front, w_back2front, w_between_node, h_course = 0.4, 0.1, 0.5, 1
    # below does not work for gauge that is not full gauging
    if object_type == 'tube':
        max_wale_id = max(node_to_course_and_wale.values(), key = lambda k: k[1])[1]
        assert (max_wale_id+1)%2 == 0, f"the number of loops in first course should be an even number"
        tube_bottom_width = int((max_wale_id+1)/2) 

    #visualization for non-tube/sheets
    def visualize_sheet():
        #set node postion 
        def get_nodes_position():
            x0 = 0
            y0 = 0
            for node in knit_graph.graph.nodes:
                nodes_to_positions[node] = {}
                node_color_property[node] = {}
                course = node_to_course_and_wale[node][0]
                wale = node_to_course_and_wale[node][1]
                #store node position 
                if yarn_start_direction == 'left to right':
                    nodes_to_positions[node]['x'] = x0 + wale * w_between_node
                elif yarn_start_direction == 'right to left':
                    nodes_to_positions[node]['x'] = x0 - wale * w_between_node
                nodes_to_positions[node]['y'] = y0 + course * h_course
        #set node color
        def get_nodes_color():
            for node in knit_graph.graph.nodes:
                #find carrier_id of the node
                #first identify the yarn of the node
                for yarn in yarns:
                    if node in yarn:
                        carrier_id = yarn.carrier.carrier_ids
                        break
                #store node color property
                node_color_property[node]['color'] = carrier_id_to_color[carrier_id]

        # @deprecated("Deprecated because this infers x coordinate by x -= w_between_node or x += w_between_node, do not work for
        # a node that sits in between that not only has no parent but also has less than two neighbors") 
        def deprecated_get_nodes_position():
            x = 0
            y = 0
            for node in knit_graph.graph.nodes:
                nodes_to_positions[node] = {}
                node_color_property[node] = {}
                course = loop_ids_to_course[node]
                parent_ids = [*knit_graph.graph.predecessors(node)]
                if len(parent_ids) == 0:
                    def yarn_layout(yarn_start_direction, x):
                        #set the yarn start from left to right
                        if yarn_start_direction == 'left to right':
                            if course % 2 == 0:
                                x += w_between_node
                            else:
                                x -= w_between_node
                        #set the yarn start from right to left
                        elif yarn_start_direction == 'right to left':
                            if course % 2 == 0:
                                x -= w_between_node
                            else:
                                x += w_between_node
                        return x
                    x = yarn_layout(yarn_start_direction, x)
                else:
                    for parent_id in parent_ids:
                        parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
                        original_parent_id = parent_id - parent_offset
                        parent_course = loop_ids_to_course[parent_id]
                        x = nodes_to_positions[original_parent_id]['x']
                        # To better express shaping effect, use below one
                        # y = nodes_to_positions[original_parent_id]['y'] + h_course
                        # To avoid visual confusion, use below one to locate node
                        y = nodes_to_positions[original_parent_id]['y'] + (course - parent_course)*h_course
                        break
                nodes_to_positions[node]['x'] = x
                nodes_to_positions[node]['y'] = y

        #get yarn edges color
        def get_yarn_edges():
            #add yarn edges and set edge color
            for yarn in yarns:
                for prior_node, next_node in yarn.yarn_graph.edges:
                    edge_color_property[(prior_node, next_node)] = {}
                    carrier_id = yarn.carrier.carrier_ids
                    edge_color_property[(prior_node, next_node)]['color'] = carrier_id_to_color[carrier_id]

        #get stitch edges color
        def get_stitch_edges():
            #add stitch edges and set edge color
            for parent_id, child_id in knit_graph.graph.edges:
                edge_color_property[(parent_id, child_id)] = {}
                stitch_labels[(parent_id, child_id)] = knit_graph.graph[parent_id][child_id]["pull_direction"]
                flag_for_on_yarn = False
                for yarn in yarns:
                    #if stitch edge color is determined by child_id, use below one
                    # if child_id in yarn:
                    #if stitch edge color is determined by parent_id, use below one
                    if parent_id in yarn:
                        flag_for_on_yarn = True
                        carrier_id = yarn.carrier.carrier_ids
                        edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
                        break
                # color the edge based on cabling depth
                if knit_graph.graph[parent_id][child_id]["depth"] < 0:
                    depth = -1
                    edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
                elif knit_graph.graph[parent_id][child_id]["depth"] > 0:
                    depth = 1
                    edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
                #if nodes not on any yarns, then it will be colored 'maroon'
                if flag_for_on_yarn == False:
                    edge_color_property[(parent_id, child_id)]['color'] = 'maroon'
                # print('parent_id, child_id', parent_id, child_id)
                # print('parent_id, child_id', parent_id, child_id, edge_color_property[(parent_id, child_id)]['color'])

        def draw_graph():
            #create a graph
            G = nx.DiGraph()
            #derive position of nodes
            pos ={}
            for node in nodes_to_positions:
                pos[node] = [*nodes_to_positions[node].values()]
            #add nodes
            G.add_nodes_from(pos.keys())
            #draw nodes
            for node in G.nodes():
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_size = 600, node_color=node_color_property[node]['color'])
            #draw edges
            for edge in [*edge_color_property.keys()]:
                nx.draw_networkx_edges(G, pos, edgelist=[edge], width=5.0, edge_color=edge_color_property[edge]['color'], style='solid')
            #draw node labels
            node_labels = {x: x for x in G.nodes}
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_color='w')
            #draw edge labels
            nx.draw_networkx_edge_labels(G, pos, edge_labels=stitch_labels, label_pos=0.5, font_size=10, font_color='k', rotate=False)
            plt.show()

        """
        def find_shortest_path_for_sheet(node_to_delete: List[int]):
            G1 = nx.DiGraph()
            # node_to_delete = [18, 19]
            # node_to_delete = [28, 29, 18, 19]
            # node_to_delete = [28, 29, 34, 35]
            # node_to_delete = [26, 27, 28, 29]
            # node_to_delete = [28, 29, 34, 35, 44, 45]
            knit_graph.graph.remove_nodes_from(node_to_delete)
            for yarn in yarns:
                yarn.yarn_graph.remove_nodes_from(node_to_delete)
            # add stitch paths
            for parent_id, child_id in knit_graph.graph.edges:
                G1.add_edge(parent_id, child_id, weight = -1)
            # add yarn paths
            for yarn in yarns:
                for prior_node, next_node in yarn.yarn_graph.edges:
                    G1.add_edge(prior_node, next_node, weight = -10)
                    # below two syntax works too
                    # nx.add_path(G, [prior_node, next_node], distance = 1)
                    # G.edges[prior_node, next_node]['distance'] = 1
            # we use bellman-ford rather than dijkstra because the former can deal with negative weighted graph while the latter cannot.
            # note that the shortest_path() below does not include "target" param, what it returns is the shortest path to all other nodes on the graph
            shortest_paths = nx.shortest_path(G1, source=0, weight='weight', method = 'bellman-ford')
            # shortest_paths = nx.shortest_path(G1,source=0,target=55, weight='weight', method = 'dijkstra')
            # get dict whose keys are reward, and values are corresponding shortest path
            d_reward_to_path = {}
            for destination in shortest_paths.keys():
                reward = nx.dijkstra_path_length(G1, 0, destination)
                d_reward_to_path[reward] = shortest_paths[destination]
            # get complete node set
            all_nodes = set(G1.nodes)
            # get complete yarn edge set
            for yarn in yarns:
                all_yarn_edges = set(yarn.yarn_graph.edges)
            # iterate over the dict "d_reward_to_path" according to ascending order of reward (i.e, from smaller to larger, since reward is a non-positive number due to
            # negative weights in our graph, thus shortest path on old yarn has smallest reward (most negative), in other words, the longest path)
            for reward, path_on_old_yarn in sorted(d_reward_to_path.items()):
                # print((reward, path_on_old_yarn))
                # if not copy but instead using "G1_for_new_yarn = G1", any action taken on updated_G1 will be applied to G1, which is unwanted
                # G1_for_new_yarn = nx.DiGraph()
                G1_for_new_yarn = G1.copy()
                # initialize node set for old yarn and new yarn
                node_on_old_yarn = set()
                node_on_new_yarn = set()
                # initialize yarn edge set for old yarn and new yarn
                old_yarn_edges = set()
                new_yarn_edges = set()
                # add node on old yarn in the set
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
                destination = max(remain_nodes)
                start_node = min(remain_nodes)
                # get shortest_path from start_node to destination in remain_nodes set
                # note that we need to update the graph for new yarn to go through after assigning the nodes to old yarn
                print('G1 before update', G1_for_new_yarn)
                # now it becomes real "G1_for_new_yarn"
                G1_for_new_yarn.remove_nodes_from(path_on_old_yarn)
                print('path', path_on_old_yarn)
                print('updated G1', G1_for_new_yarn)
                print(f'G1_for_new_yarn.nodes is {G1_for_new_yarn.nodes}, G1_for_new_yarn.edges is {G1_for_new_yarn.edges}')
                print('remain_nodes', remain_nodes)
                print('node_on_old_yarn', node_on_old_yarn)
                print(f'start_node is {start_node}, destination is {destination}')
                print('set(G1_for_new_yarn.nodes) == remain_nodes', set(G1_for_new_yarn.nodes) == remain_nodes)
                if nx.has_path(G1_for_new_yarn, source = start_node, target = destination) == True:
                    # sp means shortest path
                    # note that shortest_path() below does include the "target" param, because for situation where we have only one hole on the graph, it can be guaranteed
                    # that with only two yarns, each node and each edge on the graph can be visited.
                    sp_on_new_yarn = nx.shortest_path(G1_for_new_yarn, source = start_node, target = destination, weight='weight', method = 'bellman-ford')
                else: 
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
                    continue
                # constraint 2: ensure union of node_on_new_yarn and node_on_old_yarn == all_node
                if all_yarn_edges.issubset(old_yarn_edges.union(new_yarn_edges)) == False:
                    continue
                print(f'highest reward is {reward}, path for old yarn is {path_on_old_yarn}, while path for new yarn is {sp_on_new_yarn}')
                # when two path on two yarn can satisfy the above two constraints, the for loop would break
                break
        """
        get_nodes_position()
        get_nodes_color()
        get_yarn_edges()
        get_stitch_edges()
        # find_shortest_path_for_sheet(node_to_delete = [28, 29, 18, 19])
        draw_graph()
        

    #visualization for pocket
    def visualize_pocket():
        def get_nodes_position(yarn, h_course):
            if yarn == yarns[0]:
                x0 = 0
                y0 = 0
            elif yarn == yarns[1]:
                x0 = 0.3
                # to make close top stitch more easily be seen on the graph, change "y0 = 0.2" to "y0 = -0.5". (thus the nodes on the child fabric would appear a bit lower than corresponding nodes sharing the same course on parent knitgraph)
                y0 = 0
                # found that even adjust to y0 = -0.5, close top stitch can be seen now, however, bottom spliting edge will become unseen anymore. Thus, try to use the below method: 0.9*h_course to solve the issue.
                h_course = 0.98*h_course 
            for node in yarn.yarn_graph.nodes:
                nodes_to_positions[node] = {}
                node_color_property[node] = {}
                course = node_to_course_and_wale[node][0]
                wale = node_to_course_and_wale[node][1]
                #store node position 
                if yarn_start_direction == 'left to right':
                    nodes_to_positions[node]['x'] = x0 + wale * w_between_node
                elif yarn_start_direction == 'right to left':
                    nodes_to_positions[node]['x'] = x0 - wale * w_between_node
                nodes_to_positions[node]['y'] = y0 + course * h_course
        #set node color
        def get_nodes_color():
            for node in knit_graph.graph.nodes:
                #find carrier_id of the node
                #first identify the yarn of the node
                for yarn in yarns:
                    if node in yarn:
                        carrier_id = yarn.carrier.carrier_ids
                        break
                #store node color property
                node_color_property[node]['color'] = carrier_id_to_color[carrier_id]
                node_color_property[node]['alpha'] = alpha_front if node in yarns[0].yarn_graph.nodes else alpha_back
        
        #get yarn edges color
        def get_yarn_edges():
            #add yarn edges and set edge color
            for yarn in yarns:
                for prior_node, next_node in yarn.yarn_graph.edges:
                    edge_color_property[(prior_node, next_node)] = {}
                    carrier_id = yarn.carrier.carrier_ids
                    edge_color_property[(prior_node, next_node)]['color'] = carrier_id_to_color[carrier_id]
                    edge_color_property[(prior_node, next_node)]['alpha'] = alpha_front if prior_node in yarns[0].yarn_graph.nodes and next_node in yarns[0].yarn_graph.nodes else alpha_back
        #get stitch edges color
        def get_stitch_edges():
            #add stitch edges and set edge color
            for parent_id, child_id in knit_graph.graph.edges:
                edge_color_property[(parent_id, child_id)] = {}
                edge_color_property[(parent_id, child_id)]['alpha'] = alpha_front if parent_id in yarns[0].yarn_graph.nodes and child_id in yarns[0].yarn_graph.nodes else alpha_back
                stitch_labels[(parent_id, child_id)] = knit_graph.graph[parent_id][child_id]["pull_direction"]
                flag_for_on_yarn = False
                # flag_for_stitch_color = False
                for yarn in yarns:
                    # #if stitch edge color is determined by child_id, use below one
                    # # if child_id in yarn:
                    # #if stitch edge color is determined by parent_id, use below one
                    if parent_id in yarn:
                        flag_for_on_yarn = True
                        carrier_id = yarn.carrier.carrier_ids
                        edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
                        break
                #     if child_id in yarn and parent_id in yarn:
                #         carrier_id = yarn.carrier.carrier_ids
                #         edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
                #         flag_for_stitch_color = True
                #         break
                # if flag_for_stitch_color == False:
                #     for yarn in yarns:
                #         if yarn.yarn_id == 'old_yarn':
                #             #get carrier_id of old yarn, whose yarn_id is "yarn".
                #             carrier_id = yarn.carrier.carrier_ids
                #             edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
                            
                # color the edge based on cabling depth
                if knit_graph.graph[parent_id][child_id]["depth"] < 0:
                    depth = -1
                    edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
                elif knit_graph.graph[parent_id][child_id]["depth"] > 0:
                    depth = 1
                    edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
                #if nodes not on any yarns, then it will be colored 'maroon'
                if flag_for_on_yarn == False:
                    edge_color_property[(parent_id, child_id)]['color'] = 'maroon'
                # print('parent_id, child_id', parent_id, child_id)
                # print('parent_id, child_id', parent_id, child_id, edge_color_property[(parent_id, child_id)]['color'])

        def draw_graph():
            #create a graph
            G = nx.DiGraph()
            #derive position of nodes
            pos ={}
            for node in nodes_to_positions:
                pos[node] = [*nodes_to_positions[node].values()]
            #add nodes
            G.add_nodes_from(pos.keys())
            #draw nodes
            for node in G.nodes():
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_size = 600, node_color=node_color_property[node]['color'], alpha = node_color_property[node]['alpha'])
            #draw edges
            for edge in [*edge_color_property.keys()]:
                nx.draw_networkx_edges(G, pos, edgelist=[edge], width=5.0, edge_color=edge_color_property[edge]['color'], style='solid', alpha = edge_color_property[edge]['alpha'])
            #draw node labels
            node_labels = {x: x for x in G.nodes}
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_color='w')
            #draw edge labels
            nx.draw_networkx_edge_labels(G, pos, edge_labels=stitch_labels, label_pos=0.5, font_size=10, font_color='k', rotate=False)
            plt.show()

        get_nodes_position(yarns[0], h_course)
        get_nodes_position(yarns[1], h_course)
        get_nodes_color()
        get_yarn_edges()
        get_stitch_edges()
        draw_graph()

    #visualization for tube
    def visualize_tube():
        #set node postion 
        def get_nodes_position():
            x0 = 0
            y0 = 0
            for node in knit_graph.graph.nodes:
                nodes_to_positions[node] = {}
                node_color_property[node] = {}
                course = node_to_course_and_wale[node][0]
                wale = node_to_course_and_wale[node][1]
                if wale <= tube_bottom_width - 1:
                    if yarn_start_direction == 'left to right':
                        nodes_to_positions[node]['x'] = x0 + wale * w_between_node       
                    elif yarn_start_direction == 'right to left':
                        nodes_to_positions[node]['x'] = x0 - wale * w_between_node
                    nodes_to_positions[node]['y'] = y0 + course * h_course
                    front_side_x_pos.append(nodes_to_positions[node]['x'])
                else:
                    nodes_to_positions[node]['x'] = nodes_to_positions[tube_bottom_width*2 - 1 - wale]['x'] + w_back2front
                    nodes_to_positions[node]['y'] = y0 + course * h_course + h_back2front
        
        #set node color and transparency
        def get_nodes_color():
            for node in knit_graph.graph.nodes:
                #find carrier_id of the node
                #first identify the yarn of the node
                for yarn in yarns:
                    if node in yarn:
                        carrier_id = yarn.carrier.carrier_ids
                #store node color property
                node_color_property[node]['color'] = carrier_id_to_color[carrier_id]
                node_color_property[node]['alpha'] = alpha_front if nodes_to_positions[node]['x'] in front_side_x_pos else alpha_back
        
        #get yarn edges color
        def get_yarn_edges():
            #add yarn edges and set edge color
            for yarn in yarns:
                for prior_node, next_node in yarn.yarn_graph.edges:
                    edge_color_property[(prior_node, next_node)] = {}
                    carrier_id = yarn.carrier.carrier_ids
                    edge_color_property[(prior_node, next_node)]['color'] = carrier_id_to_color[carrier_id]
                    #As long as either node on the edge is on the front, then the edge is regarded as on the front and will be colored brighter
                    edge_color_property[(prior_node, next_node)]['alpha'] = alpha_front if nodes_to_positions[prior_node]['x'] in front_side_x_pos and nodes_to_positions[next_node]['x'] in front_side_x_pos else alpha_back
        
        #get stitch edges color
        def get_stitch_edges():
            #add stitch edges and set edge color
            for parent_id, child_id in knit_graph.graph.edges:
                edge_color_property[(parent_id, child_id)] = {}
                edge_color_property[(parent_id, child_id)]['alpha'] = alpha_front if nodes_to_positions[parent_id]['x'] in front_side_x_pos and nodes_to_positions[child_id]['x'] in front_side_x_pos else alpha_back
                stitch_labels[(parent_id, child_id)] = knit_graph.graph[parent_id][child_id]["pull_direction"]
                flag_for_on_yarn = False
                for yarn in yarns:
                    #if stitch edge color is determined by child_id, use below one
                    # if child_id in yarn:
                    #if stitch edge color is determined by parent_id, use below one
                    if parent_id in yarn:
                        flag_for_on_yarn = True
                        carrier_id = yarn.carrier.carrier_ids
                        edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
                        break
                if knit_graph.graph[parent_id][child_id]["depth"] < 0:
                    depth = -1
                    edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
                elif knit_graph.graph[parent_id][child_id]["depth"] > 0:
                    depth = 1
                    edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
                         #if nodes not on any yarns, then it will be colored 'maroon'
                if flag_for_on_yarn == False:
                    edge_color_property[(parent_id, child_id)]['color'] = 'maroon'

        #draw the graph
        def draw_graph():
            #create a graph
            G = nx.DiGraph()
            #derive position of nodes
            pos ={}
            for node in nodes_to_positions:
                pos[node] = [*nodes_to_positions[node].values()]
            #add nodes
            G.add_nodes_from(pos.keys())
            #draw nodes
            for node in G.nodes():
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_size = 600, node_color=node_color_property[node]['color'], alpha = node_color_property[node]['alpha'])
            #draw edges
            for edge in [*edge_color_property.keys()]:
                nx.draw_networkx_edges(G, pos, edgelist=[edge], width=5.0, edge_color=edge_color_property[edge]['color'], style='solid', alpha=edge_color_property[edge]['alpha'])
            #draw node labels
            node_labels = {x: x for x in G.nodes}
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_color='w')
            #draw edge labels
            nx.draw_networkx_edge_labels(G, pos, edge_labels=stitch_labels, label_pos=0.5, font_size=10, font_color='k', rotate=False)
            plt.show()
        '''
        def find_shortest_path_for_tube(node_to_delete: List[int]):
            G1 = nx.DiGraph()   
            # preprocessing: add more edges to the graph to make the path searching problem solvable
            def preprocessing_on_graph(G):
                # 1. add yarn paths of opposite direction in addition to the original direction for any neighbor nodes on the same course
                for yarn in yarns:
                    for prior_node, next_node in yarn.yarn_graph.edges:
                        # different from sheet, for a tube, the yarn edge/yarn path needs to be walkable in both left and right direction, otherwise the problem tend to be
                        # have no solution
                        G1.add_edge(prior_node, next_node, weight = -10)
                        # add an edge that is exactly of opposite direction again if they are on the same course
                        if node_to_course_and_wale[prior_node][0] == node_to_course_and_wale[next_node][0]:
                            G1.add_edge(next_node, prior_node, weight = -10)
                # 2. add edge of two opposite direction between the start node and end node on each course
                for course_id in course_to_loop_ids.keys():
                    start_node = course_to_loop_ids[course_id][0]
                    end_node = course_to_loop_ids[course_id][-1]
                    G1.add_edge(start_node, end_node, weight = -10)
                    G1.add_edge(end_node, start_node, weight = -10)
                # 3. add stitch paths, for each node, it should have three stitch edges, one is connected with node right above it, one is one wale left above it, and one
                # is one wale right above it. first node and last node on each course is special node, thus need separate discussion as below.
                for node in G1.nodes:
                    wale_id = node_to_course_and_wale[node][1]
                    course_id = node_to_course_and_wale[node][0]
                    # for first node on each course
                    if node == course_to_loop_ids[course_id][0]:
                        #node right above it
                        if (course_id+1, wale_id) in node_to_course_and_wale.values():
                            above_node = course_and_wale_to_node[(course_id+1, wale_id)]
                            G1.add_edge(node, above_node, weight = -1)
                        #node one wale right above it
                        if (course_id+1, wale_id+1) in node_to_course_and_wale.values():
                            right_above_node = course_and_wale_to_node[(course_id+1, wale_id+1)]
                            G1.add_edge(node, right_above_node, weight = -1)
                        #last node on next course
                        if course_id+1 in course_to_loop_ids.keys():
                            target_node = course_to_loop_ids[course_id+1][-1]
                            G1.add_edge(node, target_node, weight = -1)
                    # for last node on each course
                    elif node == course_to_loop_ids[course_id][-1]:
                        #node right above it
                        if (course_id+1, wale_id) in node_to_course_and_wale.values():
                            above_node = course_and_wale_to_node[(course_id+1, wale_id)]
                            G1.add_edge(node, above_node, weight = -1)
                        #node one wale left above it
                        if (course_id+1, wale_id-1) in node_to_course_and_wale.values():
                            left_above_node = course_and_wale_to_node[(course_id+1, wale_id-1)]
                            G1.add_edge(node, left_above_node, weight = -1)
                        #first node on next course
                        if course_id+1 in course_to_loop_ids.keys():
                            target_node = course_to_loop_ids[course_id+1][0]
                            G1.add_edge(node, target_node, weight = -1)
                    # for node in beweetn on each course 
                    else:
                        #node right above it
                        if (course_id+1, wale_id) in node_to_course_and_wale.values():
                            above_node = course_and_wale_to_node[(course_id+1, wale_id)]
                            G1.add_edge(node, above_node, weight = -1)
                        #node one wale left above it
                        if (course_id+1, wale_id-1) in node_to_course_and_wale.values():
                            left_above_node = course_and_wale_to_node[(course_id+1, wale_id-1)]
                            G1.add_edge(node, left_above_node, weight = -1)
                        #node one wale right above it
                        if (course_id+1, wale_id+1) in node_to_course_and_wale.values():
                            right_above_node = course_and_wale_to_node[(course_id+1, wale_id+1)]
                            G1.add_edge(node, right_above_node, weight = -1)
                # print('all edges', G1.edges)

            # path search algorithm for the graph of tube with a hole
            def path_search(G, yarn:str):
                # for old yarn, source node always starts from 0
                if yarn == 'old':
                    source_node = 0
                    visited_nodes = [0]
                    curr_course_id = 0
                elif yarn == 'new':
                    source_node = min(set(G.nodes))
                    visited_nodes = [source_node]
                    curr_course_id = node_to_course_and_wale[source_node][0]
                reward = 0
                course_nodes = []
                
                while source_node != None:
                    print('source_node', source_node)
                    reward_dict = {}
                    course_id = node_to_course_and_wale[source_node][0]
                    print('course_id', course_id)
                    total_num_of_nodes_each_course = len(course_to_loop_ids[course_id])
                    if course_id != curr_course_id:
                        course_nodes = []
                        # course_nodes.append(source_node)
                        curr_course_id = course_id
                    course_nodes.append(source_node)
                    print('course_nodes', course_nodes)
                    if len(course_nodes) == total_num_of_nodes_each_course:
                        start_node_on_course = course_nodes[0]
                        wale_id = node_to_course_and_wale[start_node_on_course][1]
                        if (course_id+1, wale_id) in course_and_wale_to_node:
                            end_node = course_and_wale_to_node[(course_id+1, wale_id)]
                            if (source_node, end_node) in G1.edges:
                                visited_nodes.append(end_node)
                                reward += G1.edges[source_node, end_node]['weight']
                                source_node = end_node
                                continue
                            else:
                                print(f'edge {(source_node, end_node)} not in G1')
                        else:
                            print(f"no node in expected position to begin a new course, visited nodes so far is {visited_nodes}")
                            break
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
            G1.remove_nodes_from(node_to_delete)
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
        '''
        


        get_nodes_position()
        get_nodes_position()
        get_nodes_color()
        get_yarn_edges()
        get_stitch_edges()
        # path_result = find_shortest_path_for_tube(node_to_delete = [15, 16, 27, 28])
        draw_graph()


    if object_type == "tube":
        visualize_tube()
    elif object_type == 'sheet':
        visualize_sheet()
    elif object_type == 'pocket':
        visualize_pocket()

    
    