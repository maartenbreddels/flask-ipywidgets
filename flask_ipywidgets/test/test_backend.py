def test_up_and_running(test_client):
    """ make sure the app is up and running

    """

    app, client = test_client

    response = client.get('/')
    assert response.status_code == 200
    assert b"""type="application/vnd.jupyter.widget-state+json""" in response.data
