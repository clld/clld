from pathlib import Path

from clld.db.meta import DBSession
from clld.db.models import common


def test_Config_replacement_key():
    assert common.Config.replacement_key('X', 'Y') == '__X_Y__'
    assert common.Config.replacement_key(None, 'Y') == '__NoneType_Y__'


def test_Files(db, tmp_path, persist):
    l = common.Sentence(id='abc', name='Name')
    f = common.Sentence_files(object=l, id='abstract', mime_type='audio/mpeg')
    p = f.create(tmp_path, 'content')
    assert Path(p).exists()

    l._files.append(f)
    persist(l)
    DBSession.refresh(l)
    assert l.files
    assert l.audio


def test_Dataset(db, persist):
    from clld import RESOURCES

    d = persist(common.Dataset(id='abc', domain='test'))
    assert d.jsondata == d.jsondatadict
    d.get_stats(RESOURCES, source=common.Source.id == None)


def test_Contributor():
    d = common.Contributor(id='abc')
    d.last_first()
    d = common.Contributor(id='abc', name='Robert Forkel')
    assert d.last_first() == 'Forkel, Robert'
    d = common.Contributor(id='abc', name='Hans Robert von Forkel')
    assert d.last_first() == 'von Forkel, Hans Robert'


def test_Language():
    d = common.Language(id='abc')
    assert d.glottocode is None
    assert d.iso_code is None


def test_Source():
    d = common.Source(id='abc')
    assert d.gbs_identifier is None
    d = common.Source(id='abc', jsondata={'gbs': {'volumeInfo': {}}})
    assert d.gbs_identifier is None
    d = common.Source(
        id='abc',
        jsondata={
            'gbs': {
                'volumeInfo': {
                    'industryIdentifiers': [{'type': 'x', 'identifier': 'y'}]}}})
    assert d.gbs_identifier == 'y'
    d = common.Source(
        id='abc',
        jsondata={
            'gbs': {
                'volumeInfo': {
                    'industryIdentifiers': [{'type': 'ISBN_10', 'identifier': ''}]}}})
    assert d.gbs_identifier == 'ISBN:'
    d = common.Source(
        id='abc',
        jsondata={
            'gbs': {
                'volumeInfo': {
                    'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': ''}]}}})
    assert d.gbs_identifier == 'ISBN:'
    d.bibtex()


def test_Data(db, persist):
    l = common.Language(id='abc', name='Name')
    l.data.append(common.Language_data(key='abstract', value='c'))
    persist(l)
    DBSession.refresh(l)
    assert l.datadict()['abstract'] == 'c'


def test_Unit():
    _ = common.Unit(name='unit', language=common.Language(name='language'))


def test_UnitValue(db, persist):
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
    persist(v, p2)
    try:
        v.unitparameter_pk = p2.pk
        raise ValueError  # pragma: no cover
    except AssertionError:
        pass

    v.unitparameter_pk = p1.pk
    DBSession.flush()


def test_unitvalue_to_string():
    de_name = common.UnitDomainElement(id='de_name', name='Code with name')
    de_noname = common.UnitDomainElement(id='de_noname')
    val_de_name = common.UnitValue(id='val_de_name', unitdomainelement=de_name)
    val_de_noname = common.UnitValue(id='val_de_noname', unitdomainelement=de_noname)
    val_name = common.UnitValue(id='val_name', name='Value with name')
    val_noname = common.UnitValue(id='val_noname')

    assert str(val_de_name) == 'Code with name'
    assert str(val_de_noname) == 'val_de_noname'
    assert str(val_name) == 'Value with name'
    assert str(val_noname) == 'val_noname'


def test_Identifier():
    i = common.Identifier(id='a', name='a', type=common.IdentifierType.iso.value)
    assert i.url()
    i = common.Identifier(id='a', name='a', type='xxx')
    assert i.url() is None


def test_Contribution(data):
    c = DBSession.query(common.Contribution).first()
    assert c.formatted_contributors()


def test_Value(data):
    assert 'valueset' in common.Value.first().__json__(None)


def test_value_to_string():
    de_name = common.DomainElement(id='de_name', name='Code with name')
    de_noname = common.DomainElement(id='de_noname')
    val_de_name = common.Value(id='val_de_name', domainelement=de_name)
    val_de_noname = common.Value(id='val_de_noname', domainelement=de_noname)
    val_name = common.Value(id='val_name', name='Value with name')
    val_noname = common.Value(id='val_noname')

    assert str(val_de_name) == 'Code with name'
    assert str(val_de_noname) == 'val_de_noname'
    assert str(val_name) == 'Value with name'
    assert str(val_noname) == 'val_noname'


def test_Combination(data):
    p = common.Parameter.first()
    c = common.Combination.get(common.Combination.delimiter.join(2 * [p.id]))
    assert c.values
    assert c.domain
    assert c.__json__()
