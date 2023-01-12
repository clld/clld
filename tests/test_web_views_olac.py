from datetime import date

import pytest

from testutils import XmlResponse
from clld.web.views.olac import ResumptionToken, olac, OlacConfig


class OaiPmhResponse(XmlResponse):
    ns = 'http://www.openarchives.org/OAI/2.0/'

    @property
    def error(self):
        e = self.findall('error')
        if e:
            return e[0].get('code')


def test_ResumptionToken():
    assert str(ResumptionToken(from_=date.today(), until=date.today()))


@pytest.mark.parametrize(
    "params,test,expected",
    [
        ({}, lambda res: res.error, 'badVerb'),
        ({'verb': 'ListSets'}, lambda res: res.error, 'noSetHierarchy'),
        (dict(verb='Identify', other='arg'), lambda res: res.error, 'badArgument'),
        (dict(verb='Identify'), lambda res: len(res.findall('Identify')), 1),
        (
            dict(verb='ListMetadataFormats'),
            lambda res: res.findone('metadataPrefix').text,
            'olac'),
        (
            dict(verb='ListMetadataFormats', other='x'),
            lambda res: res.error,
            'badArgument'),
        (
            dict(verb='ListIdentifiers', metadataPrefix='olac'),
            lambda res: len(res.findall('header')),
            100),
        (
            dict(verb='Identify'),
            lambda res: res.findone(
                '{http://www.openarchives.org/OAI/2.0/oai-identifier}sampleIdentifier'
            ).text,
            'oai:clld:language'),
        (
            dict(verb='GetRecord', metadataPrefix='olac', identifier='oai:clld:language'),
            lambda res: res.findone('identifier').text,
            'oai:clld:language'),
        (
            dict(verb='GetRecord', metadataPrefix='olac'),
            lambda res: res.error,
            'badArgument'),
        (
            dict(verb='GetRecord', metadataPrefix='ol', identifier='oai:clld:language'),
            lambda res: res.error,
            'cannotDisseminateFormat'),
        (
            dict(verb='GetRecord', metadataPrefix='olac', identifier='oai:clld:123'),
            lambda res: res.error,
            'idDoesNotExist'),
        (
            dict(verb='ListIdentifiers', resumptionToken='tr', metadataPrefix='olac'),
            lambda res: res.error,
            'badArgument'),
        (
            dict(verb='ListIdentifiers', resumptionToken='tr', o='x'),
            lambda res: res.error,
            'badArgument'),
        (
            dict(verb='ListIdentifiers'),
            lambda res: res.error,
            'badArgument'),
        (
            dict(verb='ListIdentifiers', metadataPrefix='olac', set='x'),
            lambda res: res.error,
            'noSetHierarchy'),
        (
            dict(verb='ListIdentifiers', resumptionToken='tr'),
            lambda res: res.error,
            'badResumptionToken'),
        (
            dict(verb='ListIdentifiers', resumptionToken='0f2000-01-01u2222-01-01'),
            lambda res: res.error,
            None),
        (
            dict(verb='ListIdentifiers', resumptionToken='100'),
            lambda res: res.error,
            None),
        (
            dict(verb='ListIdentifiers', resumptionToken='200'),
            lambda res: res.error,
            'noRecordsMatch'),
        (
            dict(verb='ListIdentifiers', resumptionToken='100f2000-01-01u2000-01-01'),
            lambda res: res.error,
            'noRecordsMatch'),
    ])
def test_olac(request_factory, params, test, expected):
    with request_factory(params=params) as req:
        assert test(OaiPmhResponse(olac(req))) == expected


def test_olac_config():
    OlacConfig()
