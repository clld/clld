from __future__ import unicode_literals

from clld.tests.util import TestWithDb


class Tests(TestWithDb):
    def test_Versioning(self):
        from clld.db.models.common import Language, Identifier, LanguageIdentifier
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

        li = LanguageIdentifier(
            identifier=Identifier(id='asd', type='wals'),
            language=l)
        VersionedDBSession.flush()
        VersionedDBSession.delete(li)
        VersionedDBSession.delete(l)
        VersionedDBSession.flush()
