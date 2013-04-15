from clld.db.models import common
from clld import interfaces


class Resource(object):
    """Resources are routable models, i.e. model instances with URL.
    """
    def __init__(self, name, model, interface, with_index=True):
        self.name = name
        self.model = model
        self.interface = interface
        self.with_index = with_index


RESOURCES = [
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
