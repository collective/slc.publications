from zope.interface import implements
from p4a.subtyper import interfaces as stifaces
from slc.publications import interfaces

class PublicationDescriptor(object):
    """Descriptor for the publication subtype.
    """

    implements(stifaces.IPortalTypedDescriptor)
    title = u'Publication'
    description = u'New publication.'
    type_interface = interfaces.IPublication
    for_portal_type = 'File'