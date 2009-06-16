import os
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from StringIO import StringIO
from Globals import package_home
from slc.publications.config import product_globals

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import onsetup, PloneSite
from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import layer

SiteLayer = layer.PloneSite

class PublicationsLayer(SiteLayer):
    @classmethod
    def setUp(cls):
        ztc.installProduct('PloneLanguageTool')
        ztc.installProduct('LinguaPlone')
        fiveconfigure.debug_mode = True
        import slc.publications
        import plone.app.blob
        zcml.load_config('configure.zcml', slc.publications)
        zcml.load_config('configure.zcml', plone.app.blob)
        fiveconfigure.debug_mode = False
        ztc.installPackage('slc.publications')
        ztc.installPackage('plone.app.blob')
        setupPloneSite(products=['plone.app.blob', 'slc.publications'])
        SiteLayer.setUp()


class PublicationTestCase(PloneTestCase):
    """Base class for integration tests for the 'Publication' product.
    """
    layer = PublicationsLayer

class PublicationFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'Publication' product.
    """
    layer = PublicationsLayer

    def loadfile(self, rel_filename):
        home = package_home(product_globals)
        filename = os.path.sep.join([home, rel_filename])
        data = StringIO(open(filename, 'r').read())
        data.filename = os.path.basename(rel_filename)
        return data
