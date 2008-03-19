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
    
    # Load the ZCML configuration for the slc.publications package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True
    import slc.publications
    zcml.load_config('configure.zcml', slc.publications)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    # It seems that files are automatically blobs, but my test won't run without this.
    ztc.installPackage('plone.app.blob')
    ztc.installPackage('slc.publications')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_slc_publications()
setupPloneSite(products=['slc.publications'])

class PublicationTestCase(PloneTestCase):
    """Base class for integration tests for the 'Publication' product.
    """

class PublicationFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'Publication' product.
    """
    
    def loadDocumentation(self):
        """ loads a pdf file with pdf metadata set (Title, Description)
            Language = en
            Creator = pilz
            Keywords = documentation,tutorial
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, 'doc', 'UsingthePublicationProduct.pdf'])
        self.docpdf = StringIO(open(filename, 'r').read())
        self.docpdf.filename = 'UsingthePublicationProduct.pdf'
        return self.docpdf
        
    def loadGermanFile(self):
        """ loads a pdf file with pdf metadata set (Title, Description)
            Language = de
            Creator = pilz
            Keywords = documentation,information
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, 'tests', 'data', 'GermanOSHA.pdf'])
        self.germanpdf = StringIO(open(filename, 'r').read())
        self.germanpdf.filename = 'GermanOSHA.pdf'
        return self.germanpdf
        
    def loadGermanFile_de(self):
        """ loads a pdf file with pdf metadata set (Title, Description)
            no Language but filename has extension _de
            Creator = pilz
            Keywords = documentation,tutorial
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, 'doc', 'UsingthePublicationProduct.pdf'])
        self.german_de_pdf = StringIO(open(filename, 'r').read())
        self.german_de_pdf.filename = 'GermanOSHA_de.pdf'
        return self.german_de_pdf
    
    def loadMetadataini(self):
        """ loads an ini file with metadata sets
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, 'tests', 'data', 'metadata.ini'])
        self.metadataini = StringIO(open(filename, 'r').read())
        self.metadataini.filename = 'metadata.ini'
        return self.metadataini