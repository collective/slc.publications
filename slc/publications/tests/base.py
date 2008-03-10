import os
from Testing import ZopeTestCase
from StringIO import StringIO
from Globals import package_home
from Products.PublicationProduct.config import product_globals

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct('PloneLanguageTool')
ZopeTestCase.installProduct('PublicationProduct')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site, and apply the membrane and borg extension profiles
# to make sure they are installed.
# extension_profiles=(,),
setupPloneSite(products=('PloneLanguageTool', 'PublicationProduct',))

class PublicationProductTestCase(PloneTestCase):
    """Base class for integration tests for the 'PublicationProduct' product.
    """

class PublicationProductFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'PublicationProduct' product.
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

    def loadMetadataini(self):
        """ loads an ini file with metadata sets
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, 'tests', 'data', 'metadata.ini'])
        self.metadataini = StringIO(open(filename, 'r').read())
        self.metadataini.filename = 'metadata.ini'
