from zope import schema
from zope.interface import Interface, alsoProvides


class IINIParser(Interface):
    """Parser Utility to parse metadata ini files
    """

    def parse(ini):
        """ parses the given ini file and returns a mapping of attributes """
        
    def retrieve(context):
        """ retrieves an ini representation of the given context"""

