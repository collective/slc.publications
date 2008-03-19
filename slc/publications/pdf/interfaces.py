from zope import schema
from zope.interface import Interface, alsoProvides


class IPDFParser(Interface):
    """Parser Utility to parse pdf files
    """

    def parse(pdf, owner_password='', user_password=''):
        """ parses the given pdf file and returns a mapping of attributes """