# coding: utf8
from __future__ import unicode_literals
import logging
logging.disable(logging.WARN)
from tempfile import mkdtemp

from sqlalchemy import create_engine, null
from sqlalchemy.orm import sessionmaker
from path import path
from mock import Mock

from clld.tests.util import TestWithEnv
from clld.db.meta import Base, DBSession
from clld.db.models.common import Dataset, Language, Contribution


class Tests(TestWithEnv):
    def test_freeze(self):
        from clld.scripts.freeze import freeze_func, unfreeze_func

        tmp = path(mkdtemp())
        tmp.joinpath('data').mkdir()

        class Args(object):
            env = self.env
            module_dir = tmp
            module = Mock(__name__='name')

            def data_file(self, *comps):
                return tmp.joinpath('data', *comps)

        DBSession.flush()
        args = Args()
        freeze_func(args, dataset=Dataset.first(), with_history=False)
        self.assert_(tmp.joinpath('data.zip').exists())

        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        self.assertEqual(
            engine.execute('select count(*) from language').fetchone()[0], 0)
        unfreeze_func(args, engine=engine)

        s1 = DBSession
        s2 = sessionmaker(bind=engine)()
        self.assertEqual(s1.query(Language).count(), s2.query(Language).count())

        l1 = s1.query(Language).filter(Language.latitude != null()).first()
        l2 = s2.query(Language).filter(Language.pk == l1.pk).first()
        self.assertEqual(l1.created, l2.created)
        self.assertEqual(l1.latitude, l2.latitude)
        self.assertEqual(l1.description, l2.description)

        contrib = s2.query(Contribution).filter(Contribution.id == 'contribution').one()
        self.assert_(contrib.primary_contributors)
        self.assert_(contrib.secondary_contributors)

        tmp.rmtree(ignore_errors=True)
