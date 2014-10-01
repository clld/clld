"""
We reverted back to using a third-party library. This module does only make sure, import
statements still work as before.
"""
from webhelpers2.html import literal, HTML, escape
assert literal and HTML and escape
