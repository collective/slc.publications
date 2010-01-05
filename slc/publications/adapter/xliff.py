from zope.interface import Interface
try:
    from slc.xliff.xliff import BaseAttributeExtractor
except:
    class BaseAttributeExtractor(object):
        """ Dummy """

class PublicationAttributeExtractor(BaseAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based object """
    attrs = ['title', 'description']
    
class PublicationContainerAttributeExtractor(BaseAttributeExtractor):
    """ Adapter to retrieve attributes from a standard event based object """
    attrs = ['title', 'description']    
    