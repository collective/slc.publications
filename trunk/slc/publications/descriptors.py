from zope import interface
from p4a.subtyper import interfaces as stifaces
from slc.publications import interfaces


  

class PublicationDescriptor(object):
    interface.implements(stifaces.IPortalTypedDescriptor)

    title = u'Publication'
    description = u'Publication file type'
    type_interface = interfaces.IPublicationEnhanced
    for_portal_type = 'File'

class AbstractPublicationContainerDescriptor(object):
    interface.implements(stifaces.IPortalTypedFolderishDescriptor)

    title = u'Publication Container'
    description = u'Container for holding Publications'
    type_interface = interfaces.IPublicationContainerEnhanced

class FolderPublicationContainerDescriptor(AbstractPublicationContainerDescriptor):
    for_portal_type = 'Folder'

class LargeFolderPublicationContainerDescriptor(AbstractPublicationContainerDescriptor):
    for_portal_type = 'Large Plone Folder'

class TopicPublicationContainerDescriptor(AbstractPublicationContainerDescriptor):
    for_portal_type = 'Topic'

