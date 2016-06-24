from __future__ import unicode_literals
import json
import unittest

from sqlalchemy.orm.exc import NoResultFound
from nose.tools import assert_almost_equal
from six import PY3

from clld.tests.util import WithDbMixin, WithCustomLanguageMixin
from clld.db.models.common import Language
from clld.db.meta import DBSession, VersionedDBSession


class Tests(WithCustomLanguageMixin, WithDbMixin, unittest.TestCase):

    def test_JSONEncodedDict(self):
        l = Language(id='abc', name='Name', jsondata={'i': 2})
        DBSession.add(l)
        DBSession.flush()

        DBSession.expunge(l)
        for lang in DBSession.query(Language).filter(Language.id == 'abc'):
            self.assertEqual(lang.jsondata['i'], 2)
            break

    def test_CustomModelMixin(self):
        from clld.tests.fixtures import CustomLanguage

        DBSession.add(CustomLanguage(id='abc', name='Name', custom='c'))
        DBSession.flush()
        for lang in DBSession.query(Language).filter(Language.id == 'abc'):
            self.assertEqual(lang.custom, 'c')
            self.assertTrue('custom_t' in lang.__solr__(None))
            break

    def test_CustomModelMixin_polymorphic(self):
        from clld.tests.fixtures import CustomLanguage

        lang = Language(id='def', name='Name')
        clang = CustomLanguage(id='abc', name='Name', custom='c')
        DBSession.add_all([lang, clang])
        DBSession.flush()
        DBSession.expunge_all()
        lang = DBSession.query(Language).filter_by(id='def').one()
        clang = DBSession.query(Language).filter_by(id='abc').one()

        self.assertEqual(lang.polymorphic_type, 'base')
        self.assertEqual(clang.polymorphic_type, 'custom')
        self.assertIs(type(lang), Language)
        self.assertIs(type(clang), CustomLanguage)

    def test_CsvMixin(self):
        l1 = Language(id='abc', name='Name', latitude=12.4, jsondata=dict(a=None))
        DBSession.add(l1)
        DBSession.flush()
        l1 = Language.csv_query(DBSession).first()
        cols = l1.csv_head()
        row = l1.to_csv()
        for k, v in zip(cols, row):
            if k == 'jsondata':
                self.assertIn('a', json.loads(v))
        l2 = Language.from_csv(row)
        assert_almost_equal(l1.latitude, l2.latitude)
        row[cols.index('latitude')] = '3,5'
        l2 = Language.from_csv(row)
        self.assertLess(l2.latitude, l1.latitude)

    def test_CsvMixin2(self):
        from clld.db.meta import CsvMixin

        class B(object):
            id = 5

        class A(CsvMixin):
            b = None
            bs = None

            def __init__(self, b=None):
                if b:
                    self.b = b
                    self.bs = [b, b]

            def csv_head(self):
                return ['b__id', 'bs__ids']

        a = A(B())
        self.assertEquals(a.to_csv(), [5, "5,5"])
        a = A.from_csv(['5', "5,5"])
        assert a.b is None
        assert a.bs is None

    def test_Base(self):
        l = Language(id='abc', name='Name')
        VersionedDBSession.add(l)
        VersionedDBSession.flush()
        VersionedDBSession.expunge(l)
        l = Language.get('abc')
        self.assertEqual(l.name, 'Name')
        assert not list(l.history())

        # a bit of a hack to test the human readable representations.
        # we exploit the fact, that on py2, string and unicode comparison does type
        # coercion, while on py3, the two methods should actually return the same string.
        self.assertEqual(l.__str__(), l.__unicode__())
        Language().__str__()
        if PY3:  # pragma: no cover
            self.assertEqual(repr(l), "<Language 'abc'>")
        else:
            self.assertEqual(repr(l), "<Language u'abc'>")

    def test_Base_jsondata(self):
        l = Language(id='abc', name='Name')
        VersionedDBSession.add(l)
        VersionedDBSession.flush()
        l.update_jsondata(a=1)
        self.assertTrue('a' in l.jsondata)
        l.update_jsondata(b=1)
        self.assertTrue('b' in l.jsondata and 'a' in l.jsondata)
        self.assertTrue('b' in l.__json__(None)['jsondata'])

    def test_Base_get(self):
        self.assertEqual(42, Language.get('doesntexist', default=42))
        self.assertRaises(NoResultFound, Language.get, 'doesntexist')
