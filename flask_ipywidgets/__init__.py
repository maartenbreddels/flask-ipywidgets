import json

from flask import Flask, Blueprint, send_from_directory, jsonify
from flask_sockets import Sockets

from .kernel import FlaskKernel, BytesWrap, WebsocketStreamWrapper

_kernel_spec = {
    "display_name": "flask_kernel",
    "language": "python",
    "argv": ["python", "doesnotworkthisway"],
    "env": {

    },
    "display_name": "Flask kernel",
    "language": "python",
    "interrupt_mode": "signal",
    "metadata": {},
}

http = Blueprint('jupyter', __name__)
websocket = Blueprint('jupyter', __name__)


@http.route('/api/kernelspecs')
def kernelspecs(name=None):
    return jsonify({
        'default': 'flask_kernel',
        'kernelspecs': {
            'flask_kernel': {
                'name': 'flask_kernel',
                'resources': {},
                'spec': _kernel_spec
            }
        }
    })


@http.route('/api/kernels', methods=['GET', 'POST'])
def kernels_normal():
    data = {
        "id": "4a8a8c6c-188c-40aa-8bab-3c79500a4b26",
        "name":
            "flask_kernel",
        "last_activity": "2018-01-30T19:32:04.563616Z",
        "execution_state":
            "starting",
        "connections": 0
    }
    return jsonify(data), 201


@websocket.route('/api/kernels/<id>/<name>')
def kernels(ws, id, name):
    kernel = FlaskKernel.instance()
    # kernel.stream.last_ws = ws
    while not ws.closed:
        message = ws.receive()
        if message is not None:
            msg = json.loads(message)
            msg_serialized = kernel.session.serialize(msg)
            # print("msg from front end", msg)
            # print(kernel.comm_manager.comms)
            msg_id = msg['header']['msg_id']
            kernel.session.websockets[msg_id] = ws
            if msg['channel'] == 'shell':
                kernel.dispatch_shell(WebsocketStreamWrapper(ws, msg['channel']), [
                    BytesWrap(k) for k in msg_serialized])
            else:
                print('unknown channel', msg['channel'])


def app(prefix='/jupyter', app=None):
    kernel = FlaskKernel.instance()
    app = app or Flask(__name__)

    @app.template_filter()
    def ipywidget_view(widget):
        from jinja2 import Markup
        import json
        return Markup("""<script type="application/vnd.jupyter.widget-view+json">%s</script>""" % json.dumps(
            widget.get_view_spec()))

    @app.template_filter()
    def ipywidget_state(widgets):
        from jinja2 import Markup
        from ipywidgets import embed as wembed
        drop_defaults = True
        state = wembed.dependency_state(widgets, drop_defaults=drop_defaults)
        from ipywidgets import Widget
        json_data = Widget.get_manager_state(widgets=[])
        json_data['state'] = state
        json_data_str = json.dumps(json_data, indent=' ')
        snippet = wembed.snippet_template.format(
            load='', widget_views='', json_data=json_data_str)
        return Markup(snippet)

    @app.route('/static/<path:path>')
    def send_js(path):
        app.logger.debug("serve static file: static/{}".format(path))
        return send_from_directory('static', path)

    sockets = Sockets(app)
    app.register_blueprint(http, url_prefix=prefix)
    sockets.register_blueprint(websocket, url_prefix=prefix)
    return app


def main_factory(_app):
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), _app, handler_class=WebSocketHandler)
    return server.serve_forever
