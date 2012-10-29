from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from slc.publications import HAVE_LINGUAPLONE
from slc.publications.interfaces import IPublicationEnhanced

import logging

log = logging.getLogger('slc.publications')


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
        # If we're in a LinguaPlone environment and the Publication is not
        # canonical, language-link the additionals folders.
        if HAVE_LINGUAPLONE and not ob.isCanonical():
            can = ob.getCanonical()
            can_additionals = _get_storage_folder(can)
            additionals.setLanguage(ob.Language())
            if not can_additionals.getTranslation(ob.Language()):
                additionals.addTranslationReference(can_additionals)
            else:
                # we should probably raise an Error if the're already a
                # translation
                wrong = can_additionals.getTranslation(ob.Language())
                try:
                    wrong_url = wrong.absolute_url()
                except:
                    wrong_url = "URL not available"
                log.error("The additionals folder of Publication %(can)s is "\
                "already translated to '%(lang)s' but does not have the id "\
                "'%(id)s'. The wrong folder is here: %(wrong_url)s." % dict(
                can=can.absolute_url(), lang=ob.Language(),
                id=additionals_id, wrong_url=wrong_url))
        additionals.reindexObject()
    else:
        additionals = getattr(container, additionals_id)
        # For legacy Publications, check if language-linking is necessary
        # XXX fixme: this should probably go into a migration step!
        if HAVE_LINGUAPLONE and not ob.isCanonical():
            can = ob.getCanonical()
            can_additionals = _get_storage_folder(can)
            if not can_additionals.getTranslation(ob.Language()):
                additionals.addTranslationReference(can_additionals)

    return additionals
