import os
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from StringIO import StringIO
from Globals import package_home
from slc.publications.config import product_globals

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ztc.installProduct('PloneLanguageTool')
ztc.installProduct('LinguaPlone')
ztc.installProduct('Five')
ztc.installProduct('FiveSite')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.PloneTestCase.layer import onsetup, PloneSite
    
@onsetup
def setup_slc_publications():
    """Set up the additional products required for the Publication Content.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True
    import Products.Five
    zcml.load_config('meta.zcml', Products.Five)
    import Products.FiveSite
    zcml.load_config('configure.zcml', Products.FiveSite)
    # Load the ZCML configuration for the slc.publications package.
    # This includes the other products below as well.
    
    import slc.publications
    zcml.load_config('configure.zcml', slc.publications)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    # It seems that files are automatically blobs, but my test won't run without this. (Plone3.1?)
    try:
        ztc.installPackage('plone.app.blob')
        ztc.installPackage('slc.publications')
    except AttributeError, error:
        # Old ZopeTestCase
        pass
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_slc_publications()
extra_products = ['PloneLanguageTool', 'LinguaPlone', 'slc.publications']
try:
    import plone.app.blob
except ImportError, error:
    # No plone.app.blob installed
    pass
else:
    extra_products.append('plone.app.blob')
setupPloneSite(products=extra_products)

class PublicationTestCase(PloneTestCase):
    """Base class for integration tests for the 'Publication' product.
    """
    def _setup(self):
        PloneTestCase._setup(self)
        # Set the local component registry
        from zope.app.component.hooks import setSite
        setSite(self.portal)

class PublicationFunctionalTestCase(FunctionalTestCase, PublicationTestCase):
    """Base class for functional integration tests for the 'Publication' product.
    """

    def loadfile(self, rel_filename):
        home = package_home(product_globals)
        filename = os.path.sep.join([home, rel_filename])
        data = StringIO(open(filename, 'r').read())
        data.filename = os.path.basename(rel_filename)
        return data
