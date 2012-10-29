 # -*- coding: utf-8 -*-
"""Base TestCases for slc.publications tests."""

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import quickInstallProduct
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.testing import z2
from zope.configuration import xmlconfig

import unittest2 as unittest


class SlcPublications(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import slc.publications
        xmlconfig.file('configure.zcml', slc.publications,
            context=configurationContext)

        z2.installProduct(app, 'Products.LinguaPlone')
        z2.installProduct(app, "slc.publications")

        # required for python scripts e.g. manage_add*
        z2.installProduct(app, 'Products.PythonScripts')

        import Products.LinguaPlone
        self.loadZCML('configure.zcml', package=Products.LinguaPlone)
        import slc.publications
        self.loadZCML('configure.zcml', package=slc.publications)

    def setUpPloneSite(self, portal):
        # Install all the Plone stuff + content (including the
        # Members folder)
        applyProfile(portal, 'Products.CMFPlone:plone')
        applyProfile(portal, 'Products.CMFPlone:plone-content')

        quickInstallProduct(portal, "Products.LinguaPlone")

        applyProfile(portal, 'slc.publications:default')

        # Login as manager and create a test folder
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

        # Enable Members folder
        from plone.app.controlpanel.security import ISecuritySchema
        security_adapter = ISecuritySchema(portal)
        security_adapter.set_enable_user_folders(True)

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        z2.uninstallProduct(app, "slc.publications")


SLC_PUBLICATIONS_FIXTURE = SlcPublications()
SLC_PUBLICATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_PUBLICATIONS_FIXTURE,), name="SlcPublications:Integration")
SLC_PUBLICATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_PUBLICATIONS_FIXTURE,), name="SlcPublications:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = SLC_PUBLICATIONS_INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = SLC_PUBLICATIONS_FUNCTIONAL_TESTING
