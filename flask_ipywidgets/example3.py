import datetime
import time
from threading import Thread

from flask import render_template
import flask_ipywidgets

app = flask_ipywidgets.app()

from ipywidgets import FloatSlider, Text, VBox, Label, HBox


"""

Example demonstrating pushing values to a `ipywidget`

"""



s = FloatSlider(min=0.01, max=0.5, value=0.3, step=0.01)
t = Text()

l = Label("update every text box every {}".format(s.value))


def update_text(change=None):
    t.value = str(float(s.value) ** 2)


def push_update_text():
    while True:
        time.sleep(s.value)
        t.value = str(datetime.datetime.now())
        l.value = "update every text box every {}".format(s.value)


s.observe(update_text, names='value')
update_text()
h_box = HBox([l, s])
vbox = VBox([h_box, t])

thread = Thread(target=push_update_text)
thread.daemon = True
thread.start()


@app.route('/')
def index():
    return render_template('example2.html', widget=vbox, widgets=vbox)


if __name__ == "__main__":
    flask_ipywidgets.main_factory(app)()