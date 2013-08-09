from datetime import date

from clld.tests.util import TestWithEnv


def test_ResumptionToken():
    from clld.web.views.olac import ResumptionToken

    assert ResumptionToken(from_=date.today(), until=date.today()).__unicode__()


class Tests(TestWithEnv):
    def with_params(self, **kw):
        from clld.web.views.olac import olac

        self.set_request_properties(params=kw)
        return olac(self.env['request'])

    def est_olac_no_verb(self):
        self.assertTrue(self.with_params()['error'])

    def est_olac_listsets(self):
        self.assertTrue(self.with_params(verb='ListSets')['error'])

    def est_olac_identify_and_additional_arg(self, ):
        self.assertTrue(self.with_params(verb='Identify', other='arg')['error'])

    def est_olac_identify(self):
        self.assertTrue('earliest' in self.with_params(verb='Identify'))

    def est_olac_listMetadataFormats(self):
        self.assertTrue('cfg' in self.with_params(verb='ListMetadataFormats'))
        self.assertTrue(self.with_params(verb='ListMetadataFormats', other='x')['error'])

    def est_olac_list(self):
        from clld.web.views.olac import OlacConfig

        self.assertTrue(
            self.with_params(verb='ListIdentifiers', metadataPrefix='olac')['languages'])
        cfg = OlacConfig()
        assert cfg.description(self.env['request'])
        res = self.with_params(verb='ListIdentifiers', metadataPrefix='olac')['languages']
        assert cfg.iso_codes(res[0])
        id_ = cfg.format_identifier(self.env['request'], res[0])
        self.assertTrue(self.with_params(
            verb='GetRecord', metadataPrefix='olac', identifier=id_)['language'])
        self.assertTrue(self.with_params(
            verb='GetRecord', metadataPrefix='olac')['error'])
        self.assertTrue(self.with_params(
            verb='GetRecord', metadataPrefix='ol', identifier=id_)['error'])
        self.assertTrue(self.with_params(
            verb='GetRecord', metadataPrefix='olac', identifier=id_+'123')['error'])

        self.assertTrue(
            self.with_params(verb='ListIdentifiers', resumptionToken='tr', o='')['error'])
        self.assertTrue(
            self.with_params(verb='ListIdentifiers', resumptionToken='tr')['error'])
        self.assertEqual(
            self.with_params(
                verb='ListIdentifiers',
                resumptionToken='0f2000-01-01u2222-01-01').get('error'),
            None)
        self.assertTrue(
            self.with_params(verb='ListIdentifiers', resumptionToken='100')['error'])
        self.assertTrue(
            self.with_params(
                verb='ListIdentifiers',
                resumptionToken='100f2000-01-01u2000-01-01')['error'])
