"""A method for visualizing KnitGraphs as a graph structure, mostly for debugging"""
from turtle import distance
from typing import Optional, Dict, List, Union, Tuple
import networkx as nx
from knit_graphs.Knit_Graph import Knit_Graph
from knit_graphs.Yarn import Yarn #just for the draw_rebulit_graph(), which we afterwards will move to New_Hole_Generator Module
import matplotlib.pyplot as plt


def visualize_knitGraph(knit_graph: Knit_Graph, unmodified: bool = True, is_polygon: bool = False, object_type: str = 'sheet', yarn_start_direction: str = 'left to right', node_to_course_and_wale: Optional[Dict[int, Tuple[int, int]]] = None, node_on_front_or_back: Optional[Dict[int, str]] = None):
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
    # 
    course_and_wale_and_bed_to_node = {}
    for node in node_on_front_or_back.keys():
        course_and_wale = node_to_course_and_wale[node]
        front_or_back = node_on_front_or_back[node]
        course_and_wale_and_bed_to_node[(course_and_wale, front_or_back)] = node
    print('loop_ids_to_wale in viz', loop_ids_to_wale)
    print('wale_to_loop_ids in viz', wale_to_loop_ids)
    print('course_to_loop_ids in viz', course_to_loop_ids)
    print('node_to_course_and_wale viz', node_to_course_and_wale)
    print('course_and_wale_to_node viz', course_and_wale_to_node)
    print('course_and_wale_and_bed_to_node viz', course_and_wale_and_bed_to_node)
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
    if object_type == 'tube':
        assert len(course_to_loop_ids[0])%2 == 0, f"the number of loops in first course should be an even number"
        # if not include float as width, use the below one
        # tube_bottom_width = int(len(course_to_loop_ids[0])/2) 
        # print(f'tube_bottom_width is {tube_bottom_width}')
        # if float caused by smaller gauge is considered as tube bottom width, then use below one, i.e. the wale id of the last node on the first course
        last_node_on_first_course = course_to_loop_ids[0][-1]
        tube_bottom_width = node_to_course_and_wale[last_node_on_first_course][1]
        # print(f'tube_bottom_width is {tube_bottom_width}')



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

        get_nodes_position()
        get_nodes_color()
        get_yarn_edges()
        get_stitch_edges()
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
            max_wale_id = max(node_to_course_and_wale.values(), key = lambda k: k[1])[1]
            # print(f'len(course_to_loop_ids[0])/2 is {len(course_to_loop_ids[0])/2 - 1}')
            # print(f'course_to_loop_ids[0] is {course_to_loop_ids[0]}')
            wale_id_to_define_back_and_front = node_to_course_and_wale[course_to_loop_ids[0][int(len(course_to_loop_ids[0])/2 - 1)]][1]
            # print(f'max_wale_id is {max_wale_id}')
            # print(f'wale_id_to_define_back_and_front is {wale_id_to_define_back_and_front}')
            for node in knit_graph.graph.nodes:
                nodes_to_positions[node] = {}
                node_color_property[node] = {}
                course = node_to_course_and_wale[node][0]
                wale = node_to_course_and_wale[node][1]
                if wale <= wale_id_to_define_back_and_front:
                    if yarn_start_direction == 'left to right':
                        nodes_to_positions[node]['x'] = x0 + wale * w_between_node       
                    elif yarn_start_direction == 'right to left':
                        nodes_to_positions[node]['x'] = x0 - wale * w_between_node
                    nodes_to_positions[node]['y'] = y0 + course * h_course
                    front_side_x_pos.append(nodes_to_positions[node]['x'])
                    # print(f'node is {node}, wale is {wale}')
                else:
                    # print(f'node is {node}, wale is {wale}, max_wale_id - wale is {max_wale_id - wale}')
                    # print(f'course_and_wale_to_node[(course, max_wale_id - wale)] is {course_and_wale_to_node[(0, max_wale_id - wale)]}')
                    nodes_to_positions[node]['x'] = nodes_to_positions[course_and_wale_to_node[(0, max_wale_id - wale)]]['x'] + w_back2front
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
    
        get_nodes_position()
        get_nodes_position()
        get_nodes_color()
        get_yarn_edges()
        get_stitch_edges()
        # path_result = find_shortest_path_for_tube(node_to_delete = [15, 16, 27, 28])
        draw_graph()

    #visualization for tube
    def updated_visualize_tube():
        #set node postion 
        def get_nodes_position():
            x0 = 0
            y0 = 0
            for node in knit_graph.graph.nodes:
                nodes_to_positions[node] = {}
                node_color_property[node] = {}
                course = node_to_course_and_wale[node][0]
                wale = node_to_course_and_wale[node][1]
                if yarn_start_direction == 'left to right':
                    nodes_to_positions[node]['x'] = x0 + wale * w_between_node       
                elif yarn_start_direction == 'right to left':
                    nodes_to_positions[node]['x'] = x0 - wale * w_between_node
                nodes_to_positions[node]['y'] = y0 + course * h_course
            for node in knit_graph.graph.nodes:
                if node_on_front_or_back[node] == 'b':
                    course = node_to_course_and_wale[node][0]
                    wale = node_to_course_and_wale[node][1]
                    if yarn_start_direction == 'left to right':
                        nodes_to_positions[node]['x'] = x0 + wale * w_between_node + w_back2front
                    elif yarn_start_direction == 'right to left':
                        nodes_to_positions[node]['x'] = x0 - wale * w_between_node + w_back2front
                    nodes_to_positions[node]['y'] = y0 + course * h_course + h_back2front
            print(f'nodes_to_positions is {nodes_to_positions}')
                
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

        get_nodes_position()
        get_nodes_color()
        get_yarn_edges()
        get_stitch_edges()
        draw_graph()

    
    if object_type == "tube":
        visualize_tube()
    elif object_type == "increased_tube":
        updated_visualize_tube()
    elif object_type == 'sheet':
        visualize_sheet()
    elif object_type == 'pocket':
        visualize_pocket()
    

    
    