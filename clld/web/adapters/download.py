from zipfile import ZipFile, ZIP_DEFLATED
from gzip import GzipFile
from cStringIO import StringIO
from contextlib import closing

from path import path
from zope.interface import implementer
from pyramid.path import AssetResolver
from sqlalchemy.orm import joinedload, joinedload_all, class_mapper
from clld.lib.dsv import UnicodeCsvWriter
from clld.lib.rdf import FORMATS
from clld.web.adapters import get_adapter
from clld.web.adapters.md import TxtCitation
from clld.web.util.helpers import rdf_namespace_attrs
from clld.interfaces import IRepresentation, IDownload
from clld.db.meta import DBSession
from clld.db.models.common import Language, Source, LanguageIdentifier
from clld.db.util import page_query
from clld.util import format_size


def pkg_name(pkg):
    return pkg if isinstance(pkg, basestring) else pkg.__name__


def abspath(asset_spec):
    return path(AssetResolver().resolve(asset_spec).abspath())


def download_asset_spec(pkg, *comps):
    return '%s:%s' % (pkg_name(pkg), '/'.join(['static', 'download'] + list(comps)))


def download_dir(pkg):
    return abspath(download_asset_spec(pkg))


@implementer(IDownload)
class Download(object):
    """
    >>> from mock import Mock
    >>> dl = Download(Source, 'clld', ext='x')
    >>> assert dl.asset_spec(Mock()).startswith('clld:')
    """
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
            return format_size(_path.size)

    def label(self, req):
        return "%s [%s]" % (getattr(self, 'description', self.name), self.size(req))

    def create(self, req, filename=None, verbose=True):
        p = self.abspath(req)
        if not p.dirname().exists():
            p.dirname().mkdir()
        tmp = path('%s.tmp' % p)

        if self.rdf:
            # we do not create archives with a readme for rdf downloads, because each
            # RDF entity points to the dataset and the void description of the dataset
            # covers all relevant metadata.
            with closing(GzipFile(tmp, 'w')) as fp:
                self.before(req, fp)
                for i, item in enumerate(page_query(self.query(req), verbose=verbose)):
                    self.dump(req, fp, item, i)
                self.after(req, fp)
        else:
            with ZipFile(tmp, 'w', ZIP_DEFLATED) as zipfile:
                if not filename:
                    fp = StringIO()
                    self.before(req, fp)
                    for i, item in enumerate(
                            page_query(self.query(req), verbose=verbose)):
                        self.dump(req, fp, item, i)
                    self.after(req, fp)
                    fp.seek(0)
                    zipfile.writestr(self.name, fp.read())
                else:
                    zipfile.write(filename, self.name)
                zipfile.writestr(
                    'README.txt',
                    """
{0} data download
{1}

Data of {0} is published under the following license:
{2}

It should be cited as

{3}
""".format(
                    req.dataset.name,
                    '=' * (len(req.dataset.name.encode('utf8'))
                           + len(' data download')),
                    req.dataset.license,
                    TxtCitation(None).render(req.dataset, req).encode('utf8')))
        if p.exists():
            p.remove()
        tmp.move(p)

    def query(self, req):
        q = DBSession.query(self.model).filter(self.model.active == True)
        if self.model == Language:
            q = q.options(
                joinedload_all(
                    Language.languageidentifier, LanguageIdentifier.identifier),
                #joinedload(Language.sources)
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
        fp.write(rendered.encode('utf8'))

    def after(self, req, fp):
        pass


class CsvDump(Download):
    ext = 'csv'

    def __init__(self, model, pkg, fields=None, **kw):
        """fields can be a list of column names or a dictionary mapping model attribute
        names to csv column names.
        """
        super(CsvDump, self).__init__(model, pkg, **kw)
        self.fields = fields
        self.writer = None

    def get_fields(self, req):
        if not self.fields:
            self.fields = ['id', 'name']
        return self.fields

    def before(self, req, fp):
        self.writer = UnicodeCsvWriter(fp)
        self.writer.writerow(
            [f if isinstance(f, basestring) else f[1] for f in self.get_fields(req)])

    def row(self, req, fp, item, index):
        return [getattr(item, f if isinstance(f, basestring) else f[0])
                for f in self.get_fields(req)]

    def dump(self, req, fp, item, index):
        self.writer.writerow(self.row(req, fp, item, index))


class N3Dump(Download):
    ext = 'n3'

    def dump_rendered(self, req, fp, item, index, rendered):
        header, body = rendered.split('\n\n', 1)
        if index == 0:
            fp.write(header)
            fp.write('\n\n')
        fp.write(body)


class RdfXmlDump(Download):
    ext = 'rdf'

    def before(self, req, fp):
        fp.write('<rdf:RDF %s>\n' % rdf_namespace_attrs())

    def after(self, req, fp):
        fp.write('</rdf:RDF>')

    def dump_rendered(self, req, fp, item, index, rendered):
        body = rendered.split('rdf:Description')[1]
        fp.write('<rdf:Description%srdf:Description>\n' % body)


class Sqlite(Download):
    ext = 'sqlite'

    def create(self, req):  # pragma: no cover
        print '+---------------------------------------------+'
        print '| This download must be created "by hand".'
        print '| Make sure a suitable file is available at'
        print '|', self.abspath(req)
        print '| when the app is started.'
        print '+---------------------------------------------+'
        return
        #super(Sqlite, self).create(req, filename=postgres2sqlite(self.pkg))
