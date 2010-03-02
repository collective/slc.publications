from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent

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
        try:
            # FIXME: shouldn't this additional data be created along
            # with the pdf?

            # Calling this from browser/publications.py e.g. viewing a
            # publication as an Anonymous user was returning
            # Unauthorized.
            container.invokeFactory("Folder", additionals_id)
            additionals = getattr(container, additionals_id)
            additionals.setTitle('Additional material on %s' % ob.Title())
            additionals.setExcludeFromNav(True)
            additionals.reindexObject()
        except Unauthorized:
            return None
    else:
        additionals = getattr(container, additionals_id)

    return additionals
