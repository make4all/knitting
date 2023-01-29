from tests.test_knitspeak_compiler import generate_initial_graph
from tests.test_knitspeak_compiler import generate_final_graph
from tests.test_knitspeak_compiler import generate_file
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import opts
import panel as pn
hv.extension('bokeh')
pn.extension('altair', 'tabulator')

# run the following command to launch notebook
# panel serve knit_ui.py --autoreload --show

ui = pn.Column()

knit_graph = None
html_graph = None


# pattern type - button
pattern_type_options = ["Tube", "Sheet"]
pattern_type = pn.widgets.RadioButtonGroup(name='Pattern Type',
                                           options=pattern_type_options,
                                           value=pattern_type_options[0])

# TODO eventually want to allow users to enter their own knit speak
knit_speak = pn.widgets.TextInput(name='Knit Speak', value='Enter knit speak')

# knitting procedure - radio button
tube_knitting_procedure_options = ["Handle", "Pocket", "Hole", "Strap"]
sheet_knitting_procedure_options = ["Handle", "Pocket", "Hole"]

knitting_procedure = pn.widgets.RadioButtonGroup(name='Knitting Procedure',
                                                 options=tube_knitting_procedure_options)

# gauge - drop down
gauge_options = ["1/4", "1/3", "1/2"]

gauge = pn.widgets.Select(name='Gauge',
                          options=gauge_options,
                          value=gauge_options[0],
                          disabled_options=["1/2"])

# yarn carrier - drop down
yarn_carrier_options = {"Black": 1, "Skyblue": 2, "Orange": 3, "Green": 4, "Yellow": 5, "Blue": 6, "Pink": 7, "Purple": 8, "Cyan": 9, "Red": 10}
yarn_carrier = pn.widgets.Select(name='Color', options=yarn_carrier_options)


# graph height and width - int sliders
height = pn.widgets.IntInput(name='Height')

width = pn.widgets.IntInput(name='Width')

# create knit graph - button
create_knit_graph_button = pn.widgets.Button(name='Create Knit Graph', button_type='primary')

# knit graph generation section
nodes = pn.widgets.TextInput(name='Node Select', value='Enter a comma separated list of nodes')

hole_index = pn.widgets.TextInput(name='Yarn ID to use', value='Integer starting from 1')
hole_nodes = pn.widgets.TextInput(name='Hole Nodes', value='Node IDs to delete for the hole')
more_hole = pn.widgets.Button(name='Add more holes')

update_map_button = pn.widgets.Button(name='Update Knit Graph', button_type='primary')
confirm_graph = pn.widgets.Button(name='Confirm Graph', button_type='primary')
back1 = pn.widgets.Button(name='Back', button_type='danger')

# confirmation and download section
filename_input = pn.widgets.TextInput(name='Knit Out File Name', value='Enter file name for knit out')
confirm_filename = pn.widgets.Button(name='Confirm Knit Out')
back2 = pn.widgets.Button(name='Back', button_type='danger')

# widget sections
widget1 = pn.WidgetBox('## Starter Selector', pattern_type, knit_speak, knitting_procedure, gauge,
                       yarn_carrier, height, width, create_knit_graph_button)

widget2 = pn.WidgetBox('## End Selector', back1, update_map_button, confirm_graph)
widget3 = pn.WidgetBox('## Export', filename_input, confirm_filename, back2)


@pn.depends(pattern_type.param.value, watch=True)
def _update_knitting_procedures(a):
    if a == "Tube":
        knitting_procedure.options = tube_knitting_procedure_options
    elif a == "Sheet":
        knitting_procedure.options = sheet_knitting_procedure_options


@pn.depends(knitting_procedure.param.value, pattern_type.param.value, watch=True)
def _update_gauge(a, b):
    gauge.value = gauge_options[0]
    gauge.disabled_options = []
    if a == "Handle" or a == "Pocket":
        gauge.disabled_options = ["1/2"]


# TODO on button clicks, hide and show different widget boxes -> doing something strange right now
def _create_knit_graph(event):
    ui.clear()

    final_type = knit_speak.value

    # if(type == "Sheet"):
    #     final_type = "all rs rows k. all ws rows p."
    # else:
    #     final_type = "all rs rounds k. all ws rounds p."

    g = gauge.value
    color = yarn_carrier.value
    try:
        gauge_map = {"1/4": 0.25, "1/3": 1/3, "1/2": 0.5}
        global html_graph
        global knit_graph
        html_graph, knit_graph = generate_initial_graph(final_type, gauge_map[gauge.value], int(yarn_carrier.value), width.value, height.value)
        html_pane = pn.pane.HTML(html_graph)
        row = pn.Row(widget2, html_pane)
        ui.append(row)

        if knitting_procedure.value == "Hole":
            holes = pn.Column(more_hole, pn.Row(hole_index, hole_nodes))
            ui.append(holes)
    except:
        error_widget = pn.widgets.StaticText(value='Starting width should be greater than or equal to total and a multiple of total')
        ui.append(error_widget)
        ui.append(back1)
    


def _back_to_start(event):
    ui.clear()
    ui.append(widget1)
    ui.append(widget2)


def _update_graph(event):
    # if knitting_procedure.value == "Hole" and pattern_type.value == "Sheet":
    map =  {int(hole_index.value): [int(i) for i in hole_nodes.value.split(",")]}
    print(f'nodes is {[int(i) for i in hole_nodes.value.split(",")]}')
    print(f'map is {map}')
    global html_graph
    global knit_graph
    final_html_graph, final_knit_graph = generate_final_graph(pattern_type.value, knitting_procedure.value, map, knit_graph)
    # ui.remove(html_graph)
    ui.append(final_html_graph)
    html_graph = final_html_graph
    knit_graph = final_knit_graph




def _more_hole(event):
    new_hole_index = pn.widgets.TextInput(name='Hole Index', value='Integer starting from 0')
    new_hole_nodes = pn.widgets.TextInput(name='Hole Nodes', value='Node IDs to delete for the hole')
    ui.append(pn.Row(new_hole_index, new_hole_nodes))



def _confirm_graph(event):
    # TODO get the knit speak and put it into a file download
    ui.clear()
    ui.append(widget3)


def _confirm_file_name(event):
    global knit_graph
    generate_file(knit_graph, filename_input.value + '.k')
    file_download = pn.widgets.FileDownload(file=filename_input.value + '.k', embed=True)
    ui.append(file_download)


def _back_to_graph(event):
    ui.clear()
    ui.append(widget2)


create_knit_graph_button.on_click(_create_knit_graph)
back1.on_click(_back_to_start)
update_map_button.on_click(_update_graph)
confirm_graph.on_click(_confirm_graph)
back2.on_click(_back_to_graph)
more_hole.on_click(_more_hole)
confirm_filename.on_click(_confirm_file_name)

# ui
ui.append(widget1)
ui.servable()
