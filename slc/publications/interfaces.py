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
    cover_image = p4aimage.ImageField(title=u'Cover Image', required=False,
                                      preferred_dimensions=(70, 100))
    file = p4afile.FileField(title=u'File', required=False)
    author = schema.TextLine(title=u'Author', required=False, default=AUTHOR)
    publication_date = schema.Date(title=u'Publication Date', required=True)
    isbn = schema.TextLine(title=u'ISBN Number', required=False)
    order_id = schema.TextLine(title=u'Order-ID', required=False)
    for_sale = schema.Bool(title=u'For sale', required=False)
    chapters = schema.Text(title=u'Chapters', required=False)
    metadata_upload = p4afile.FileField(title=u'Metadata Upload', required=False)            
    owner_password = schema.TextLine(title=u'Owner Password', required=False)
    user_password = schema.TextLine(title=u'User Password', required=False)

    
    
class IPublicationProvider(Interface):
    """Provide publications.
    """
    
    publication_items = schema.List(title=u'Publication Items',
                                    required=True,
                                    readonly=True)    