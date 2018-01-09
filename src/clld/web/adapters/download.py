# coding: utf8
"""Functionality to create downloads for the data of a clld app."""
from __future__ import unicode_literals, division, absolute_import, print_function
from zipfile import ZipFile, ZIP_DEFLATED
from gzip import GzipFile
from contextlib import closing

from six import string_types, BytesIO, text_type, StringIO, PY3
from zope.interface import implementer
from pyramid.path import AssetResolver
from sqlalchemy.orm import joinedload, joinedload_all, class_mapper
from csvw.dsv import UnicodeWriter
from clldutils.path import Path
from clldutils.misc import format_size, to_binary

from clld.util import safe_overwrite
from clld.lib.rdf import FORMATS
from clld.web.adapters import get_adapter
from clld.web.adapters.md import TxtCitation
from clld.web.util.helpers import rdf_namespace_attrs
from clld.interfaces import IRepresentation, IDownload
from clld.db.meta import DBSession
from clld.db.models.common import Language, Source, LanguageIdentifier
from clld.db.util import page_query

__all__ = ['download_dir', 'Download', 'N3Dump', 'CsvDump', 'RdfXmlDump']

README = """
{0} data download
{1}

Data of {0} is published under the following license:
{2}

It should be cited as

{3}
"""


def format_readme(req):
    return README.format(
        req.dataset.name,
        '=' * (len(req.dataset.name) + len(' data download')),
        req.dataset.license,
        TxtCitation(None).render(req.dataset, req))


def pkg_name(pkg):
    return pkg if isinstance(pkg, string_types) else pkg.__name__


def abspath(asset_spec):
    return Path(AssetResolver().resolve(asset_spec).abspath())


def download_asset_spec(pkg, *comps):
    return '%s:%s' % (pkg_name(pkg), '/'.join(['static', 'download'] + list(comps)))


def download_dir(pkg):
    return abspath(download_asset_spec(pkg))


@implementer(IDownload)
class Download(object):

    """Represents a download format of a clld app's data."""

    ext = None

    def __init__(self, model, pkg, **kw):
        if self.ext is None:
            self.ext = kw['ext']
        self.rdf = self.ext in [fmt.extension for fmt in FORMATS.values()]
        self.model = model
        self.pkg = pkg_name(pkg)
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def name(self):
        return '%s.%s' % (class_mapper(self.model).class_.__name__.lower(), self.ext)

    def asset_spec(self, req):
        return download_asset_spec(self.pkg, '%s-%s.%s' % (
            req.dataset.id, self.name, 'gz' if self.rdf else 'zip'))

    def url(self, req):
        return req.static_url(self.asset_spec(req))

    def abspath(self, req):
        return abspath(self.asset_spec(req))

    def size(self, req):
        _path = self.abspath(req)
        if _path.exists():
            return format_size(_path.stat().st_size)

    def label(self, req):
        return "%s [%s]" % (getattr(self, 'description', self.name), self.size(req))

    def create(self, req, filename=None, verbose=True, outfile=None):
        with safe_overwrite(outfile or self.abspath(req)) as tmp:
            if self.rdf:
                # we do not create archives with a readme for rdf downloads, because each
                # RDF entity points to the dataset and the void description of the dataset
                # covers all relevant metadata.
                #
                # TODO: write test for the file name things!?
                #
                with closing(GzipFile(
                    filename=Path(tmp.stem).stem, fileobj=tmp.open('wb')
                )) as fp:
                    self.before(req, fp)
                    for i, item in enumerate(page_query(self.query(req), verbose=verbose)):
                        self.dump(req, fp, item, i)
                    self.after(req, fp)
            else:
                with ZipFile(tmp.as_posix(), 'w', ZIP_DEFLATED) as zipfile:
                    if not filename:
                        fp = self.get_stream()
                        self.before(req, fp)
                        for i, item in enumerate(
                                page_query(self.query(req), verbose=verbose)):
                            self.dump(req, fp, item, i)
                        self.after(req, fp)
                        zipfile.writestr(self.name, self.read_stream(fp))
                    else:  # pragma: no cover
                        zipfile.write(Path(filename).as_posix(), self.name)
                    zipfile.writestr('README.txt', format_readme(req).encode('utf8'))

    def get_stream(self):
        return BytesIO()

    def read_stream(self, fp):
        fp.seek(0)
        return fp.read()

    def query(self, req):
        q = DBSession.query(self.model).filter(self.model.active == True)
        if self.model == Language:  # pragma: no cover
            q = q.options(
                joinedload_all(
                    Language.languageidentifier, LanguageIdentifier.identifier),
            )
        if self.model == Source:
            q = q.options(joinedload(Source.languages))
        return q.order_by(self.model.pk)

    def before(self, req, fp):
        pass

    def dump(self, req, fp, item, index):
        adapter = get_adapter(IRepresentation, item, req, ext=self.ext)
        self.dump_rendered(req, fp, item, index, adapter.render(item, req))

    def dump_rendered(self, req, fp, item, index, rendered):
        if isinstance(rendered, text_type):
            rendered = rendered.encode('utf8')
        fp.write(rendered)

    def after(self, req, fp):
        pass


class CsvDump(Download):

    """Download of a resource type as csv."""

    ext = 'csv'

    def __init__(self, model, pkg, fields=None, **kw):
        """Initialize.

        fields can be a list of column names or a dictionary mapping model attribute
        names to csv column names.
        """
        super(CsvDump, self).__init__(model, pkg, **kw)
        self.fields = fields
        self.writer = None

    def get_stream(self):
        return StringIO(newline='') if PY3 else BytesIO()

    def read_stream(self, fp):
        res = Download.read_stream(self, fp)
        if PY3:  # pragma: no cover
            res = res.encode('utf8')
        return res

    def get_fields(self, req):
        if not self.fields:
            self.fields = ['id', 'name']
        return self.fields

    def before(self, req, fp):
        self.writer = UnicodeWriter(fp)
        self.writer.__enter__()
        self.writer.writerow(
            [f if isinstance(f, string_types) else f[1] for f in self.get_fields(req)])

    def row(self, req, fp, item, index):
        return [getattr(item, f if isinstance(f, string_types) else f[0])
                for f in self.get_fields(req)]

    def dump(self, req, fp, item, index):
        self.writer.writerow(self.row(req, fp, item, index))


class N3Dump(Download):

    """Download of a resource type as n-triples."""

    ext = 'n3'

    def dump_rendered(self, req, fp, item, index, rendered):
        header, body = rendered.split(to_binary('\n\n'), 1)
        if index == 0:
            fp.write(header)
            fp.write(to_binary('\n\n'))
        fp.write(body)


class RdfXmlDump(Download):

    """Download of a resource type as rdf-xml."""

    ext = 'rdf'

    def before(self, req, fp):
        fp.write(
            to_binary('<rdf:RDF ') + to_binary(rdf_namespace_attrs()) + to_binary('>\n'))

    def after(self, req, fp):
        fp.write(to_binary('</rdf:RDF>'))

    def dump_rendered(self, req, fp, item, index, rendered):
        body = rendered.split(to_binary('rdf:Description'))[1]
        fp.write(to_binary('<rdf:Description') + body + to_binary('rdf:Description>\n'))
