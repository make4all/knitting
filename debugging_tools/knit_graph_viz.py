"""A method for visualizing KnitGraphs as a graph structure, mostly for debugging"""
from typing import Optional
from pyvis import network as nw
import networkx as nx
from knit_graphs.Knit_Graph import Knit_Graph
import matplotlib.pyplot as plt


def visualize_knitGraph(knit_graph: Knit_Graph, is_tube: bool = False, indicator: Optional[int] = 0, hole_end_wale: Optional[int] = 0):
    """
    Runs an html file in browser to visualize the given knitgraph
    :param display_name: The html file name to display from
    :param knit_graph: the knit graph to visualize
    :param height: the height of the html window
    :param width: the width of the html window
    """
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    # print('course_to_loop_ids', course_to_loop_ids)
    # print('knit_graph.graph.nodes', knit_graph.graph.nodes)
    # knit_graph.deprecated_get_course()
    loop_ids_row_index = {}
    loops_in_first_course = course_to_loop_ids[0]
    for loop_id in loops_in_first_course:
        loop_ids_row_index[loop_id] = loops_in_first_course.index(loop_id)
    nodes_to_positions = {} 
    #we assume different carrier carry yarns of differnt color, though practically they can be the same.
    carrier_id_to_color = {1:'black', 2:'skyblue', 3:'orange', 4:'green', 5: 'yellow', 6:'blue', 7: 'pink', 8: 'purple', 9:'cyan', 10:'red'}
    cable_depth_to_color = {1:'grey', -1:'magenta'}
    alpha_front = 1
    alpha_back = 0.5
    front_side_x_pos = []
    node_color_property = {}
    edge_color_property = {}
    stitch_labels = {}
    yarns = [*knit_graph.yarns.values()]
    x = 0
    y0 = y = 0
    h_back2front, w_back2front, w_between_node, h_course = 0.4, 0.1, 0.5, 1
    row_length = len(loops_in_first_course)
    hole_height = [len(row)<row_length for row in [*course_to_loop_ids.values()]].count(True)
    hole_width = row_length - min([len(value) for key, value in course_to_loop_ids.items()])
    tube_width = int(len(course_to_loop_ids[0])/2) 

    #visualization for non-tube/sheets
    def visualize_sheet():
        x = 0
        y0 = y = 0
        for node in knit_graph.graph.nodes:
            nodes_to_positions[node] = {}
            node_color_property[node] = {}
            course = loop_ids_to_course[node]
            parent_ids = [*knit_graph.graph.predecessors(node)]
            if len(parent_ids) == 0:
                if course % 2 == 0:
                    x += w_between_node
                else:
                    x -= w_between_node
            else:
                for parent_id in parent_ids:
                    parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
                    original_parent_id = parent_id - parent_offset
                    parent_course = loop_ids_to_course[parent_id]
                    x = nodes_to_positions[original_parent_id]['x']
                    # To better express shaping effect, use below one
                    y = nodes_to_positions[original_parent_id]['y'] + h_course
                    # To avoid visual confusion, use below one to locate node
                    # y = nodes_to_positions[original_parent_id]['y'] + (course - parent_course)*h_course
                    break
            #find carrier_id of the node
            #first identify the yarn of the node
            for yarn in yarns:
                if node in yarn:
                    carrier_id = yarn.carrier.carrier_ids
            #store node position and color property
            nodes_to_positions[node]['x'] = x
            nodes_to_positions[node]['y'] = y
            node_color_property[node]['color'] = carrier_id_to_color[carrier_id]
        
        #add yarn edges
        for yarn in yarns:
            for prior_node, next_node in yarn.yarn_graph.edges:
                edge_color_property[(prior_node, next_node)] = {}
                carrier_id = yarn.carrier.carrier_ids
                edge_color_property[(prior_node, next_node)]['color'] = carrier_id_to_color[carrier_id]
               
        #add stitch edges and create edge labels
        for parent_id, child_id in knit_graph.graph.edges:
            edge_color_property[(parent_id, child_id)] = {}
            stitch_labels[(parent_id, child_id)] = knit_graph.graph[parent_id][child_id]["pull_direction"]
            for yarn in yarns:
                if child_id in yarn:
                    carrier_id = yarn.carrier.carrier_ids
                    edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
                    break
            if knit_graph.graph[parent_id][child_id]["depth"] < 0:
                depth = -1
                edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
            elif knit_graph.graph[parent_id][child_id]["depth"] > 0:
                depth = 1
                edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]

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

    #visualization for tube
    def visualize_tube():
        x = 0
        y0 = y = 0
        if indicator != 0: # that means there is a hole on tube, otherwise the tube is a complete tube, so no need to care about the below assertion
            assert hole_end_wale != 0, f'invalid hole_end_wale'
        if indicator == 1:
            if hole_height % 2 == 0:
                no_parent_loop_index = hole_width - 1
            elif hole_height % 2 == 1:
                no_parent_loop_index = 0
        elif indicator == 2:
            if hole_height % 2 == 0:
                no_parent_loop_index = row_length - hole_width
            elif hole_height % 2 == 1:
                no_parent_loop_index = row_length - 1
        elif indicator == 3:
            if hole_height % 2 == 0 or hole_end_wale == 2*tube_width - 1:
                no_parent_loop_index = hole_end_wale - 1
            else:
                no_parent_loop_index = hole_end_wale - hole_width
        
        for node in knit_graph.graph.nodes:
            nodes_to_positions[node] = {}
            node_color_property[node] = {}
            course = loop_ids_to_course[node]
            parent_ids = [*knit_graph.graph.predecessors(node)]
            if len(parent_ids) == 0:
                if course == 0:
                    if loop_ids_row_index[node] <= tube_width - 1:
                        x += w_between_node
                        y = y0
                        front_side_x_pos.append(x)
                    else:
                        # level = tube_width*2 - 1 - loop_ids_row_index[node]- 0.5
                        x = nodes_to_positions[tube_width*2 - 1 - loop_ids_row_index[node]]['x'] + w_back2front
                        y = y0 + h_back2front
                elif course != 0:
                    if indicator == 1:
                        if hole_height % 2 == 0:
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*h_course
                            no_parent_loop_index -= 1
                        elif hole_height % 2 == 1:
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*h_course
                            no_parent_loop_index += 1
                    elif indicator == 2:
                        if hole_height % 2 == 0:
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*h_course
                            no_parent_loop_index += 1
                        elif hole_height % 2 == 1:
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*h_course
                            no_parent_loop_index -= 1
                    elif indicator == 3: # when indicator = 3, i.e., hole in between
                        if hole_height % 2 == 0 or hole_end_wale == 2*tube_width - 1:
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*h_course
                            no_parent_loop_index -= 1
                        else:
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*h_course
                            no_parent_loop_index += 1
            else:
                for parent_id in parent_ids:
                    parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
                    original_parent_id = parent_id - parent_offset
                    x = nodes_to_positions[original_parent_id]['x']
                    y = nodes_to_positions[original_parent_id]['y'] + h_course
                    break
            #find carrier_id of the node
            #first identify the yarn of the node
            for yarn in yarns:
                if node in yarn:
                    carrier_id = yarn.carrier.carrier_ids
            #store node position and color property
            nodes_to_positions[node]['x'] = x
            nodes_to_positions[node]['y'] = y
            node_color_property[node]['color'] = carrier_id_to_color[carrier_id]
            node_color_property[node]['alpha'] = alpha_front if nodes_to_positions[node]['x'] in front_side_x_pos else alpha_back
            #use level to locate
            # network.add_node(node, label=str(node), value=node, shape="circle", level=level, physics=True) 
            #try to use x and y coordinate to locate but won't work
            # network.add_node(node, label=str(node), value=node, shape="circle", x = nodes_to_positions[node]['x'], y = nodes_to_positions[node]['y'], physics=True)
        
        #add yarn edges
        for yarn in yarns:
            for prior_node, next_node in yarn.yarn_graph.edges:
                edge_color_property[(prior_node, next_node)] = {}
                carrier_id = yarn.carrier.carrier_ids
                edge_color_property[(prior_node, next_node)]['color'] = carrier_id_to_color[carrier_id]
                #As long as either node on the edge is on the front, then the edge is regarded as on the front and will be colored brighter
                edge_color_property[(prior_node, next_node)]['alpha'] = alpha_front if nodes_to_positions[prior_node]['x'] in front_side_x_pos and nodes_to_positions[next_node]['x'] in front_side_x_pos else alpha_back
        
        #add stitch edges and create edge labels
        for parent_id, child_id in knit_graph.graph.edges:
            edge_color_property[(parent_id, child_id)] = {}
            edge_color_property[(parent_id, child_id)]['alpha'] = alpha_front if nodes_to_positions[parent_id]['x'] in front_side_x_pos and nodes_to_positions[child_id]['x'] in front_side_x_pos else alpha_back
            stitch_labels[(parent_id, child_id)] = knit_graph.graph[parent_id][child_id]["pull_direction"]
            for yarn in yarns:
                if child_id in yarn:
                    carrier_id = yarn.carrier.carrier_ids
                    edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
                    break
            if knit_graph.graph[parent_id][child_id]["depth"] < 0:
                depth = -1
                edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
            elif knit_graph.graph[parent_id][child_id]["depth"] > 0:
                depth = 1
                edge_color_property[(parent_id, child_id)]['color'] = cable_depth_to_color[depth]
        
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

    if is_tube == True:
        visualize_tube()
    else:
        visualize_sheet()
    
    