"""Functionality to create downloads for the data of a clld app."""
import io
import gzip
import pathlib
import zipfile
import contextlib

from zope.interface import implementer
from pyramid.path import AssetResolver
from sqlalchemy.orm import joinedload, class_mapper
from csvw.dsv import UnicodeWriter
from clldutils.misc import format_size, to_binary

from clld.util import safe_overwrite
from clld.lib.rdf import FORMATS
from clld.web.adapters import get_adapter
from clld.web.adapters.md import TxtCitation
from clld.web.util.helpers import rdf_namespace_attrs
from clld.interfaces import IRepresentation, IDownload
from clld.db.meta import DBSession
from clld.db.models.common import Language, Source, LanguageIdentifier, Dataset
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


def format_readme(req, dataset):
    return README.format(
        dataset.name,
        '=' * (len(dataset.name) + len(' data download')),
        dataset.license,
        TxtCitation(None).render(dataset, req))


def pkg_name(pkg):
    return pkg if isinstance(pkg, str) else pkg.__name__


def abspath(asset_spec):
    return pathlib.Path(AssetResolver().resolve(asset_spec).abspath())


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
        dataset = req.db.query(Dataset).first()
        return download_asset_spec(self.pkg, '%s-%s.%s' % (
            dataset.id, self.name, 'gz' if self.rdf else 'zip'))

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
                with contextlib.closing(gzip.GzipFile(
                    filename=pathlib.Path(tmp.stem).stem, fileobj=tmp.open('wb')
                )) as fp:
                    self.before(req, fp)
                    for i, item in enumerate(page_query(self.query(req), verbose=verbose)):
                        self.dump(req, fp, item, i)
                    self.after(req, fp)
            else:
                with zipfile.ZipFile(tmp.as_posix(), 'w', zipfile.ZIP_DEFLATED) as zipf:
                    if not filename:
                        fp = self.get_stream()
                        self.before(req, fp)
                        for i, item in enumerate(page_query(self.query(req), verbose=verbose)):
                            self.dump(req, fp, item, i)
                        self.after(req, fp)
                        zipf.writestr(self.name, self.read_stream(fp))
                    else:  # pragma: no cover
                        zipf.write(str(pathlib.Path(filename)), self.name)
                    zipf.writestr(
                        'README.txt',
                        format_readme(req, req.db.query(Dataset).first()).encode('utf8'))

    def get_stream(self):
        return io.BytesIO()

    def read_stream(self, fp):
        fp.seek(0)
        return fp.read()

    def query(self, req):
        q = DBSession.query(self.model).filter(self.model.active == True)
        if self.model == Language:  # pragma: no cover
            q = q.options(
                joinedload(
                    Language.languageidentifier
                ).joinedload(
                    LanguageIdentifier.identifier
                )
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
        if isinstance(rendered, str):
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
        return io.StringIO(newline='')

    def read_stream(self, fp):
        return Download.read_stream(self, fp).encode('utf8')

    def get_fields(self, req):
        if not self.fields:
            self.fields = ['id', 'name']
        return self.fields

    def before(self, req, fp):
        self.writer = UnicodeWriter(fp)
        self.writer.__enter__()
        self.writer.writerow(
            [f if isinstance(f, str) else f[1] for f in self.get_fields(req)])

    def row(self, req, fp, item, index):
        return [getattr(item, f if isinstance(f, str) else f[0])
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
