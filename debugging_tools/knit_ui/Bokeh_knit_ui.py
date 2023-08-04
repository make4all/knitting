from functools import partial

from knit_ui_wrapper import *
import holoviews as hv
import re
from bokeh.models.widgets import Button, TextInput, Select, NumericInput, CheckboxGroup, RadioButtonGroup, Toggle, \
    PreText, TextAreaInput
from bokeh.layouts import column, row
from bokeh.plotting import curdoc
import bokeh.events
from bokeh.layouts import widgetbox
from bokeh.models import CustomJS

hv.extension('bokeh')

# run the following command to launch notebook
# panel serve knit_ui.py --autoreload --show
# bokeh serve --show Bokeh_knit_ui.py

# if(type == "Sheet"):
#     all rs rows k. all ws rows p.
# else:
#     all rs rounds k. all ws rounds p.

plot = None
knit_graph = None
selected = [0]

# pattern type - button
pattern_type_options = ["Tube", "Sheet"]
pattern_type = RadioButtonGroup(name='Pattern Type', labels=pattern_type_options, active=0)

# knit speak - text input
# knit_speak = TextInput(title='Knit Speak', placeholder='Enter knit speak, e.g.: all rs rounds k. all ws rounds p.', height=300)
knit_speak = TextAreaInput(value = 'Enter knit speak, e.g.: all rs rounds k. all ws rounds p.', rows=15, cols=30, title='Knit Speak')

# knitting procedure - radio button
tube_knitting_procedure_options = ["Handle", "Pocket", "Hole", "Strap"]
sheet_knitting_procedure_options = ["Handle", "Pocket", "Hole"]
knitting_procedure = RadioButtonGroup(name='Knitting Procedure', labels=["Handle", "Pocket", "Hole", "Strap"], active=0)

# gauge - drop down
gauge_options = ["1/4", "1/3"]
gauge = Select(title='Gauge',
               options=gauge_options,
               value=gauge_options[0])

# yarn carrier - drop down
yarn_carrier_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
yarn_carrier_options_adjusted = ["2", "3", "4", "5", "6", "7", "8", "9", "10"]
yarn_carrier = Select(title='Yarn ID', options=yarn_carrier_options, value=yarn_carrier_options[0])

# graph height and width - int sliders
height = NumericInput(title='Height', low=1, value=1)
width = NumericInput(title='Width', low=1, value=1)

# create knit graph - button
create_knit_graph_button = Button(label='Create Knit Graph', button_type='primary')

# knit graph generation section
update_map_button = Button(label='Update Knit Graph', button_type='primary')
confirm_graph = Button(label='Confirm Graph', button_type='primary')
back_to_start = Button(label='Back', button_type='danger')

# TODO move these widget creations inside the create knit graph method -> allows widgets to re-update if user goes back

# hole modification
# hole_nodes = TextInput(title='Hole Nodes', placeholder='Node IDs to delete', width=320)
# hole_nodes_add_from_graph = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
# hole modification sheet
# hole_carrier = Select(title='Yarn ID', options=yarn_carrier_options_adjusted, value=yarn_carrier_options_adjusted[0])

# pocket modification (SHEET and TUBE)
left_keynodes_pocket = TextInput(title='Vertex Coordinates on Small Wale Side', placeholder='ex. (1,1), (2,2)')
pocket_left_add_from_graph = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
right_keynodes_pocket = TextInput(title='Vertex Coordinates on the Big Wale Side', placeholder='ex. (1,1), (2,2)')
pocket_right_add_from_graph = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
pocket_yarn_carrier_id = Select(title='Yarn ID for Pocket', options=yarn_carrier_options_adjusted, value=yarn_carrier_options_adjusted[0])
# is_front_patch_pocket = Toggle(label='Make Front Patch', active=False)
is_front_patch_pocket = Select(title='Patch on front', options=['True', 'False'], value='True')
close_top_pocket = Toggle(label='Close the Top', active=False)
confirm_tuples_pocket = Button(label='Confirm Vertices')
right_checkbox = CheckboxGroup(name='Big Wale Side Connections', inline=False)
left_checkbox = CheckboxGroup(name='Small Wale Side Connections', inline=False)

# handle modification (SHEET and TUBE)
handle_yarn_carrier_id = Select(title='Yarn ID for Handle', options=yarn_carrier_options_adjusted, value=yarn_carrier_options_adjusted[0])
# is_front_patch_handle = Toggle(label='Make Front Patch', active=False)
is_front_patch_handle = Select(title='Patch on front', options=['True', 'False'], value='True')
left_keynodes_handle = TextInput(title='Vertex Coordinates on Small Wale Side', placeholder='ex. (1,1), (2,2)')
handle_left_add_from_graph = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
right_keynodes_handle = TextInput(title='Vertex Coordinates on the Big Wale Side', placeholder='ex. (1,1), (2,2)')
handle_right_add_from_graph = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))

# strap modification (TUBE)
strap_height = NumericInput(title='Strap Height', low=1, value=1)
strap_front_1 = TextInput(title='Strap 1 Front', placeholder='ex. (1, 1)', width=160)
strap_back_1 = TextInput(title='Strap 1 Back', placeholder='(1, 1)', width=160)
strap_front_color_1 = Select(title='Yarn ID for Strap 1 Front', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[0])
strap_back_color_1 = Select(title='Yarn ID for Strap 1 Back', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[1])

strap_front_2 = TextInput(title='Strap 2 Front', placeholder='ex. (1, 1)', width=160)
strap_back_2 = TextInput(title='Strap 2 Back', placeholder='(1, 1)', width=160)
strap_front_color_2 = Select(title='Yarn ID for Strap 2 Front', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[0])
strap_back_color_2 = Select(title='Yarn ID for Strap 2 Back', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[1])

strap_front_3 = TextInput(title='Strap 3 Front', placeholder='ex. (1, 1)', width=160)
strap_back_3 = TextInput(title='Strap 3 Back', placeholder='(1, 1)', width=160)
strap_front_color_3 = Select(title='Yarn ID for Strap 3 Front', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[0])
strap_back_color_3 = Select(title='Yarn ID for Strap 3 Back', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[1])

strap_front_4 = TextInput(title='Strap 4 Front', placeholder='ex. (1, 1)', width=160)
strap_back_4 = TextInput(title='Strap 4 Back', placeholder='(1, 1)', width=160)
strap_front_color_4 = Select(title='Yarn ID for Strap 4 Front', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[0])
strap_back_color_4 = Select(title='Yarn ID for Strap 4 Back', options=yarn_carrier_options_adjusted, width=160, value=yarn_carrier_options_adjusted[1])

# after the updated graph has been generated
back_to_graph = Button(label='Back', button_type='danger')

# confirmation and download section
filename_input = TextInput(title='Knit-Out File Name', placeholder='Enter file name for knit out (no extension)')
confirm_filename = Button(label='Confirm Knit Out File Name')

# widget sections
widget1 = widgetbox(pattern_type, knit_speak, knitting_procedure, gauge,
                    yarn_carrier, height, width, create_knit_graph_button)
widget2 = widgetbox(back_to_start, update_map_button, confirm_graph)
widget3 = widgetbox(back_to_graph, confirm_graph)
widget4 = widgetbox(filename_input, confirm_filename, back_to_graph)


def _update_knit_procedures(attr, old, new):
    if new == 0:
        knitting_procedure.labels = tube_knitting_procedure_options
    elif new == 1:
        knitting_procedure.labels = sheet_knitting_procedure_options

    knitting_procedure.active = 0

pattern_type.on_change("active", _update_knit_procedures)

def _update_yarn_carrier(attr, old, new):
    yarn_carrier_options_adjusted.insert(int(old) - 1, old)
    yarn_carrier_options_adjusted.remove(new)
    pocket_yarn_carrier_id.options = yarn_carrier_options_adjusted
    pocket_yarn_carrier_id.value=yarn_carrier_options_adjusted[0]
    handle_yarn_carrier_id.options = yarn_carrier_options_adjusted
    handle_yarn_carrier_id.value=yarn_carrier_options_adjusted[0]
    strap_front_color_1.options = yarn_carrier_options_adjusted
    strap_front_color_2.options = yarn_carrier_options_adjusted
    strap_front_color_3.options = yarn_carrier_options_adjusted
    strap_front_color_4.options = yarn_carrier_options_adjusted
    strap_back_color_1.options = yarn_carrier_options_adjusted
    strap_back_color_2.options = yarn_carrier_options_adjusted
    strap_back_color_3.options = yarn_carrier_options_adjusted
    strap_back_color_4.options = yarn_carrier_options_adjusted
yarn_carrier.on_change("value", _update_yarn_carrier)


def _update_gauge(attr, old, new):
    gauge.options = ["1/4", "1/3", "1/2"]
    gauge.value = gauge_options[0]
    if (
            new == 0 or new == 1) and pattern_type.active == 0:  # if (new == "Handle" or new == "Pocket") and pattern_type.active == "Tube":
        gauge.options = ["1/4", "1/3"]
    elif new == 2 and pattern_type.active == 1:  # elif new == "Hole" and new == "Sheet":
        gauge.options = ["1/4", "1/3", "1/2", "1"]

knitting_procedure.on_change("active", _update_gauge)

def _update_patch_side(attr, old, new):
    xx

def _create_knit_graph(event):
    check_pattern_type = knit_speak.value.lower().split(" ")
    # print(f'check_pattern_type is {check_pattern_type}')
    if ("rounds" in check_pattern_type or "round" in check_pattern_type and pattern_type.active == 0) or (
            "rows" in check_pattern_type or 'row' in check_pattern_type and pattern_type.active == 1):  # 0 is Tube, 1 is Sheet
        curdoc().clear()
        final_type = knit_speak.value
        # try:
        gauge_map = {"1/4": 0.25, "1/3": 1 / 3, "1/2": 0.5, "1": 1}
        global knit_graph
        global plot
        plot, knit_graph = generate_initial_graph(final_type, gauge_map[gauge.value], int(yarn_carrier.value),
                                                  width.value, height.value,
                                                  "Tube" if pattern_type.active == 0 else "Sheet")

        column_widgets = column()
        # 0 is Handle, 1 is Pocket, 2 is Hole, 3 is Strap
        if knitting_procedure.active == 2:
            ###########################################################################
            # call back events
            def hole_nodes_button_clicked(event, i, textbox):
                selected[0] = 10 + i
                hole_selected_nodes = []
                add_holes_code = '''
                            if (selected[0] == 10 + s)
                            {
                                for (let i = 0; i < node.selected.indices.length; i++)
                                { 
                                    if (! selected_nodes.includes(node.selected.indices[i]))
                                        selected_nodes.push(node.selected.indices[i]);
                                }
                                
                                if (selected_nodes.length > 0)
                                {
                                    textbox.value = '' + selected_nodes[0];
                                    for (let i = 1; i < selected_nodes.length; i++)
                                        textbox.value = textbox.value + ',' + selected_nodes[i];
                                }
                            }
                            '''
                add_holes_callback = CustomJS(
                     args={'node': plot.renderers[-1].node_renderer.data_source, 'textbox': textbox, 'selected': selected, 'selected_nodes': hole_selected_nodes, 's': i},
                     code=add_holes_code)
                # #plot.js_on_event(bokeh.events.SelectionGeometry, add_holes_callback)
                plot.renderers[-1].node_renderer.data_source.selected.js_on_change('indices', add_holes_callback)


            ###########################################################################

            if pattern_type.active == 0:  # Hole on Tube
                hole_children = [widget2]
                for i in range(0, 10):
                    hole_index = TextInput(title='Hole Nodes', placeholder='Node IDs to delete', width=320)
                    hole_nodes_add_from_graph = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
                    hole_nodes_add_from_graph.on_event(bokeh.events.ButtonClick, partial(hole_nodes_button_clicked,bokeh.events.ButtonClick, i, hole_index))
                    hole_children.append(row(hole_index, hole_nodes_add_from_graph))

                column_widgets = column(children=hole_children)
            elif pattern_type.active == 1:  # Hole on Sheet
                hole_children = [widget2]
                for i in range(0, 10):
                    hole_index = TextInput(title='Hole Nodes', placeholder='Node IDs to delete', width=160)
                    hole_carrier = Select(title='Yarn ID', options=yarn_carrier_options_adjusted, value=yarn_carrier_options_adjusted[0], width=160)
                    hole_nodes_add_from_graph = Button(label='Add from graph', button_type='success', width=120,
                                                       margin=(24, 0, 0, 0))
                    hole_nodes_add_from_graph.on_event(bokeh.events.ButtonClick, partial(hole_nodes_button_clicked,bokeh.events.ButtonClick, i + 10, hole_index))
                    hole_children.append(row(hole_carrier, hole_index, hole_nodes_add_from_graph))

                column_widgets = column(children=hole_children)
        elif knitting_procedure.active == 1:
            ###########################################################################
            # call back events
            def pocket_left_button_clicked(event):
                selected[0] = 2
                pocket_left_selected_nodes = []
                pocket_left_code = '''
                           if (selected[0] == 2)
                           {
                                if (node.selected.indices.length > 0 && ! selected_nodes.includes(node.selected.indices[0]))
                                    selected_nodes.push(node.selected.indices[0]);
                                
                                if (selected_nodes.length > 0)
                                {
                                    let course = node.data['course'][selected_nodes[0]];
                                    let wale = node.data['wale'][selected_nodes[0]];

                                    //newly added to deal with gauging to avoid entangle        
                                    if (wale % parseInt(1/gauge) == 0)
                                    {
                                        textbox.value = '(' + course + ',' + (wale-2) + ')';
                                        is_front_patch_pocket.value = 'True';
                                    }
                                    else {
                                        textbox.value = '(' + course + ',' + (wale-1) + ')';
                                        is_front_patch_pocket.value = 'False';
                                    }
                                    //textbox.value = '(' + course + ',' + (wale-1) + ')';
                                    for (let i = 1; i < selected_nodes.length; i++)
                                    {
                                        let course = node.data['course'][selected_nodes[i]];
                                        let wale = node.data['wale'][selected_nodes[i]];

                                        //newly added to deal with gauging to avoid entangle
                                        if (wale % parseInt(1/gauge) == 0)
                                        {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-2) + ')';
                                        }
                                        else {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                        }

                                        //textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                    }
                                }
                           }
                                                              '''
                pocket_left_callback = CustomJS(
                    args={'node': plot.renderers[-1].node_renderer.data_source, 'textbox': left_keynodes_pocket,
                          'selected': selected, 'gauge': gauge_map[gauge.value], 'is_front_patch_pocket': is_front_patch_pocket, 'selected_nodes': pocket_left_selected_nodes},
                    code=pocket_left_code)
                plot.renderers[-1].node_renderer.data_source.selected.js_on_change('indices', pocket_left_callback)

            def pocket_right_button_clicked(event):
                selected[0] = 3
                pocket_right_selected_nodes = []
                pocket_right_code = '''
                           if (selected[0] == 3)
                           {
                                if (node.selected.indices.length > 0 && ! selected_nodes.includes(node.selected.indices[0]))
                                    selected_nodes.push(node.selected.indices[0]);
                                
                                if (selected_nodes.length > 0)
                                {
                                    let course = node.data['course'][selected_nodes[0]];
                                    let wale = node.data['wale'][selected_nodes[0]];
                                    
                                    //newly added to deal with gauging to avoid entangle        
                                    if (wale % parseInt(1/gauge) == 0)
                                    {
                                        textbox.value = '(' + course + ',' + (wale-2) + ')';
                                    }
                                    else {
                                        textbox.value = '(' + course + ',' + (wale-1) + ')';
                                    }
                                    //textbox.value = '(' + course + ',' + (wale-1) + ')';
                                    for (let i = 1; i < selected_nodes.length; i++)
                                    {
                                        let course = node.data['course'][selected_nodes[i]];
                                        let wale = node.data['wale'][selected_nodes[i]];

                                        //newly added to deal with gauging to avoid entangle
                                        if (wale % parseInt(1/gauge) == 0)
                                        {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-2) + ')';
                                        }
                                        else {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                        }
                                        
                                        //textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                    }
                                }
                           }
                                                              '''
                pocket_right_callback = CustomJS(
                    args={'node': plot.renderers[-1].node_renderer.data_source, 'textbox': right_keynodes_pocket,
                          'selected': selected, 'gauge': gauge_map[gauge.value], 'is_front_patch_pocket': is_front_patch_pocket, 'selected_nodes': pocket_right_selected_nodes},
                    code=pocket_right_code)
                plot.renderers[-1].node_renderer.data_source.selected.js_on_change('indices', pocket_right_callback)

            pocket_left_add_from_graph.on_event(bokeh.events.ButtonClick, pocket_left_button_clicked)
            pocket_right_add_from_graph.on_event(bokeh.events.ButtonClick, pocket_right_button_clicked)
            ###########################################################################
            pocket_widget_box = column(row(left_keynodes_pocket, pocket_left_add_from_graph), row(right_keynodes_pocket, pocket_right_add_from_graph), confirm_tuples_pocket,
                                          left_checkbox, right_checkbox, pocket_yarn_carrier_id,
                                          is_front_patch_pocket, close_top_pocket)
            column_widgets = column(widget2, pocket_widget_box)
        elif knitting_procedure.active == 0:
            ###########################################################################
            # call back events
            def handle_left_button_clicked(event):
                selected[0] = 4
                handle_left_selected_nodes = []
                handle_left_code = '''
                           if (selected[0] == 4)
                           {
                                if (node.selected.indices.length > 0 && ! selected_nodes.includes(node.selected.indices[0]))
                                    selected_nodes.push(node.selected.indices[0]);
                                
                                if (selected_nodes.length > 0)
                                {
                                    let course = node.data['course'][selected_nodes[0]];
                                    let wale = node.data['wale'][selected_nodes[0]];
                                    
                                    //newly added to deal with gauging to avoid entangle
                                    if (wale % parseInt(1/gauge) == 0)
                                    {
                                        textbox.value = '(' + course + ',' + (wale-2) + ')';
                                        is_front_patch_handle.value = 'True';
                                    }
                                    else {
                                        textbox.value = '(' + course + ',' + (wale-1) + ')';
                                        is_front_patch_handle.value = 'False';
                                    }
                                    
                                    //textbox.value = '(' + course + ',' + (wale-1) + ')';
                                    for (let i = 1; i < selected_nodes.length; i++)
                                    {
                                        let course = node.data['course'][selected_nodes[i]];
                                        let wale = node.data['wale'][selected_nodes[i]];
                                        
                                        //newly added to deal with gauging to avoid entangle
                                        if (wale % parseInt(1/gauge) == 0)
                                        {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-2) + ')';
                                        }
                                        else {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                        }
                                        
                                        //textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                    }
                                }
                           }
                                                   '''
                handle_left_callback = CustomJS(
                    args={'node': plot.renderers[-1].node_renderer.data_source, 'textbox': left_keynodes_handle,
                          'selected': selected, 'gauge': gauge_map[gauge.value], 'is_front_patch_handle': is_front_patch_handle, 'selected_nodes': handle_left_selected_nodes},
                    code=handle_left_code)
                plot.renderers[-1].node_renderer.data_source.selected.js_on_change('indices', handle_left_callback)

            def handle_right_button_clicked(event):
                selected[0] = 5
                handle_right_selected_nodes = []
                handle_right_code = '''
                           if (selected[0] == 5)
                           {
                                if (node.selected.indices.length > 0 && ! selected_nodes.includes(node.selected.indices[0]))
                                    selected_nodes.push(node.selected.indices[0]);
                                
                                if (selected_nodes.length > 0)
                                {
                                    let course = node.data['course'][selected_nodes[0]];
                                    let wale = node.data['wale'][selected_nodes[0]];

                                    //newly added to deal with gauging to avoid entangle        
                                    if (wale % parseInt(1/gauge) == 0)
                                    {
                                        textbox.value = '(' + course + ',' + (wale-2) + ')';
                                    }
                                    else {
                                        textbox.value = '(' + course + ',' + (wale-1) + ')';
                                    }

                                    //textbox.value = '(' + course + ',' + (wale-1) + ')';
                                    for (let i = 1; i < selected_nodes.length; i++)
                                    {
                                        let course = node.data['course'][selected_nodes[i]];
                                        let wale = node.data['wale'][selected_nodes[i]];
                                        
                                        //newly added to deal with gauging to avoid entangle
                                        if (wale % parseInt(1/gauge) == 0)
                                        {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-2) + ')';
                                        }
                                        else {
                                            textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                        }
                                        
                                        //textbox.value = textbox.value + ', ' + '(' + course + ',' + (wale-1) + ')';
                                    }
                                }
                           }
                                                   '''
                handle_right_callback = CustomJS(
                    args={'node': plot.renderers[-1].node_renderer.data_source, 'textbox': right_keynodes_handle,
                          'selected': selected, 'gauge': gauge_map[gauge.value], 'is_front_patch_handle': is_front_patch_handle, 'selected_nodes': handle_right_selected_nodes},
                    code=handle_right_code)
                plot.renderers[-1].node_renderer.data_source.selected.js_on_change('indices', handle_right_callback)

            handle_left_add_from_graph.on_event(bokeh.events.ButtonClick, handle_left_button_clicked)
            handle_right_add_from_graph.on_event(bokeh.events.ButtonClick, handle_right_button_clicked)
            ###########################################################################
            handle_widget_box = column(row(left_keynodes_handle, handle_left_add_from_graph), row(right_keynodes_handle, handle_right_add_from_graph),
                                          handle_yarn_carrier_id, is_front_patch_handle)
            column_widgets = column(widget2, handle_widget_box)
        elif knitting_procedure.active == 3:
            ###########################################################################
            # call back events
            def strap_button_clicked(event, i, textbox_front, textbox_back):
                selected[0] = 30 + i
                strap_selected_nodes = []
                strap_code = '''
                    if (selected[0] == s + 30)
                    {
                        if (node.selected.indices.length > 0 && ! selected_nodes.includes(node.selected.indices[0]))
                            selected_nodes.push(node.selected.indices[0]);
                        
                        if (selected_nodes.length > 0)
                        {
                            let course = node.data['course'][selected_nodes[0]];
                            let wale = node.data['wale'][selected_nodes[0]];
                            textbox_front.value = '(' + wale + ',';
                            if (selected_nodes.length > 1)
                            {
                                let course = node.data['course'][selected_nodes[1]];
                                let wale = node.data['wale'][selected_nodes[1]];
                                textbox_front.value += ' ' + wale + ')';
                            }
                        }
                        if (selected_nodes.length > 2)
                        {
                            let course = node.data['course'][selected_nodes[2]];
                            let wale = node.data['wale'][selected_nodes[2]];
                            textbox_back.value = '(' + wale + ',';
                            if (selected_nodes.length > 3)
                            {
                                let course = node.data['course'][selected_nodes[3]];
                                let wale = node.data['wale'][selected_nodes[3]];
                                textbox_back.value += ' ' + wale + ')';
                            }
                        }
                    }
                '''
                strap_callback = CustomJS(
                    args={'node': plot.renderers[-1].node_renderer.data_source, 'textbox_front': textbox_front, 'textbox_back': textbox_back,
                          'selected': selected, 'gauge': gauge_map[gauge.value],
                          'selected_nodes': strap_selected_nodes, 's': i},
                    code=strap_code)
                plot.renderers[-1].node_renderer.data_source.selected.js_on_change('indices', strap_callback)
            ###########################################################################
            strap_button_1 = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
            strap_button_2 = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
            strap_button_3 = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
            strap_button_4 = Button(label='Add from graph', button_type='success', width=120, margin=(24, 0, 0, 0))
            strap_button_1.on_event(bokeh.events.ButtonClick, partial(strap_button_clicked, bokeh.events.ButtonClick, 1, strap_front_1, strap_back_1))
            strap_button_2.on_event(bokeh.events.ButtonClick, partial(strap_button_clicked, bokeh.events.ButtonClick, 2, strap_front_2, strap_back_2))
            strap_button_3.on_event(bokeh.events.ButtonClick, partial(strap_button_clicked, bokeh.events.ButtonClick, 3, strap_front_3, strap_back_3))
            strap_button_4.on_event(bokeh.events.ButtonClick, partial(strap_button_clicked, bokeh.events.ButtonClick, 4, strap_front_4, strap_back_4))

            column_widgets = column(widget2, strap_height,
                                    row(strap_front_1, strap_back_1, strap_button_1), row(strap_front_color_1, strap_back_color_1),
                                    PreText(),
                                    row(strap_front_2, strap_back_2, strap_button_2), row(strap_front_color_2, strap_back_color_2),
                                    PreText(),
                                    row(strap_front_3, strap_back_3, strap_button_3), row(strap_front_color_3, strap_back_color_3),
                                    PreText(),
                                    row(strap_front_4, strap_back_4, strap_button_4), row(strap_front_color_4, strap_back_color_4))

        curdoc().add_root(row(column_widgets, plot))

        # HOW TO ACCESS ELEMENTS IN CURDOC()
        # print(curdoc().roots)
        # print(curdoc().roots[0])
        # print(curdoc().roots[0].children) # column_widgets, plot
        # print(curdoc().roots[0].children[0].children) # column_widgets children
        # print(curdoc().roots[0].children[0].children[1].children[0].value)

        # Todo - use PreText Widget to show the error message, but how do we append the error message?
        # except ErrorException as error:
        #     error = pn.pane.Alert(error.message)
        #     ui.append(error)
        #     ui.append(back1)
        # except AssertionError as error:
        #     error = pn.pane.Alert(str(error) + '\nPlease contact developers for more information')
        #     ui.append(error)
        #     ui.append(back1)
        # except:
        #     error = pn.pane.Alert('## Internal errors occurred.' + '\nPlease contact developers for more information')
        #     ui.append(error)
        #     ui.append(back1)
    else:
        # Todo
        pass
        # error = pn.pane.Alert('Knit speak entered does not match with pattern type')
        # ui.insert(0, error)


def _back_to_start(event):
    curdoc().clear()
    curdoc().add_root(widget1)


def _update_graph(event):
    global knit_graph
    final_plot = None
    final_knit_graph = None
    if knitting_procedure.active == 2:  # Hole
        holes = curdoc().roots[0].children[0].children
        if pattern_type.active == 0: # Tube
            complete_nodes_dict = []
            pattern = re.compile("^([0-9]*,)*[0-9]+$")

            for i in range(1, len(holes)):
                current = holes[i].children[0].value
                if pattern.match(current):
                    complete_nodes_dict.append([int(i) for i in current.split(",")])
                else:
                    pass
                    # Todo
                    # error = pn.pane.Alert('## Wrong Input Format\nExample Input Format for Hole Nodes: 1,2,3,4,5,6')
                    # ui.insert(0, error)

            if len(complete_nodes_dict) != 0:
                final_plot, final_knit_graph = generate_final_graph_hole(
                    "Tube" if pattern_type.active == 0 else "Sheet",
                    "Hole", complete_nodes_dict, knit_graph)
        elif pattern_type.active == 1: # Sheet
            complete_nodes_dict = {}
            pattern = re.compile("^([0-9]*,)*[0-9]+$")
            for i in range(1, len(holes)):

                current_hole = holes[i].children[1].value
                current_carrier = int(holes[i].children[0].value)

                if pattern.match(current_hole):
                    complete_nodes_dict.update({current_carrier: [int(i) for i in current_hole.split(",")]})
                else:
                    pass
                    # Todo
                    # error = pn.pane.Alert('## Wrong Input Format\nExample Input Format for Hole Nodes: 1,2,3,4,5,6')
                    # ui.insert(0, error)

            if len(complete_nodes_dict) != 0:
                final_plot, final_knit_graph = generate_final_graph_hole(
                    "Tube" if pattern_type.active == 0 else "Sheet",
                    "Hole", complete_nodes_dict, knit_graph)


    elif knitting_procedure.active == 1:  # pocket
        pattern = re.compile("^(\([0-9]+,[0-9]+\), )*\([0-9]+,[0-9]+\)$")
        if pattern.match(left_keynodes_pocket.value) and pattern.match(right_keynodes_pocket.value):
            left_vertices, right_vertices = parse_left_right_vertices(left_keynodes_pocket.value,
                                                                      right_keynodes_pocket.value)
            right_options = right_checkbox.labels
            left_options = left_checkbox.labels
            right_bools = []
            left_bools = []

            for i in range(0, len(right_options)):
                if i in right_checkbox.active:
                    right_bools.append(True)
                else:
                    right_bools.append(False)

            for i in range(0, len(left_options)):
                if i in left_checkbox.active:
                    left_bools.append(True)
                else:
                    left_bools.append(False)

            final_plot, final_knit_graph = generate_final_graph_pocket(
                "Tube" if pattern_type.active == 0 else "Sheet",
                "Pocket",
                int(yarn_carrier.value),
                int(pocket_yarn_carrier_id.value),
                knit_graph,
                is_front_patch_pocket.value == 'True',
                left_vertices,
                right_vertices,
                close_top_pocket.active, right_bools, left_bools) #is_front_patch_pocket.active
        else:
            # Todo
            pass
            # error = pn.pane.Alert(
            #     '## Wrong Input Format\nExample Input Format for Vertex Coordinates: (1,2), (3,4), (5,6)')
            # ui.insert(0, error)
    elif knitting_procedure.active == 0:  # Handle
        pattern = re.compile("^(\([0-9]+,[0-9]+\), )*\([0-9]+,[0-9]+\)$")
        if pattern.match(left_keynodes_handle.value) and pattern.match(right_keynodes_handle.value):
            left_vertices, right_vertices = parse_left_right_vertices(left_keynodes_handle.value,
                                                                      right_keynodes_handle.value)
            final_plot, final_knit_graph = generate_final_graph_handle(
                "Tube" if pattern_type.active == 0 else "Sheet",
                "Handle",
                int(yarn_carrier.value),
                int(handle_yarn_carrier_id.value), knit_graph,
                is_front_patch_handle.value == 'True', left_vertices,
                right_vertices) #is_front_patch_handle.active
        else:
            # Todo
            pass
            # error = pn.pane.Alert(
            #     '## Wrong Input Format\nExample Input Format for Vertex Coordinates: (1,2), (3,4), (5,6)')
            # ui.insert(0, error)

    elif knitting_procedure.active == 3:  # Strap
        strap_coor_info = {}
        pattern = re.compile("^\([0-9]+, [0-9]+\)$")

        def strap_coor_info_helper(strap_front, strap_back, strap_front_color, strap_back_color, strap_dict, pos):
            if pattern.match(strap_front.value) and pattern.match(strap_back.value):
                tup_front = strap_front.value.replace('(', '')
                tup_front = tup_front.replace(')', '')
                tup_back = strap_back.value.replace('(', '')
                tup_back = tup_back.replace(')', '')
                print(f'haha is {strap_front_color.value}')
                color_front = int(strap_front_color.value)
                color_back = int(strap_back_color.value)
                strap_dict.update({pos: {'front': [tuple(map(int, tup_front.split(', '))), color_front],
                                         'back': [tuple(map(int, tup_back.split(', '))), color_back]}})

        strap_coor_info_helper(strap_front_1, strap_back_1, strap_front_color_1, strap_back_color_1, strap_coor_info, 1)
        strap_coor_info_helper(strap_front_2, strap_back_2, strap_front_color_2, strap_back_color_2, strap_coor_info, 2)
        strap_coor_info_helper(strap_front_3, strap_back_3, strap_front_color_3, strap_back_color_3, strap_coor_info, 3)
        strap_coor_info_helper(strap_front_4, strap_back_4, strap_front_color_4, strap_back_color_4, strap_coor_info, 4)
        # else:
        # Todo
        # error = pn.pane.Alert(
        #     '## Wrong Input Format\nExample Input Format for Front or Back Vertex Coordinate: (1, 2)')
        # ui.insert(0, error)
        # strap_coor_info = {}
        # break

        if len(strap_coor_info) != 0:
            final_plot, final_knit_graph = generate_final_graph_strap("Tube",
                                                                      "Strap",
                                                                      int(yarn_carrier.value),
                                                                      int(strap_height.value),
                                                                      knit_graph,
                                                                      strap_coor_info)

    curdoc().clear()
    curdoc().add_root(row(widget3, final_plot))
    knit_graph = final_knit_graph

    # Todo
    # except ErrorException as error:
    #     error = pn.pane.Alert(error.message)
    #     ui.insert(0, error)
    # except AssertionError as error:
    #     error = pn.pane.Alert(str(error) + '\nPlease contact developers for more information')
    #     ui.insert(0, error)
    # except:
    #     error = pn.pane.Alert('Internal errors occurred.' + '\nPlease contact developers for more information')
    #     ui.insert(0, error)


def _confirm_graph(event):
    curdoc().clear()
    curdoc().add_root(widget4)


def _confirm_file_name(event):
    global knit_graph
    generate_file(knit_graph, filename_input.value_input + '.k')
    confirm_filename.label = 'File successfully generated'


def _back_to_graph(event):
    _create_knit_graph(bokeh.events.ButtonClick)
    confirm_filename.label = 'Confirm Knit Out File Name'


def _confirm_tuples(event):
    left_vertices, right_vertices = parse_left_right_vertices(left_keynodes_pocket.value, right_keynodes_pocket.value)
    right_options = []
    left_options = []
    for i in range(0, len(right_vertices) - 1):
        right_options.append("Connect " + str(right_vertices[i]) + " and " + str(right_vertices[i + 1]))

    for i in range(0, len(left_vertices) - 1):
        left_options.append("Connect " + str(left_vertices[i]) + " and " + str(left_vertices[i + 1]))

    if right_options != [] and left_options != [] and (
            left_options != left_checkbox.labels or right_options != right_checkbox.labels):
        # Todo
        # if left_checkbox.labels:
        #     ui.pop(len(ui) - 2)
        # if right_checkbox.labels:
        #     ui.pop(len(ui) - 1)

        left_checkbox.labels = left_options
        right_checkbox.labels = right_options


def parse_left_right_vertices(left_string, right_string):
    left_vertices = []
    right_vertices = []

    left_split = left_string.split(", ")
    right_split = right_string.split(", ")
    for i in range(0, len(left_split)):
        tuple_l = left_split[i].replace('(', '')
        tuple_l = tuple_l.replace(')', '')
        left_vertices.append(tuple(map(int, tuple_l.split(','))))
    for i in range(0, len(right_split)):
        tuple_r = right_split[i].replace('(', '')
        tuple_r = tuple_r.replace(')', '')
        right_vertices.append(tuple(map(int, tuple_r.split(','))))

    return left_vertices, right_vertices


create_knit_graph_button.on_click(_create_knit_graph)
back_to_start.on_click(_back_to_start)
update_map_button.on_click(_update_graph)
confirm_graph.on_click(_confirm_graph)
back_to_graph.on_click(_back_to_graph)
confirm_filename.on_click(_confirm_file_name)
confirm_tuples_pocket.on_click(_confirm_tuples)

curdoc().add_root(widget1)