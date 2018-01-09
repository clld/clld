from __future__ import unicode_literals
import time


def test_ui(selenium):
    selenium.browser.get(selenium.url('/feature'))
    time.sleep(3)
