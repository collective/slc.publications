from zope import interface
from zope import component
from slc.publications import interfaces
from Products.ATContentTypes import interface as atctifaces
from plone.app.blob.interfaces import IATBlob
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

    ANNO_KEY = 'slc.publications.AnnotationPublication'

    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.publication_data = annotations.get(self.ANNO_KEY, None)
        if self.publication_data is None:
            self.publication_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.publication_data
        print "In my annoadapter XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"        
            

    title = DictProperty(interfaces.IPublication['title'], 'publication_data')
    description = DictProperty(interfaces.IPublication['description'], 'publication_data')
    isbn = DictProperty(interfaces.IPublication['isbn'], 'publication_data')
#    rich_description = DictProperty(interfaces.IPublication['rich_description'],
#                                    'publication_data')
#    video_author = DictProperty(interfaces.IPublication['video_author'], 'publication_data')
#    height = DictProperty(interfaces.IPublication['height'], 'publication_data')
#    width = DictProperty(interfaces.IPublication['width'], 'publication_data')
#    duration = DictProperty(interfaces.IPublication['duration'], 'publication_data')
#    file = DictProperty(interfaces.IPublication['file'], 'publication_data')
#    video_image = DictProperty(interfaces.IPublication['video_image'], 'publication_data')
#    video_type = DictProperty(interfaces.IPublication['video_type'], 'publication_data')
#    urls = DictProperty(interfaces.IPublication['urls'], 'publication_data')
#


@interface.implementer(interfaces.IPublication)
@component.adapter(IATBlob)
def ATCTBlobPublication(context):
    if not interfaces.IVideoEnhanced.providedBy(context):
        return None
    return _ATCTPublication(context)

@interface.implementer(interfaces.IPublication)
@component.adapter(atctifaces.IATFile)
def ATCTFilePublication(context):
    if not interfaces.IVideoEnhanced.providedBy(context):
        return None
    return _ATCTPublication(context)

    
class _ATCTPublication(AnnotationPublication):
    """ 
    """
    interface.implements(interfaces.IPublication)
    component.adapts(atctifaces.IATFile)
        

    ANNO_KEY = 'slc.publications.ATCTFilePublication'

    file = None

    title = atfield('title', 'context')
    description = atfield('description', 'context')



    def _get_file(self):
        field = self.context.getPrimaryField()
        return field.getEditAccessor(self.context)()
    def _set_file(self, v):
        if v != interfaces.IVideo['file'].missing_value:
            field = self.context.getPrimaryField()
            field.getMutator(self.context)(v)
    file = property(_get_file, _set_file)



    def _get_isbn(self):
        v = self.publication_data.get('isbn', '')
        return v
    def _set_isbn(self, v):
        self.video_data['isbn'] = v
    isbn = property(_get_isbn, _set_isbn)






    def __str__(self):
        return '<slc.publication %s title=%s>' % (self.__class__.__name__, self.title)
    __repr__ = __str__
