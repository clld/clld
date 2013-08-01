from zipfile import ZipFile
from cStringIO import StringIO

from path import path
from zope.interface import implementer
from pyramid.path import AssetResolver
from sqlalchemy.orm import joinedload, class_mapper
from clld.lib.dsv import UnicodeCsvWriter
from clld.web.adapters import get_adapter
from clld.web.adapters.md import TxtCitation
from clld.interfaces import IRepresentation, IDownload
from clld.db.meta import DBSession


@implementer(IDownload)
class Download(object):
    ext = None

    def __init__(self, model, pkg, **kw):
        if self.ext is None:
            self.ext = kw['ext']
        self.model = model
        self.pkg = pkg if isinstance(pkg, basestring) else pkg.__name__
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def name(self):
        return '%s.%s' % (class_mapper(self.model).class_.__name__.lower(), self.ext)

    def asset_spec(self, req):
        return '%s:static/download/%s-%s.zip' % (self.pkg, req.dataset.id, self.name)

    def url(self, req):
        return req.static_url(self.asset_spec(req))

    def abspath(self, req):
        return path(AssetResolver().resolve(self.asset_spec(req)).abspath())

    def create(self, req):
        p = self.abspath(req)
        if not p.dirname().exists():
            p.dirname().mkdir()

        with ZipFile(p, mode='w') as zipfile:
            fp = StringIO()
            self.before(req, fp)
            for i, item in enumerate(self.query(req)):
                self.dump(req, fp, item, i)
            self.after(req, fp)
            fp.seek(0)
            zipfile.writestr(self.name, fp.read())
            zipfile.writestr('README.txt', """
{0} data download
{1}

Data of {0} is published under the following license:
{2}

It should be cited as

{3}
""".format(req.dataset.name,
           '='*(len(req.dataset.name) + len(' data download')),
           req.dataset.license,
           TxtCitation(None).render(req.dataset, req)))

    def query(self, req):
        return DBSession.query(self.model).filter(self.model.active == True)\
            .order_by(self.model.pk)

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
        kw['fields'] = fields or ['id', 'name']
        super(CsvDump, self).__init__(model, pkg, **kw)
        self.writer = None

    def before(self, req, fp):
        self.writer = UnicodeCsvWriter(fp)
        self.writer.writerow(
            [f if isinstance(f, basestring) else f[1] for f in self.fields])

    def dump(self, req, fp, item, index):
        self.writer.writerow(
            [getattr(item, f if isinstance(f, basestring) else f[0])
             for f in self.fields])


class N3Dump(Download):
    ext = 'n3'

    def dump_rendered(self, req, fp, item, index, rendered):
        header, body = rendered.split('\n\n', 1)
        if index == 0:
            fp.write(header)
            fp.write('\n\n')
        fp.write(body)
