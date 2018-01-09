# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def test_Versioning(db):
    from clld.db.models.common import Language, Language_data
    from clld.db.meta import VersionedDBSession

    l = Language(id='abc', name='Old Name', jsondata={'i': 2})
    VersionedDBSession.add(l)
    VersionedDBSession.flush()
    assert l.version == 1

    l.name = 'New Name'
    l.description = 'New Description'
    VersionedDBSession.flush()
    assert l.version == 2

    History = l.__history_mapper__.class_
    res = VersionedDBSession.query(History).filter(History.pk == l.pk).all()
    assert res[0].name == 'Old Name'

    l.data.append(Language_data(key='k', value='v'))
    VersionedDBSession.flush()
    assert l.datadict()
    VersionedDBSession.delete(l)
    VersionedDBSession.flush()
