from zope import interface
from slc.publications import interfaces
from Products.ATContentTypes import interface as atctifaces
try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces


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
            
class ATPublication(AnnotationPublication):
    """ 
    """
    interface.implements(interfaces.IPublication)
    component.adapts(atctifaces.IATFile)

    if not interfaces.IPublicationEnhanced.providedBy(context):
        return None
        

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


    def __str__(self):
        return '<slc.publication %s title=%s>' % (self.__class__.__name__, self.title)
    __repr__ = __str__
