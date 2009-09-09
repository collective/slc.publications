from Acquisition import aq_base, aq_inner, aq_parent
from slc.publications.interfaces import IPublicationEnhanced

def _get_storage_folder(ob):
    """ Helper Method to fetch the folder containing additional material like chapters and further pdf parts 
    """
    if not IPublicationEnhanced.providedBy(ob):
        return None

    additionals_id = ob.getId().replace('.pdf', '')+'_data'

    if additionals_id == ob.getId():
        raise AttributeError, "Cannot get a unique name for the additionals folder"
        
    container = aq_parent(aq_inner(ob)) 
    
    if additionals_id not in container.objectIds():
        container.invokeFactory("Folder", additionals_id)
        additionals = getattr(container, additionals_id)
        additionals.setTitle('Additional material on %s' % ob.Title())
        additionals.setExcludeFromNav(True)
        additionals.reindexObject()
    else:    
        additionals = getattr(container, additionals_id)

    return additionals
