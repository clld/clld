from zope.interface import (
    Interface,
    Attribute,
)


#----------------------------------------------------------------------------
# Interfaces for model classes
#----------------------------------------------------------------------------
class ILanguage(Interface):
    name = Attribute('')
    latitude = Attribute('')
    longitude = Attribute('')


class ISentence(Interface):
    """marker interface
    """


class ISource(Interface):
    """marker interface
    """


class IParameter(Interface):
    """marker interface
    """


class IValue(Interface):
    """marker interface
    """


class IContribution(Interface):
    """marker interface
    """


class IContributor(Interface):
    """marker interface
    """


class IDomainElement(Interface):
    """marker interface
    """


class IUnitParameter(Interface):
    """marker interface
    """


class IUnit(Interface):
    """marker interface
    """


class IUnitValue(Interface):
    """marker interface
    """


class IUnitDomainElement(Interface):
    """marker interface
    """


#----------------------------------------------------------------------------
# Interfaces for pluggable functionality
#----------------------------------------------------------------------------
class IRepresentation(Interface):
    """
    """
    mimetype = Attribute('')
    charset = Attribute('')
    extension = Attribute('')

    def render(request):
        """
        """

    def render_to_response(request):
        """
        """


class IIndex(Interface):
    """
    """
    mimetype = Attribute('')
    charset = Attribute('')
    extension = Attribute('')

    def render(request, query, count):
        """
        """

    def render_to_response(request, query, count):
        """
        """


class IDataTable(Interface):
    """marker
    """


class IMenuItems(Interface):
    """marker interface
    """
