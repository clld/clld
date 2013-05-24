from clld.tests.util import TestWithEnv


class Tests(TestWithEnv):
    def with_params(self, **kw):
        from clld.web.views.olac import olac

        self.set_request_properties(params=kw)
        return olac(self.env['request'])

    def test_olac_no_verb(self):
        self.assertTrue(self.with_params()['error'])

    def test_olac_listsets(self):
        self.assertTrue(self.with_params(verb='ListSets')['error'])

    def test_olac_identify_and_additional_arg(self, ):
        self.assertTrue(self.with_params(verb='Identify', other='arg')['error'])

    def test_olac_identify(self):
        self.assertTrue('earliest' in self.with_params(verb='Identify'))
