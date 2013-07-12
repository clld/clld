from collections import namedtuple

from clld.db.models import common
from clld import interfaces


_Resource = namedtuple('Resource', 'name model interface with_index with_adapters')


def Resource(name, model, interface, with_index=True, with_adapters=True):
    return _Resource(name, model, interface, with_index, with_adapters)


RESOURCES = [
    Resource('dataset', common.Dataset, interfaces.IDataset, with_index=False),
    Resource('file', common.File, interfaces.IFile, with_adapters=False),
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
]
