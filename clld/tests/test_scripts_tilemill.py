from json import dumps
import unittest

from mock import Mock, MagicMock, patch
from six import PY3

from clld.util import to_binary


GEOJSON = {
    'features': [
        {'properties': {'icon': 'x', 'language': {'id': 'code'}}},
    ],
    'properties': {
        'name': 'Parameter',
        'domain': [
            {'id': '1', 'name': 'de', 'icon': 'x'},
            {'id': '1', 'name': 'de', 'icon': ''},
        ],
    }
}


class Tests(unittest.TestCase):
    def test_main(self):
        from clld.scripts.tilemill import main

        geojson = dumps(GEOJSON)
        if PY3:  # pragma: no cover
            geojson = to_binary(geojson)

        with patch.multiple(
            'clld.scripts.tilemill',
            urlopen=Mock(return_value=Mock(read=lambda: geojson)),
            ZipFile=MagicMock(),
        ):
            main('http://example.org/')
