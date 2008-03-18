from persistent.dict import PersistentDict
from zope import interface
from zope import component
from slc.publications import interfaces
from Products.ATContentTypes import interface as atctifaces
from plone.app.blob.interfaces import IATBlobFile
try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces

from p4a.common.descriptors import atfield
from p4a.fileimage import DictProperty


class AnnotationPublication(object):
    """An IPublication adapter designed to handle ATCT based file content.
    """

    interface.implements(interfaces.IPublication)
    component.adapts(atctifaces.IATFile)           
    ANNO_KEY = 'slc.publications.AnnotationPublication'
                                               
    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.publication_data = annotations.get(self.ANNO_KEY, None)
        if self.publication_data is None:
            self.publication_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.publication_data
            

    title = DictProperty(interfaces.IPublication['title'], 'publication_data')
    description = DictProperty(interfaces.IPublication['description'], 'publication_data')
    cover_image = DictProperty(interfaces.IPublication['cover_image'], 'publication_data')
    file = DictProperty(interfaces.IPublication['file'], 'publication_data')
    author = DictProperty(interfaces.IPublication['author'], 'publication_data')
    publication_date = DictProperty(interfaces.IPublication['publication_date'], 'publication_data')
    isbn = DictProperty(interfaces.IPublication['isbn'], 'publication_data')
    order_id = DictProperty(interfaces.IPublication['order_id'], 'publication_data')
    for_sale = DictProperty(interfaces.IPublication['for_sale'], 'publication_data')
    chapters = DictProperty(interfaces.IPublication['chapters'], 'publication_data')
    metadata_upload = DictProperty(interfaces.IPublication['metadata_upload'], 'publication_data')
    owner_password = DictProperty(interfaces.IPublication['owner_password'], 'publication_data')
    user_password = DictProperty(interfaces.IPublication['user_password'], 'publication_data')


#@interface.implementer(interfaces.IPublication)
#@component.adapter(IATBlobFile)
#def ATCTBlobFilePublication(context):
#    if not interfaces.IPublicationEnhanced.providedBy(context):
#        return None
#    return _ATCTPublication(context)

@interface.implementer(interfaces.IPublication)
@component.adapter(atctifaces.IATFile)
def ATCTFilePublication(context):
    if not interfaces.IPublicationEnhanced.providedBy(context):
        return None
    return _ATCTPublication(context)

    
class _ATCTPublication(AnnotationPublication):
    """ 
    """
    interface.implements(interfaces.IPublication)
    component.adapts(atctifaces.IATFile)
       
    ANNO_KEY = 'slc.publications.ATCTFilePublication'

    file = None
    isbn = ''
    cover_image = None

    
    title = atfield('title', 'context')
    description = atfield('description', 'context')
    
    def _get_file(self):
        field = self.context.getPrimaryField()
        return field.getEditAccessor(self.context)()
    def _set_file(self, v):
        if v != interfaces.IPublication['file'].missing_value:
            field = self.context.getPrimaryField()
            field.getMutator(self.context)(v)
    file = property(_get_file, _set_file)


    def _get_cover_image(self):
        v = self.publication_data.get('cover_image', None)
        if v == None or v.get_size() == 0:
            return None
        return v
    def _set_cover_image(self, v):
        if v == interfaces.IPublication['cover_image'].missing_value:
            return
        upload = v
        if isinstance(upload, ofsimage.Image):
            image = upload
        else:
            image = ofsimage.Image(id=upload.filename,
                                   title=upload.filename,
                                   file=upload)
        self.publication_data['cover_image'] = image
    cover_image = property(_get_cover_image, _set_cover_image)


    def _get_isbn(self):
        v = self.publication_data.get('isbn', '')
        return v
    def _set_isbn(self, v):
        self.publication_data['isbn'] = v
    isbn = property(_get_isbn, _set_isbn)
#
#




    def __str__(self):
        return '<slc.publication %s title=%s>' % (self.__class__.__name__, self.title)
    __repr__ = __str__
