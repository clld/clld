# coding: utf8
from __future__ import unicode_literals
import logging
logging.disable(logging.WARN)
from tempfile import mkdtemp

from six import PY3
from sqlalchemy import create_engine
from path import path
import dataset as ds

from clld.tests.util import TestWithEnv
from clld.db.meta import Base
from clld.db.models.common import Dataset, Source, Parameter, DomainElement
from clld.db.migration import Connection
from clld.lib.bibtex import EntryType


class Tests(TestWithEnv):
    def test_freeze(self):
        from clld.scripts.freeze import freeze_func, unfreeze_func

        if PY3:
            # pending: https://github.com/pudo/dataset/issues/100
            return  # pragma: no cover

        tmp = path(mkdtemp())
        tmp.joinpath('data').mkdir()

        class Args(object):
            env = self.env

            def data_file(self, *comps):
                return tmp.joinpath('data', *comps)

        db = ds.connect('sqlite://', reflectMetadata=False)
        Base.metadata.create_all(db.engine)
        conn = Connection(db.engine)
        conn.insert(Dataset, id='test', domain='test', name='äöüß')
        conn.insert(Dataset, id='test2', domain='test', name='test', jsondata=dict(a=1.1))
        conn.insert(Source, id='test', name='test', bibtex_type=EntryType.book)
        pk = conn.insert(Parameter, id='p', name='p')
        conn.insert(DomainElement, id='de', name='de', parameter_pk=pk)

        args = Args()
        freeze_func(args, dataset=Dataset.first(), datafreeze_db=db)
        self.assert_(tmp.joinpath('data.zip').exists())

        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        unfreeze_func(args, engine=engine)
        count = engine.execute('select count(*) from dataset').fetchone()[0]
        self.assertEqual(count, 2)

        tmp.rmtree(ignore_errors=True)
