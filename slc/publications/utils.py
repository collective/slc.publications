from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent

from zope.component import getUtility
from zope.component.interfaces import IFactory

from Products.CMFCore.utils import getToolByName

from slc.publications.interfaces import IPublicationEnhanced


def _get_storage_folder(ob):
    """ Helper Method to fetch the folder containing additional material
        like chapters and further pdf parts
    """
    if not IPublicationEnhanced.providedBy(ob):
        return None

    additionals_id = ob.getId().replace('.pdf', '') + '_data'

    if additionals_id == ob.getId():
        raise AttributeError("Cannot get a unique name" + \
            " for the additionals folder")

    container = aq_parent(aq_inner(ob))

    if additionals_id not in container.objectIds():
        #container.invokeFactory("Folder", additionals_id)
        pt = getToolByName(ob, 'portal_types')
        folder_type = pt.getTypeInfo("Folder")
        factory = getUtility(IFactory, folder_type.factory)
        data_obj = factory(additionals_id, *args, **kw)
        container._setObject(additionals_id, data_obj)
        additionals = getattr(container, additionals_id)
        additionals.title = 'Additional material on %s' % ob.Title()
        additionals.setExcludeFromNav(True)
        additionals.reindexObject()
    else:
        additionals = getattr(container, additionals_id)

    return additionals
