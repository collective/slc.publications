import logging
import transaction
from Products.CMFCore.utils import getToolByName
from config import DEPENDENCIES

log = logging.getLogger("slc.publications.setuphandlers.py")

def isNotPublicationsProfile(self):
    return self.readDataFile('publications-various.txt') is None

def installDependencies(self):
    """ Install product dependencies
    """
    if isNotPublicationsProfile(self):
        return

    log.info("installDependencies")
    site = self.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if not qi.isProductInstalled(product):
            log.info("Installing dependency: %s" % product)
            qi.installProduct(product)
            transaction.savepoint(optimistic=True)
    transaction.commit()

def setupActions(self):
    """ Update the relevant portal_type actions
    """
    if isNotPublicationsProfile(self):
        return

    tool = getToolByName(self, 'portal_types')
    filetype = getattr(tool, 'File')
    acts = filter(lambda x: x.id == 'generate_metadata', filetype.listActions())
    action = acts and acts[0] or None
    if action is None:
        filetype.addAction( 
                    'generate_metadata',
                    'Generate Metadata INI',
                    'string:${object_url}/@@generate-metadata',
                    '',
                    'View',
                    'object_buttons',
                    visible=1
                    )
