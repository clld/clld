"""
Support for the provider implementation of an OLAC OAI-PMH repository.

.. seealso:: http://www.language-archives.org/OLAC/repositories.html
"""
import re
from datetime import datetime, timedelta
from copy import copy
from collections import namedtuple

from pyramid.renderers import render
from pyramid.response import Response
from sqlalchemy.orm import joinedload_all, undefer
from clldutils.misc import UnicodeMixin

from clld.db.models.common import Language, LanguageIdentifier, Identifier, IdentifierType
from clld.interfaces import IOlacConfig


#
# OAI-PMH protocol specifics:
#
VERBS = [
    'GetRecord',
    'Identify',
    'ListIdentifiers',
    'ListMetadataFormats',
    'ListRecords',
    'ListSets',
]

ERRORS = {
    'badArgument': 'The request includes illegal arguments, is missing required '
    'arguments, includes a repeated argument, or values for arguments have an illegal '
    'syntax.',
    'badResumptionToken': 'The value of the resumptionToken argument is invalid or '
    'expired.',
    'badVerb': 'Value of the verb argument is not a legal OAI-PMH verb, the verb '
    'argument is missing, or the verb argument is repeated.',
    'cannotDisseminateFormat': 'The metadata format identified by the value given for '
    'the metadataPrefix argument is not supported by the item or by the repository.',
    'idDoesNotExist': 'The value of the identifier argument is unknown or illegal in '
    'this repository.',
    'noRecordsMatch': 'The combination of the values of the from, until, set and '
    'metadataPrefix arguments results in an empty list.',
    'noMetadataFormats': 'There are no metadata formats available for the specified '
    'item.',
    'noSetHierarchy': 'The repository does not support sets.'
}

MD_PREFIX = 'olac'

TIMESTAMP_REGEX = '[0-9]{4}\-[0-9]{2}\-[0-9]{2}'
TIMESTAMP_PATTERN = re.compile(TIMESTAMP_REGEX + '$')

Participant = namedtuple('Participant', 'role name email')
Institution = namedtuple('Institution', 'name url location')


def timestamp(dt=None):
    return str(dt or datetime.utcnow()).split('.')[0].replace(' ', 'T') + 'Z'


def date(dt=None):
    return str(dt or datetime.utcnow()).split(' ')[0]


class ResumptionToken(UnicodeMixin):

    """Represents an OAI-PMH resumption token.

    We encode all information from a List query in the resumption token so that we do
    not actually have to keep track of sequences of requests (in the spirit of REST).

    .. seealso: http://www.openarchives.org/OAI/openarchivesprotocol.html#FlowControl
    """

    PATTERN = re.compile('(?P<offset>[0-9]+)(?P<from>f%s)?(?P<until>u%s)?$'
                         % (TIMESTAMP_REGEX, TIMESTAMP_REGEX))
    limit = 100

    def __init__(self, url_arg=None, offset=None, from_=None, until=None):
        def datetime_from_iso(s):
            return datetime(*map(int, s.split('-')))

        self.offset = offset or 0
        self.from_ = from_
        self.until = until

        if url_arg is not None:
            m = self.PATTERN.match(url_arg)
            assert m
            self.offset = int(m.group('offset'))
            assert self.offset % self.limit == 0
            if m.group('from'):
                self.from_ = datetime_from_iso(m.group('from')[1:])
            if m.group('until'):
                self.until = datetime_from_iso(m.group('until')[1:]) + timedelta(1)

    def __unicode__(self):
        res = "%s" % self.offset
        if self.from_:
            res += "f%s" % date(self.from_)
        if self.until:
            res += "u%s" % date(self.until)
        assert self.PATTERN.match(res)
        return res


class OlacConfig(object):

    """Configuration of an applications OLAC repository."""

    scheme = 'oai'
    delimiter = ':'

    def _query(self, req):
        subquery = req.db.query(Identifier)\
            .filter_by(type=IdentifierType.iso.value)\
            .join(LanguageIdentifier)\
            .filter_by(language_pk=Language.pk)
        return req.db.query(Language).filter(subquery.exists())\
            .options(undefer('updated'), joinedload_all(
                Language.languageidentifier, LanguageIdentifier.identifier))

    def get_earliest_record(self, req):
        return self._query(req).order_by(Language.updated, Language.pk).first()

    def get_record(self, req, identifier):
        rec = Language.get(self.parse_identifier(req, identifier), default=None)
        assert rec
        return rec

    def query_records(self, req, from_=None, until=None):
        q = self._query(req).order_by(Language.pk)
        if from_:
            q = q.filter(Language.updated >= from_)
        if until:
            q = q.filter(Language.updated < until)
        return q

    def format_identifier(self, req, item):
        return self.delimiter.join([self.scheme, req.dataset.domain, item.id])

    def parse_identifier(self, req, id_):
        assert self.delimiter in id_
        return id_.split(self.delimiter)[-1]

    def admin(self, req):
        """Configure the archive participant with role admin.

        Note: According to http://www.language-archives.org/OLAC/repositories.html the
        list of participants
        > must include the system administrator whose email address is given in the
        > <oai:adminEmail> element of the Identify response.

        :param req: The current request.
        :return: A suitable `Participant` instance or None.
        """
        return Participant("Admin", "Archive Admin", req.dataset.contact)

    def description(self, req):
        # Note: According to http://www.language-archives.org/OLAC/repositories.html the
        # list of participants
        # > must include the system administrator whose email address is given in the
        # > <oai:adminEmail> element of the Identify response.
        participants = [self.admin(req)]
        for ed in req.dataset.editors:
            participants.append(Participant(
                "Editor",
                ed.contributor.name,
                ed.contributor.email or req.dataset.contact))
        return {
            'archiveURL': 'http://%s/' % req.dataset.domain,
            'participants': participants,
            'institution': Institution(
                req.dataset.publisher_name,
                req.dataset.publisher_url,
                req.dataset.publisher_place,
            ),
            'synopsis': req.dataset.description or '',
        }


def olac(req):
    """View implementing the OLAC OAI-PMH repository protocol."""
    return olac_with_cfg(req, req.registry.getUtility(IOlacConfig))


def olac_with_cfg(req, cfg):
    """Factory function for olac views with different configurations.

    If applications want to disseminate metadata for other resources than languages
    this function can be used to provide a second olac repository.
    """
    res = dict(verb=None, error=None, response_date=timestamp(), params={}, date=date)
    res['cfg'] = cfg

    def response(res):
        return Response(
            render('olac.mako', res, request=req).encode('utf8'),
            content_type='text/xml',
            charset=None)

    def error(_error):
        if _error:
            res['error'] = (_error, ERRORS[_error])
        return response(res)

    args = dict(req.params.items())
    res['params'] = copy(args)
    res['verb'] = args.pop('verb', None)

    if res['verb'] not in VERBS:
        return error("badVerb")

    if res['verb'] == 'ListSets':
        return error("noSetHierarchy")

    if res['verb'] == 'Identify':
        if args:
            return error("badArgument")
        res['earliest'] = res['cfg'].get_earliest_record(req)

    if res['verb'] == 'GetRecord':
        if sorted(args.keys()) != ['identifier', 'metadataPrefix']:
            return error("badArgument")

        if args['metadataPrefix'] != MD_PREFIX:
            return error("cannotDisseminateFormat")

        try:
            res['language'] = res['cfg'].get_record(req, args['identifier'])
        except AssertionError:
            return error("idDoesNotExist")

    if res['verb'] in ['ListIdentifiers', 'ListRecords']:
        if (('metadataPrefix' not in args and 'resumptionToken' not in args)
                or ('from' in args and not TIMESTAMP_PATTERN.match(args['from']))
                or ('until' in args and not TIMESTAMP_PATTERN.match(args['until']))):
            return error("badArgument")

        if [arg for arg in args if arg not in [
                'from', 'until', 'metadataPrefix', 'set', 'resumptionToken']]:
            return error("badArgument")

        if 'set' in args:
            return error("noSetHierarchy")

        if 'resumptionToken' in args:
            if len(args) > 1:
                return error("badArgument")

            try:
                rt = ResumptionToken(url_arg=args['resumptionToken'])
            except AssertionError:
                return error("badResumptionToken")
        else:
            rt = ResumptionToken(
                None, 0, args.get('from', None), args.get('until', None))

        q = res['cfg'].query_records(req, from_=rt.from_, until=rt.until)
        res['languages'] = q.offset(rt.offset).limit(rt.limit).all()
        if not res['languages']:
            return error('noRecordsMatch')

        if len(res['languages']) < rt.limit:
            res['resumptionToken'] = None
        else:
            rt.offset += rt.limit
            res['resumptionToken'] = rt

    if res['verb'] == 'ListMetadataFormats':
        if args and 'identifier' not in args:
            return error("badArgument")

    return response(res)
