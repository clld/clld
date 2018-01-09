# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from sqlalchemy.orm import undefer
from sqlalchemy.exc import InvalidRequestError

from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.migration import Connection


def test_crud(db):
    migration = Connection(DBSession)

    assert len(list(migration.select(common.Identifier))) == 0
    pk = migration.insert(
        common.Identifier,
        id='iso-csw', name='csw', type=common.IdentifierType.iso.value)
    assert migration.pk(common.Identifier, 'iso-csw') == pk
    assert len(list(migration.select(common.Identifier))) == 1

    identifier = DBSession.query(common.Identifier)\
        .options(undefer('*')).get(pk)
    assert identifier.active
    assert identifier.version == 1
    assert identifier.created
    assert identifier.updated

    migration.update(common.Identifier, [('name', 'cea')], pk=pk)
    DBSession.refresh(identifier)
    assert identifier.name == 'cea'

    migration.delete(common.Identifier, pk=pk)
    with pytest.raises(InvalidRequestError):
        DBSession.refresh(identifier)


def test_set_glottocode(db):
    c = Connection(DBSession)
    lpk = c.insert(common.Language, id='l', name='Language')
    c.set_glottocode('l', 'abcd1234')
    c.set_glottocode('l', 'abcd1234')
    l = DBSession.query(common.Language).get(lpk)
    assert l.glottocode == 'abcd1234'

    c.set_glottocode('l', 'dcba1234')
    DBSession.expire_all()
    l = DBSession.query(common.Language).get(lpk)
    assert l.glottocode == 'dcba1234'
    c.set_glottocode('l', 'abcd1234')
