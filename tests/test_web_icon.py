import pytest

from clld.db.models.common import DomainElement, Value, ValueSet
from clld.web.icon import Icon


def test_Icon():
    icon = Icon('c000', opacity=0.5)
    assert icon.color == '#00000080'
    assert icon.shape == 'c'


@pytest.mark.parametrize(
    'spec,icon,opacity',
    [
        ('x', 'x', None),
        ('c012', 'c001122', None),
        ("c012'xyz", 'c001122', None),
        ('12345678', '1223344', None),
        ('123456700', '1234567', 0),
    ]
)
def test_Icon_parse_icon_spec(spec, icon, opacity):
    assert Icon.parse_icon_spec(spec) == (icon, opacity)


def test_Icon_from_req(mocker):
    icon = Icon.from_req(mocker.Mock(), mocker.Mock(), icon_spec_factory=lambda c, r: ('c000', 'x'))
    assert icon.name == 'c000000'
    de = DomainElement(number='1', jsondata={'icon': 'c000'})
    icon = Icon.from_req(de, mocker.MagicMock(params={}))
    assert icon.name == 'c000000'
    icon = Icon.from_req(Value(domainelement=de), mocker.MagicMock(params={}))
    assert icon.name == 'c000000'
    icon = Icon.from_req(ValueSet(values=[Value(domainelement=de)]), mocker.MagicMock(params={}))
    assert icon.name == 'c000000'
