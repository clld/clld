from json import dumps
import unittest

from mock import Mock, MagicMock, patch


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

        with patch.multiple(
            'clld.scripts.tilemill',
            urlopen=Mock(return_value=Mock(read=lambda: dumps(GEOJSON))),
            ZipFile=MagicMock(),
        ):
            main('http://example.org/')
