from collections import namedtuple

from clld.db.models import common
from clld import interfaces


__version__ = "0.6"
_Resource = namedtuple('Resource', 'name model interface with_index')


class _ExtendedResource(_Resource):
    @property
    def plural(self):
        return self.name + 's'


def Resource(name, model, interface, with_index=True):
    return _ExtendedResource(name, model, interface, with_index)


RESOURCES = [
    Resource('dataset', common.Dataset, interfaces.IDataset, with_index=False),
    Resource('contribution', common.Contribution, interfaces.IContribution),
    Resource('parameter', common.Parameter, interfaces.IParameter),
    Resource('language', common.Language, interfaces.ILanguage),
    Resource('contributor', common.Contributor, interfaces.IContributor),
    Resource('source', common.Source, interfaces.ISource),
    Resource('sentence', common.Sentence, interfaces.ISentence),
    Resource('valueset', common.ValueSet, interfaces.IValueSet),
    Resource('value', common.Value, interfaces.IValue),
    Resource('unitparameter', common.UnitParameter, interfaces.IUnitParameter),
    Resource('unit', common.Unit, interfaces.IUnit),
    Resource('unitvalue', common.UnitValue, interfaces.IUnitValue),
    Resource(
        'combination', common.Combination, interfaces.ICombination, with_index=False),
]
