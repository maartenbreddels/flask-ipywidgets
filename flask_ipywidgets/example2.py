from flask import Flask, render_template
import flask_ipywidgets


app = flask_ipywidgets.app()

from ipywidgets import IntSlider, Text, VBox
s = IntSlider(max=200, value=100)
t = Text()

def update_text(change=None):
    t.value = str(float(s.value) ** 2)

s.observe(update_text, names='value')
update_text()
vbox = VBox([s, t])


@app.route('/')
def index():
    return render_template('example2.html', widget=vbox, widgets=vbox)


if __name__ == "__main__":
    flask_ipywidgets.main_factory(app)()