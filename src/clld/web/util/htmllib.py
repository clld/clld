"""Provide webhelpers2.html functionality in a backwards compatible way.

We reverted back to using a third-party library. This module does only make sure, import
statements still work as before.
"""
from clldutils.html import literal, HTML, escape
assert literal and HTML and escape
