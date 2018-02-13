import logging
import json

import ipykernel.kernelbase
import jupyter_client.session as session
import notebook.base.zmqhandlers 

from ipykernel.comm import CommManager
from notebook.base.zmqhandlers import serialize_binary_message
from jupyter_client.session import json_unpacker, json_packer
from flask import jsonify

SESSION_KEY = b'flask_ipywidgets'


class WebsocketStream(object):
    def __init__(self, session):
        self.session = session

class BytesWrap(object):
    def __init__(self, bytes):
        self.bytes = bytes

class WebsocketStreamWrapper(object):
    def __init__(self, websocket, channel):
        self.websocket = websocket
        self.channel = channel

class SessionWebsocket(session.Session):
    def __init__(self, *args, **kwargs):
        super(SessionWebsocket, self).__init__(*args, **kwargs)
        self.websockets = {} # map from .. msg id to websocket? 

    def send(self, stream, msg_or_type, content=None, parent=None, ident=None,
             buffers=None, track=False, header=None, metadata=None):
        msg = self.msg(msg_or_type, content=content, parent=parent,
                       header=header, metadata=metadata)
        msg['channel'] = stream.channel
        if buffers:
            msg['buffers'] = buffers
            binary_msg = serialize_binary_message(msg)
        else:
            binary_msg = json_packer(msg).decode('utf8')
        for key, ws in list(self.websockets.items()):
            if ws.closed:
                self.websockets.pop(key)
            else:
                print('sending over wire:', binary_msg)
                ws.send(binary_msg)


class FlaskKernel(ipykernel.kernelbase.Kernel):
    implementation = 'ipython'
    implementation_version = '0.1'
    banner = 'banner'
    def __init__(self):
        super(FlaskKernel, self).__init__()
        self.session = SessionWebsocket(parent=self, key=SESSION_KEY)

        self.stream = self.iopub_socket = WebsocketStream(self.session)
        self.iopub_socket.channel = 'iopub'
        self.session.stream = self.iopub_socket
        self.comm_manager = CommManager(parent=self, kernel=self)
        self.shell = None
        self.log = logging.getLogger('fake')

        comm_msg_types = [ 'comm_open', 'comm_msg', 'comm_close' ]
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(self.comm_manager, msg_type)

