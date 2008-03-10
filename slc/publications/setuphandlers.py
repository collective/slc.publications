# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# GNU General Public License (GPL)
#

__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'


import os, logging, transaction
logger = logging.getLogger('publications: setuphandlers')
from slc.publications.config import PROJECTNAME
from slc.publications.config import DEPENDENCIES
from Products.CMFCore.utils import getToolByName


def isNotpublicationsProfile(context):
    return context.readDataFile("publications-various.txt") is None


def configurePortal(site):
    """ makes settings within the portal """
    
    propsTool = getToolByName(site, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    typesUseViewActionInListings = list(siteProperties.getProperty('typesUseViewActionInListings'))
    if 'Publication' not in typesUseViewActionInListings:
        typesUseViewActionInListings.append('Publication')
    siteProperties.manage_changeProperties(typesUseViewActionInListings  = typesUseViewActionInListings)

    # Add the getImage metadatum if not already present
    pc = getToolByName(site, 'portal_catalog')
    col = 'getImage'
    if col not in pc.schema():
        pc.addColumn(col)

    # Add blob file support
    quickinst = getToolByName(site, 'portal_quickinstaller')
    quickinst.installProduct('plone.app.blob')

    # register publication_listing as view method
    pt = getToolByName(site, 'portal_types')
    LPF = getattr(pt, 'Large Plone Folder')
    vm = list(LPF.getProperty('view_methods'))
    vm.append('publication_listing')
    LPF._updateProperty('view_methods', tuple(vm))


def installGSDependencies(context):
    """Install dependend profiles."""
    if isNotpublicationsProfile(context): return 

    # XXX Hacky, but works for now. has to be refactored as soon as generic
    # setup allows a more flexible way to handle dependencies.

    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'publications':
        # the current import step is triggered too many times, this creates infinite recursions
        # therefore, we'll only run it if it is triggered from proper context
        logger.debug("installGSDependencies will not run in context %s" % shortContext)
        return
    logger.info("installGSDependencies started")
    dependencies = []
    if not dependencies:
        return

    site = context.getSite()
    setup_tool = getToolByName(site, 'portal_setup')
    qi = getToolByName(site, 'portal_quickinstaller')
    for dependency in dependencies:
        logger.info("  installing GS dependency %s:" % dependency)
        if dependency.find(':') == -1:
            dependency += ':default'
        old_context = setup_tool.getImportContextID()
        setup_tool.setImportContext('profile-%s' % dependency)
        importsteps = setup_tool.getImportStepRegistry().sortSteps()
        excludes = [
            u'publications-QI-dependencies',
            u'publications-GS-dependencies'
        ]
        importsteps = [s for s in importsteps if s not in excludes]
        for step in importsteps:
            logger.debug("     running import step %s" % step)
            setup_tool.runImportStep(step) # purging flag here?
            logger.debug("     finished import step %s" % step)
        # let's make quickinstaller aware that this product is installed now
        product_name = dependency.split(':')[0]
        qi.notifyInstalled(product_name)
        logger.debug("   notified QI that %s is installed now" % product_name)
        # maybe a savepoint is welcome here (I saw some in optilude's examples)? maybe not? well...
        transaction.savepoint()
        if old_context: # sometimes, for some unknown reason, the old_context is None, believe me
            setup_tool.setImportContext(old_context)
        logger.debug("   installed GS dependency %s:" % dependency)

    # re-run some steps to be sure the current profile applies as expected
    importsteps = setup_tool.getImportStepRegistry().sortSteps()
    filter = [
        u'typeinfo',
        u'workflow',
        u'membranetool',
        u'factorytool',
        u'content_type_registry',
        u'membrane-sitemanager'
    ]
    importsteps = [s for s in importsteps if s in filter]
    for step in importsteps:
        setup_tool.runImportStep(step) # purging flag here?
    logger.info("installGSDependencies finished")

def installQIDependencies(context):
    """This is for old-style products using QuickInstaller"""
    if isNotpublicationsProfile(context): return 
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'publications': # avoid infinite recursions
        logger.debug("installQIDependencies will not run in context %s" % shortContext)
        return
    logger.info("installQIDependencies starting")
    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')

    for dependency in DEPENDENCIES:
        if qi.isProductInstalled(dependency):
            logger.info("   re-Installing QI dependency %s:" % dependency)
            qi.reinstallProducts([dependency])
            transaction.savepoint() # is a savepoint really needed here?
            logger.debug("   re-Installed QI dependency %s:" % dependency)
        else:
            if qi.isProductInstallable(dependency):
                logger.info("   installing QI dependency %s:" % dependency)
                qi.installProduct(dependency)
                transaction.savepoint() # is a savepoint really needed here?
                logger.debug("   installed dependency %s:" % dependency)
            else:
                logger.info("   QI dependency %s not installable" % dependency)
                raise "   QI dependency %s not installable" % dependency
    logger.info("installQIDependencies finished")



def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotpublicationsProfile(context): return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'publications': # avoid infinite recursions
        return
    site = context.getSite()
    
    configurePortal(site)


