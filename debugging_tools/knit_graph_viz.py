"""A method for visualizing KnitGraphs as a graph structure, mostly for debugging"""
from typing import Optional
from pyvis import network as nw
import networkx as nx
from knit_graphs.Knit_Graph import Knit_Graph
import matplotlib.pyplot as plt


def visualize_knitGraph(knit_graph: Knit_Graph, display_name: str = "nx.html", height: float = 750, width: float = 1000, is_tube: bool = False, indicator: Optional[int] = 0, hole_end_wale: Optional[int] = 0):
    """
    Runs an html file in browser to visualize the given knitgraph
    :param display_name: The html file name to display from
    :param knit_graph: the knit graph to visualize
    :param height: the height of the html window
    :param width: the width of the html window
    """
    # G = nx.DiGraph()
    network = nw.Network(f'{height}px', f'{width}px', layout=True, directed=True)
    network.toggle_physics(True)
    network.options.layout.hierarchical.enabled = True
    network.options.layout.hierarchical.direction = "LR"  # make the stitches start at the bottom
    # LR, RL, UD, DU
    network.options.layout.hierarchical.sortMethod = "hubsize"  # "hubsize" # "directed"
    # network.options.layout.hierarchical.blockShifting = False
    network.options.layout.hierarchical.edgeMinimization = True
    # network.options.layout.hierarchical.parentCentralization = False
    loop_ids_to_course, course_to_loop_ids = knit_graph.get_courses()
    # print('course_to_loop_ids', course_to_loop_ids)
    # print('knit_graph.graph.nodes', knit_graph.graph.nodes)
    # knit_graph.deprecated_get_course()
    loop_ids_row_index = {}
    loops_in_first_course = course_to_loop_ids[0]
    for loop_id in loops_in_first_course:
        loop_ids_row_index[loop_id] = loops_in_first_course.index(loop_id)
    # print(loop_ids_row_index)
    nodes_to_levels = {}
    nodes_to_positions = {} 
    #we assume different carrier carry yarns of differnt color, though practically they can be the same.
    carrier_id_to_color = {1:'black', 2:'skyblue', 3:'orange', 4:'green', 5: 'yellow', 6:'blue', 7: 'pink', 8: 'purple', 9:'cyan', 10:'red'}
    alpha_front = 1
    alpha_back = 0.5
    front_side_x_pos = []
    node_color_property = {}
    edge_color_property = {}
    yarns = [*knit_graph.yarns.values()]
    # print('yarns',yarns)
    assert hole_end_wale != 0, f'invalid hole_end_wale'
    x=-1
    y=-1
    d1, d2, d3, d4 = 0, 0, 0, 1
    row_length = len(loops_in_first_course)
    hole_height = [len(row)<row_length for row in [*course_to_loop_ids.values()]].count(True)
    hole_width = row_length - min([len(value) for key, value in course_to_loop_ids.items()])
    tube_width = int(len(course_to_loop_ids[0])/2) 
    #visualization for tube
    if is_tube:
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
        # print('no_parent_loop_index', no_parent_loop_index)
        # print(hole_height, hole_width, no_parent_loop_index)
        backside_level = []
        for node in knit_graph.graph.nodes:
            nodes_to_positions[node] = {}
            node_color_property[node] = {}
            course = loop_ids_to_course[node]
            parent_ids = [*knit_graph.graph.predecessors(node)]
            if len(parent_ids) == 0:
                if course == 0:
                    if loop_ids_row_index[node] <= tube_width - 1:
                        level = loop_ids_row_index[node]
                        x+=0.5
                        backside_level.append(level)  
                        front_side_x_pos.append(x)
                    else:
                        # level = tube_width*2 - 1 - loop_ids_row_index[node]- 0.5
                        level = tube_width*2 - 1 - loop_ids_row_index[node] + 0.5
                        x = nodes_to_positions[tube_width*2 - 1 - loop_ids_row_index[node]]['x'] + 0.1
                        y = -1 + 0.4
                elif course != 0:
                    if indicator == 1:
                        if hole_height % 2 == 0:
                            level = nodes_to_levels[no_parent_loop_index]
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*d4
                            no_parent_loop_index -= 1
                        elif hole_height % 2 == 1:
                            level = nodes_to_levels[no_parent_loop_index]
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*d4
                            no_parent_loop_index += 1
                    elif indicator == 2:
                        if hole_height % 2 == 0:
                            level  = nodes_to_levels[no_parent_loop_index]
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*d4
                            no_parent_loop_index += 1
                        elif hole_height % 2 == 1:
                            level = nodes_to_levels[no_parent_loop_index]
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*d4
                            no_parent_loop_index -= 1
                    elif indicator == 3: # when indicator = 3, i.e., hole in between
                        if hole_height % 2 == 0 or hole_end_wale == 2*tube_width - 1:
                            level = nodes_to_levels[no_parent_loop_index]
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*d4
                            no_parent_loop_index -= 1
                        else:
                            level = nodes_to_levels[no_parent_loop_index]
                            x = nodes_to_positions[no_parent_loop_index]['x']
                            y = nodes_to_positions[no_parent_loop_index]['y'] + (course)*d4
                            no_parent_loop_index += 1
            else:
                for parent_id in parent_ids:
                    parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
                    # print('parent_offset', parent_id, parent_offset)
                    parent_level = nodes_to_levels[parent_id]
                    # print('parent_level', parent_level)
                    level = parent_level - parent_offset
                    # print('level', parent_id, level)
                    x = nodes_to_positions[parent_id]['x']
                    y = nodes_to_positions[parent_id]['y'] + d4
                    break
            #find carrier_id of the node
            #first identify the yarn of the node
            for yarn in yarns:
                if node in yarn:
                    # print('yarn.carrier()', type(yarn.carrier), yarn.carrier, type(yarn.carrier.carrier_ids), yarn.carrier.carrier_ids)
                    carrier_id = yarn.carrier.carrier_ids
            nodes_to_positions[node]['x'] = x
            nodes_to_positions[node]['y'] = y
            node_color_property[node]['color'] = carrier_id_to_color[carrier_id]
            node_color_property[node]['alpha'] = alpha_front if nodes_to_positions[node]['x'] in front_side_x_pos else alpha_back
            #use level to locate
            # network.add_node(node, label=str(node), value=node, shape="circle", level=level, physics=True) 
            #use x and y coordinate to locate
            # network.add_node(node, label=str(node), value=node, shape="circle", x = nodes_to_positions[node]['x'], y = nodes_to_positions[node]['y'], physics=True)
            nodes_to_levels[node] = level
        # print('nodes_to_levels', nodes_to_levels)
        # print('nodes_to_positions', nodes_to_positions)
        # print('node_color_property', node_color_property)

    #visualization for non-tube
    else:
        prior_level = -1
        nodes_to_levels = {}
        for node in knit_graph.graph.nodes:
            course = loop_ids_to_course[node]
            parent_ids = [*knit_graph.graph.predecessors(node)]
            print(parent_ids)
            level = -1
            if len(parent_ids) == 0:
                if course % 2 == 0:
                    level = prior_level + 1
                else:
                    level = prior_level - 1
            else:
                for parent_id in parent_ids:
                    parent_offset = knit_graph.graph[parent_id][node]["parent_offset"]
                    # print('parent_offset', parent_id, parent_offset)
                    parent_level = nodes_to_levels[parent_id]
                    # print('parent_level', parent_level)
                    level = parent_level - parent_offset
                    # print('level', parent_id, level)
                    break
            network.add_node(node, label=str(node), value=node, shape="circle", level=level, physics=True)
            nodes_to_levels[node] = level
            prior_level = level 

    #add yarn edges
    for yarn in yarns:
        # print('yarn.yarn_id', yarn.yarn_id)
        for prior_node, next_node in yarn.yarn_graph.edges:
            edge_color_property[(prior_node, next_node)] = {}
            carrier_id = yarn.carrier.carrier_ids
            edge_color_property[(prior_node, next_node)]['color'] = carrier_id_to_color[carrier_id]
            #As long as either node on the edge is on the front, then the edge is regarded as on the front and will be colored brighter
            edge_color_property[(prior_node, next_node)]['alpha'] = alpha_front if nodes_to_positions[prior_node]['x'] in front_side_x_pos and nodes_to_positions[next_node]['x'] in front_side_x_pos else alpha_back
            # print('prior_node, next_node', (prior_node, next_node), carrier_id_to_color[carrier_id])
    #add stitch edges
    for parent_id, child_id in knit_graph.graph.edges:
        edge_color_property[(parent_id, child_id)] = {}
        for yarn in yarns:
            if child_id in yarn:
                carrier_id = yarn.carrier.carrier_ids
        edge_color_property[(parent_id, child_id)]['color'] = carrier_id_to_color[carrier_id]
        edge_color_property[(parent_id, child_id)]['alpha'] = alpha_front if nodes_to_positions[parent_id]['x'] in front_side_x_pos and nodes_to_positions[child_id]['x'] in front_side_x_pos else alpha_back
    # print('edge_color_property', edge_color_property, len(edge_color_property))
    
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
    #draw labels
    labels = {x: x for x in G.nodes}
    # nx.draw_networkx_labels(G, pos, labels, font_size=12, font_color='w')
    #draw edges
    for edge in [*edge_color_property.keys()]:
        nx.draw_networkx_edges(G, pos, edgelist=[edge], width=5.0, edge_color=edge_color_property[edge]['color'], style='solid', alpha=edge_color_property[edge]['alpha'])
    
    plt.show()
    '''
    #visualiza yarn edges        
    all_yarn_edges = {}
    print('knit_graph.yarns.values()', knit_graph.yarns.values())
    for yarn in knit_graph.yarns.values():
        print('yarn.yarn_id', yarn.yarn_id)
        color = 'red' if yarn.yarn_id == 'yarn' else 'green'
        all_yarn_edges[yarn] = yarn.yarn_graph.edges
        print('yarn.yarn_graph.edges', yarn.yarn_graph.edges)
        for prior_node, next_node in yarn.yarn_graph.edges:
            network.add_edge(prior_node, next_node, arrow="middle", physics=True, color=color)
    print('all_yarn_edges', all_yarn_edges)

    #visualize stitch edeges
    print('knit_graph.graph.edges', knit_graph.graph.edges)
    for parent_id, child_id in knit_graph.graph.edges:
        direction = knit_graph.graph[parent_id][child_id]["pull_direction"]
        depth = knit_graph.graph[parent_id][child_id]["depth"]
        # color = "blue"
        color = 'grey' if nodes_to_levels[parent_id] in backside_level else 'black'
        if depth < 0:
            color = "purple"
        elif depth > 0:
            color = "green"
        network.add_edge(parent_id, child_id, arrows="middle", color=color, label=direction.value, physics=True)
    #     # network.add_edge(parent_id, child_id, arrows="middle", color=color, label=direction.value, physics=True)
    # # network.set_edge_smooth(smooth_type='horizontal')
    network.show_buttons()  # turn on to show different control windows, see pyVis documentation
    network.show(display_name)
    '''
