import panel as pn
pn.extension()
# --- run the following command to launch notebook ---
# panel serve panel_test.py --autoreload --show
ui = pn.Column()

text = pn.widgets.TextInput(value='Ready')

def b(event):
    text.value = 'Clicked {0} times'.format(button.clicks)

button = pn.widgets.Button(name='Click me', button_type='primary')


button.on_click(b)
pn.Row(button, text)

ui.append(pn.Row(button, text))
ui.servable()