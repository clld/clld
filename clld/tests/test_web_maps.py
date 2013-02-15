from mock import Mock

from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.interfaces import IMap


class Tests(TestWithEnv):
    def test_Map(self):
        from clld.web.maps import Map

        class MockRoute(Mock):
            name = 'language'

        self.set_request_properties(matched_route=MockRoute())

        dt = Map(common.Parameter.first(), self.env['request'])
        dt.render()
