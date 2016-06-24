# coding: utf8
from __future__ import unicode_literals
from datetime import date

from clld.tests.util import TestWithEnv, XmlResponse, WithDbAndDataMixin


class OaiPmhResponse(XmlResponse):
    ns = 'http://www.openarchives.org/OAI/2.0/'

    @property
    def error(self):
        e = self.findall('error')
        if e:
            return e[0].get('code')


def test_ResumptionToken():
    from clld.web.views.olac import ResumptionToken

    assert ResumptionToken(from_=date.today(), until=date.today()).__unicode__()


class Tests(WithDbAndDataMixin, TestWithEnv):
    def with_params(self, **kw):
        from clld.web.views.olac import olac

        self.set_request_properties(params=kw)
        return OaiPmhResponse(olac(self.env['request']))

    def test_olac_no_verb(self):
        self.assertEqual(self.with_params().error, 'badVerb')

    def test_olac_listsets(self):
        self.assertNotEqual(self.with_params(verb='ListSets').error, None)

    def test_olac_identify_and_additional_arg(self):
        self.assertEqual(
            self.with_params(verb='Identify', other='arg').error, 'badArgument')

    def test_olac_identify(self):
        assert self.with_params(verb='Identify').findall('Identify')

    def test_olac_listMetadataFormats(self):
        self.with_params(
            verb='ListMetadataFormats').findone('metadataPrefix').text == 'olac'
        assert self.with_params(verb='ListMetadataFormats', other='x').error

    def test_olac_list(self):
        from clld.web.views.olac import OlacConfig

        res = self.with_params(verb='ListIdentifiers', metadataPrefix='olac')
        self.assertTrue(res.findall('header'))

        OlacConfig()

        id_ = self.with_params(verb='Identify').findone(
            '{http://www.openarchives.org/OAI/2.0/oai-identifier}sampleIdentifier').text

        assert self.with_params(
            verb='GetRecord', metadataPrefix='olac', identifier=id_).findone('record')
        assert self.with_params(verb='GetRecord', metadataPrefix='olac').error
        assert self.with_params(
            verb='GetRecord', metadataPrefix='ol', identifier=id_).error
        assert self.with_params(
            verb='GetRecord', metadataPrefix='olac', identifier=id_ + '123').error
        assert self.with_params(
            verb='ListIdentifiers', resumptionToken='tr', metadataPrefix='olac').error
        assert self.with_params(
            verb='ListIdentifiers', resumptionToken='tr', o='x').error
        assert self.with_params(verb='ListIdentifiers').error
        assert self.with_params(
            verb='ListIdentifiers', metadataPrefix='olac', set='x').error
        assert self.with_params(verb='ListIdentifiers', resumptionToken='tr').error
        assert not self.with_params(
            verb='ListIdentifiers',
            resumptionToken='0f2000-01-01u2222-01-01').error
        assert not self.with_params(verb='ListIdentifiers', resumptionToken='100').error
        assert self.with_params(verb='ListIdentifiers', resumptionToken='200').error
        assert self.with_params(
            verb='ListIdentifiers',
            resumptionToken='100f2000-01-01u2000-01-01').error
