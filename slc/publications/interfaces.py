# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, alsoProvides
from zope.app.content import interfaces as contentifaces
from p4a.fileimage import file as p4afile
from p4a.fileimage import image as p4aimage
from slc.publications.config import AUTHOR

class IPublicationEnhanced(Interface):
    """Marker interface for publications
    """

class IPublicationContainerEnhanced(Interface):
    """Any folderish entity that has had it's IPublicationContainer features
    enabled.
    """    

alsoProvides(IPublicationEnhanced, contentifaces.IContentType)


class IPublication(Interface):
    """Objects which have publication information.
    """

    title = schema.TextLine(title=u'Title', required=False)
    description = schema.Text(title=u'Description', required=False)
#    rich_description = schema.Text(title=u'Rich Text Description',
#                                   required=False)
#    file = p4afile.FileField(title=u'File', required=False)
 #   isbn = schema.TextLine(title=u'ISBN Number', required=False, readonly=False)

#    publication_author = schema.TextLine(title=u'Author', default=AUTHOR, required=False)
    
    
class IPublicationProvider(Interface):
    """Provide publications.
    """
    
    publication_items = schema.List(title=u'Publication Items',
                                    required=True,
                                    readonly=True)    