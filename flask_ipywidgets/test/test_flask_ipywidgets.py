import time

import pytest
from selenium import webdriver


@pytest.fixture()
def driver():
    # options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    _driver = webdriver.Chrome()
    return _driver


def test_selenium(driver):
    url = 'http://localhost:5000'
    driver.get(url)
    time.sleep(5)
    h = driver.find_element_by_id("ipywidget-server-result")
    assert h.tag_name == "div"
    driver.quit()
