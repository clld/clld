from mock import Mock

from clld.tests.util import TestWithEnv
from clld.db.models import common
from clld.db.meta import DBSession


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

        dt = ParameterMap(common.Parameter.get('parameter'), self.env['request'])
        for l in dt.layers:
            l.representation = 5
        dt.render()

        dt = ParameterMap(common.Parameter.get('no-domain'), self.env['request'])
        dt.render()

    def test_LanguageMap(self):
        from clld.web.maps import LanguageMap

        class MockRoute(Mock):
            name = 'language'

        self.set_request_properties(matched_route=MockRoute())

        dt = LanguageMap(common.Language.first(), self.env['request'])
        dt.render()
