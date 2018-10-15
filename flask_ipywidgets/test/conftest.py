import os
import sys
from multiprocessing import Process
from pathlib import Path

import pytest
from gevent import os
from selenium import webdriver

import flask_ipywidgets


@pytest.fixture(scope='module')
def test_client():
    from flask_ipywidgets.example1 import app
    flask_app = flask_ipywidgets.main_factory(app)

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield (flask_app, testing_client)

    ctx.pop()


@pytest.fixture()
def example3_app(request):
    from flask_ipywidgets.example3 import app
    _app = flask_ipywidgets.main_factory(app)
    t = Process(target=_app)

    def start():
        # start the Flask server in a Process
        # Gevent is not to stoked about
        t.daemon = True
        t.start()

    return start


@pytest.fixture()
def driver():
    if sys.platform == "darwin":
        p = Path.home().joinpath("miniconda3", "envs", "flask-ipywidgets", "bin", "phantomjs").resolve()
        path = os.environ["PATH"]
        p = "{}:{}".format(path, p.parent)
        os.environ["PATH"] = p
        _driver = webdriver.PhantomJS()
        return _driver

    elif "TRAVIS" in os.environ or sys.platform == "linux":
        _driver = webdriver.PhantomJS()
        return _driver
