import time


def test_ui(selenium):
    selenium.browser.get(selenium.url('/'))
    time.sleep(3)
