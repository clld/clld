# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from clldutils.path import Path
from clld.db.meta import DBSession


def test_Config_replacement_key():
    from clld.db.models.common import Config

    assert Config.replacement_key('X', 'Y') == '__X_Y__'
    assert Config.replacement_key(None, 'Y') == '__NoneType_Y__'


def test_Files(db, tmppath):
    from clld.db.models.common import Sentence, Sentence_files

    l = Sentence(id='abc', name='Name')
    f = Sentence_files(object=l, id='abstract', mime_type='audio/mpeg')
    p = f.create(Path(tmppath), 'content')
    assert Path(p).exists()

    l._files.append(f)
    DBSession.add(l)
    DBSession.flush()
    DBSession.refresh(l)
    assert l.files
    assert l.audio


def test_Dataset(db):
    from clld import RESOURCES
    from clld.db.models.common import Dataset, Source

    d = Dataset(id='abc', domain='test')
    DBSession.add(d)
    DBSession.flush()
    assert d.jsondata == d.jsondatadict
    d.get_stats(RESOURCES, source=Source.id == None)


def test_Contributor():
    from clld.db.models.common import Contributor

    d = Contributor(id='abc')
    d.last_first()
    d = Contributor(id='abc', name='Robert Forkel')
    assert d.last_first() == 'Forkel, Robert'
    d = Contributor(id='abc', name='Hans Robert von Forkel')
    assert d.last_first() == 'von Forkel, Hans Robert'


def test_Language():
    from clld.db.models.common import Language

    d = Language(id='abc')
    assert d.glottocode is None
    assert d.iso_code is None


def test_Source():
    from clld.db.models.common import Source

    d = Source(id='abc')
    assert d.gbs_identifier is None
    d = Source(id='abc', jsondata={'gbs': {'volumeInfo': {}}})
    assert d.gbs_identifier is None
    d = Source(
        id='abc',
        jsondata={
            'gbs': {
                'volumeInfo': {
                    'industryIdentifiers': [{'type': 'x', 'identifier': 'y'}]}}})
    assert d.gbs_identifier == 'y'
    d = Source(
        id='abc',
        jsondata={
            'gbs': {
                'volumeInfo': {
                    'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': ''}]}}})
    assert d.gbs_identifier == 'ISBN:'
    d = Source(
        id='abc',
        jsondata={
            'gbs': {
                'volumeInfo': {
                    'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': ''}]}}})
    assert d.gbs_identifier == 'ISBN:'
    d.bibtex()


def test_Data(db):
    from clld.db.models.common import Language, Language_data

    l = Language(id='abc', name='Name')
    l.data.append(Language_data(key='abstract', value='c'))
    DBSession.add(l)
    DBSession.flush()
    DBSession.refresh(l)
    assert l.datadict()['abstract'] == 'c'


def test_Unit():
    from clld.db.models.common import Unit, Language

    u = Unit(name='unit', language=Language(name='language'))


def test_UnitValue(db):
    from clld.db.models.common import Unit, Language, UnitParameter, UnitValue, UnitDomainElement

    u = Unit(name='unit', language=Language(name='language'))
    p1 = UnitParameter()
    p2 = UnitParameter()
    # NOTE: we assume paramter of UnitValue and UnitDomainElement are identical
    #       (i.e. we do not enforce/check this)
    v = UnitValue(
        unit=u, unitparameter=p1,
        unitdomainelement=UnitDomainElement(parameter=p1, name='ude'))
    assert str(v) == 'ude'
    DBSession.add(v)
    DBSession.add(p2)
    DBSession.flush()
    try:
        v.unitparameter_pk = p2.pk
        raise ValueError  # pragma: no cover
    except AssertionError:
        pass

    v.unitparameter_pk = p1.pk
    DBSession.flush()


def test_Identifier():
    from clld.db.models.common import Identifier, IdentifierType

    i = Identifier(id='a', name='a', type=IdentifierType.iso.value)
    assert i.url()
    i = Identifier(id='a', name='a', type='xxx')
    assert i.url() is None


def test_Contribution(data):
    from clld.db.models.common import Contribution

    c = DBSession.query(Contribution).first()
    assert c.formatted_contributors()


def test_Value(data):
    from clld.db.models.common import Value

    assert 'valueset' in Value.first().__json__(None)


def test_Combination(data):
    from clld.db.models.common import Combination, Parameter

    p = Parameter.first()
    c = Combination.get(Combination.delimiter.join(2 * [p.id]))
    assert c.values
    assert c.domain
