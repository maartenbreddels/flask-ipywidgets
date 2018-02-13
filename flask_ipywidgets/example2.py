from flask import render_template
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
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
