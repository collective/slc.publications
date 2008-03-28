from zope import interface
from zope import component
from slc.publications import interfaces

import p4a.z2utils #Patch CMFDynamicViewFTI
from Products.CMFDynamicViewFTI import interfaces as cmfdynifaces

class PublicationContainerDynamicViews(object):
    
    interface.implements(cmfdynifaces.IDynamicallyViewable)
    component.adapts(interfaces.IPublicationContainerEnhanced)

    def __init__(self, context):
        self.context = context # Actually ignored...
        
    def getAvailableViewMethods(self):
        """Get a list of registered view method names
        """
        return [view for view, name in self.getAvailableLayouts()]

    def getDefaultViewMethod(self):
        """Get the default view method name
        """
        return "publication-container.html"

    def getAvailableLayouts(self):
        """Get the layouts registered for this object.
        """        
        return (("publication-container.html", "Publication view"),)
