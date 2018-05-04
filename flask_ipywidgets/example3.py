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

l = Label(f"update every text box every {s.value}")


def update_text(change=None):
    t.value = str(float(s.value) ** 2)


def push_update_text():
    while True:
        time.sleep(s.value)
        t.value = str(datetime.datetime.now())
        l.value = f"update every text box every {s.value}"


s.observe(update_text, names='value')
update_text()
h_box = HBox([l, s])
vbox = VBox([h_box, t])

thread = Thread(target=push_update_text)
thread.start()


@app.route('/')
def index():
    return render_template('example2.html', widget=vbox, widgets=vbox)


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
