# -*- coding: utf-8 -*-

__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'

from zope.i18nmessageid import MessageFactory
SLCPublicationsMessageFactory = MessageFactory('slc.publications')

import logging

logger = logging.getLogger('slc.publications')
logger.debug('Installing slc.publications')

try:
    from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
    from Products.LinguaPlone.utils import generateMethods
    from Products.LinguaPlone.config import RELATIONSHIP
    import linguaplone_addTranslation_patch
    HAVE_LINGUAPLONE=True
    logger.info('slc.publications :: Patching LinguaPlone addTranslation')
except ImportError:
    HAVE_LINGUAPLONE=False
    class AlreadyTranslated(Exception):
        """Raised when trying to create an existing translation."""
        pass
    generateMethods = None
    RELATIONSHIP = ""
    logger.info('slc.publications :: LinguaPlone not installed. Not patching LinguaPlone addTranslation')


import os
import os.path
from Globals import package_home
import Products.CMFPlone.interfaces
from Products.Archetypes import listTypes
from Products.Archetypes.atapi import *
from Products.Archetypes.utils import capitalize
from Products.CMFCore import DirectoryView
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import ToolInit
from config import *

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.file import ATFileSchema





ATFileSchema['file'].languageIndependent = False
ATFileSchema['file'].required = False
finalizeATCTSchema(ATFileSchema)


def initialize(context):
    """initialize product (called by zope)"""

    # Initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types=content_types,
        permission=DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors=constructors,
        fti=ftis,
        ).initialize(context)
