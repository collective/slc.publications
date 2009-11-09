from zope import schema
from zope.interface import Interface, alsoProvides
from zope.app.content import interfaces as contentifaces


class IAnyPublicationCapable(Interface):
    """Any aspect of publication/content capable.
    """
    
class IPossiblePublication(IAnyPublicationCapable):
    """ All objects that should have the ability to be converted to some
        form of publication should implement this interface.
    """

class IPossiblePublicationContainer(IAnyPublicationCapable):
    """ All objects that should have the ability to be converted to some
        form of publication should implement this interface.
    """

class IPublicationEnhanced(Interface):
    """ Marker interface for publications
    """
        
class IPublicationContainerEnhanced(Interface):
    """ Any folderish entity that has had it's IPublicationContainer features
        enabled.
    """

alsoProvides(IPublicationEnhanced, contentifaces.IContentType)


class IPublication(Interface):
    """ Objects which have publication information.
    """
    
class IPublicationProvider(Interface):
    """ Provide publications.
    """
    publication_items = schema.List(title=u'Publication Items', required=True, readonly=True)    


                                    
class IBasicPublicationSupport(Interface):
    """ Provides certain information about publication support.
    """
    support_enabled = schema.Bool(title=u'Publication Support Enabled?', required=True, readonly=True)                

class IPublicationSupport(IBasicPublicationSupport):
    """ Provides full information about publication support.
    """     
                                      
class IMediaActivator(Interface):
    """ For seeing the activation status or toggling activation.
    """
    media_activated = schema.Bool(title=u'Media Activated',required=True, readonly=False)
    
    
class IPrettyFormatter(Interface):
    """ Provides functionality to format strings """

class IAdditionalPublicationInfo(Interface):
    """ Marker for adapter that provides additional info in the publication view """
