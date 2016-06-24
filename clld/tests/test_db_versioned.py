# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from clld.tests.util import WithDbMixin


class Tests(WithDbMixin, unittest.TestCase):
    def test_Versioning(self):
        from clld.db.models.common import Language, Language_data
        from clld.db.meta import VersionedDBSession

        l = Language(id='abc', name='Old Name', jsondata={'i': 2})
        VersionedDBSession.add(l)
        VersionedDBSession.flush()
        self.assertEqual(l.version, 1)

        l.name = 'New Name'
        l.description = 'New Description'
        VersionedDBSession.flush()
        self.assertEqual(l.version, 2)

        History = l.__history_mapper__.class_
        res = VersionedDBSession.query(History).filter(History.pk == l.pk).all()
        self.assertEqual(res[0].name, 'Old Name')

        l.data.append(Language_data(key='k', value='v'))
        VersionedDBSession.flush()
        assert l.datadict()
        VersionedDBSession.delete(l)
        VersionedDBSession.flush()
