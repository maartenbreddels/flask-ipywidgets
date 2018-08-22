from flask import render_template
import flask_ipywidgets
import traitlets

app = flask_ipywidgets.app()

def echo_state(*args):
    print('changes', args)


import ipywidgets
slider_shared = ipywidgets.FloatSlider(description='shared slider')
slider_shared.observe(echo_state, 'value')


@app.route('/')
def index():
    slider_private = ipywidgets.FloatSlider(value=2, description='private slider')
    traitlets.link((slider_shared, 'value'), (slider_private, 'value'))
    return render_template('example1.html', slider1=slider_private, slider2=slider_shared, widgets=[slider_private, slider_shared])


if __name__ == "__main__":
    flask_ipywidgets.main_factory(app)()
