from zope import component
from zope import interface
from zope import schema
from slc.publications import interfaces

class IContextualPublicationSupport(interfaces.IBasicPublicationSupport):
    can_activate_publication = schema.Bool(title=u'Can Activate Publication',
                                     readonly=True)
    can_deactivate_publication = schema.Bool(title=u'Can Deactivate Publication',
                                       readonly=True)

class Support(object):
    """A view that returns certain information regarding p4acal status.
    """

    interface.implements(IContextualPublicationSupport)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @property
    def support_enabled(self):
        """Check to make sure an IPublicationSupport utility is available and
        if so, query it to determine if support is enabled.
        """
        
        support = component.queryUtility(interfaces.IPublicationSupport)
        if support is None:
            return False

        return support.support_enabled

    @property
    def _basic_can(self):
        if not self.support_enabled:
            return False

        if not interfaces.IAnyPublicationCapable.providedBy(self.context):
            return False

        return True

    @property
    def can_activate_video(self):
        if not self._basic_can:
            return False
        
        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='publication-config.html')
        return not mediaconfig.media_activated

    @property
    def can_deactivate_video(self):
        if not self._basic_can:
            return False
        
        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='publication-config.html')
        return mediaconfig.media_activated
