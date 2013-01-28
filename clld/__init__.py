from clld.db.models.common import (
    Contribution,
    Parameter,
    Language,
    Contributor,
    Source,
    Sentence,
    Value,
    UnitParameter,
    Unit,
)
from clld.interfaces import (
    IContribution,
    IParameter,
    ILanguage,
    IContributor,
    ISource,
    ISentence,
    IValue,
    IUnitParameter,
    IUnit,
)


class Resource(object):
    """Resources are routable models, i.e. model instances with URL.
    """
    def __init__(self, name, model, interface):
        self.name = name
        self.model = model
        self.interface = interface


RESOURCES = [
    Resource('contribution', Contribution, IContribution),
    Resource('parameter', Parameter, IParameter),
    Resource('language', Language, ILanguage),
    Resource('contributor', Contributor, IContributor),
    Resource('source', Source, ISource),
    Resource('sentence', Sentence, ISentence),
    Resource('value', Value, IValue),
    Resource('unitparameter', UnitParameter, IUnitParameter),
    Resource('unit', Unit, IUnit),
]
