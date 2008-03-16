# -*- coding: utf-8 -*-

from zope.interface import Interface, alsoProvides
from zope.app.content import interfaces as contentifaces


class IPublication(Interface):
    """Marker interface for .Publication.Publication
    """
    
alsoProvides(IPublication, contentifaces.IContentType)
