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

    def test_ParameterMap(self):
        from clld.web.maps import ParameterMap

        class MockRoute(Mock):
            name = 'parameter'

        self.set_request_properties(matched_route=MockRoute())

        dt = ParameterMap(common.Parameter.first(), self.env['request'])
        dt.render()

    def test_LanguageMap(self):
        from clld.web.maps import LanguageMap

        class MockRoute(Mock):
            name = 'language'

        self.set_request_properties(matched_route=MockRoute())

        dt = LanguageMap(common.Language.first(), self.env['request'])
        dt.render()
