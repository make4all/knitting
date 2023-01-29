from tests.test_knitspeak_compiler import generate_initial_graph
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
height = pn.widgets.IntSlider(name='Height', start=1, end=50, step=1, value=1)

width = pn.widgets.IntSlider(name='Width', start=1, end=50, step=1, value=1)

# create knit graph - button
create_knit_graph_button = pn.widgets.Button(name='Create Knit Graph', button_type='primary')

# knit graph generation section
nodes = pn.widgets.TextInput(name='Node Select', value='Enter a comma separated list of nodes')
update_map_button = pn.widgets.Button(name='Update Knit Graph', button_type='primary')
confirm_graph = pn.widgets.Button(name='Confirm Graph', button_type='primary')
back1 = pn.widgets.Button(name='Back', button_type='danger')

# confirmation and download section
file_download = pn.widgets.FileDownload(file='station_info.csv', filename='knit_graph.csv') # TODO update the filename
back2 = pn.widgets.Button(name='Back', button_type='danger')

# widget sections
widget1 = pn.WidgetBox('## Starter Selector', pattern_type, knitting_procedure, gauge,
                       yarn_carrier, height, width, create_knit_graph_button)
widget2 = pn.WidgetBox('## End Selector', nodes, back1, update_map_button, confirm_graph)
widget3 = pn.WidgetBox('## Export', back2, file_download)


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

    final_type = None

    type = pattern_type.value
    if(type == "Sheet"):
        final_type = "all rs rows k. all ws rows p."
    else:
        final_type = "all rs rounds k. all ws rounds p."

    g = gauge.value
    color = yarn_carrier.value
    graph = generate_initial_graph(final_type, .5, 2)
    html_pane = pn.pane.HTML(graph)
    row = pn.Row(widget2, html_pane)
    ui.append(row)


def _back_to_start(event):
    ui.clear()
    ui.append(widget1)


def _confirm_graph(event):
    # TODO get the knit speak and put it into a file download
    ui.clear()
    ui.append(widget3)


def _back_to_graph(event):
    ui.clear()
    ui.append(widget2)


create_knit_graph_button.on_click(_create_knit_graph)
back1.on_click(_back_to_start)
confirm_graph.on_click(_confirm_graph)
back2.on_click(_back_to_graph)

# ui
ui.append(widget1)
ui.servable()
