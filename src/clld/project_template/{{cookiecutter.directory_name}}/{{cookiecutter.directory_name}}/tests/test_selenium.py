import time


def test_ui(selenium):
    selenium.browser.get(selenium.url('/'))
{% if cookiecutter.cldf_module %}
    time.sleep(1)
    selenium.browser.get(selenium.url('/languages'))
    time.sleep(3)
    selenium.browser.get(selenium.url('/sources'))
{% endif %}
    time.sleep(3)
