def test_selenium(driver, example3_app):
    print("pre start app")
    example3_app()
    print("post start app")
    url = 'http://localhost:5000'
    driver.get(url)
    driver.implicitly_wait(3)
    h = driver.find_element_by_id("ipywidget-server-result")
    assert h.tag_name == "div"
    print("trivial selenium test passed")
    driver.quit()


def test_npm_build(test_client):
    """ assert that JS dependencies have been build & loaded correctly

    """
    pass
