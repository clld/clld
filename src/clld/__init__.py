import collections

from clld.db.models import common
from clld import interfaces

__version__ = "7.3.0"


class Resource(collections.namedtuple('Resource', 'name model interface with_index with_rdfdump')):

    def __new__(cls, name, model, interface, with_index=True, with_rdfdump=True):
        return super(Resource, cls).__new__(cls, name, model, interface, with_index, with_rdfdump)

    @property
    def plural(self):
        return self.name + 's'


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
        'combination',
        common.Combination,
        interfaces.ICombination,
        with_index=False,
        with_rdfdump=False),
]
