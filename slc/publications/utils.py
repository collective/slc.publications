from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent

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
        pt = getToolByName(ob, 'portal_types')
        folder_type = pt.getTypeInfo("Folder")
        # Deliberately bypassing the security mechanism so that
        # Anonymous users can also create this folder
        factory_method = folder_type._getFactoryMethod(
            container, check_security=0
            )
        factory_method(additionals_id)
        additionals = getattr(container, additionals_id)
        additionals.title = 'Additional material on %s' % ob.Title()
        additionals.setExcludeFromNav(True)
        additionals.reindexObject()
    else:
        additionals = getattr(container, additionals_id)

    return additionals
