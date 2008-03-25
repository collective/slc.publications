# -*- coding: utf-8 -*-
#
# File: publications.py
#
# GNU General Public License (GPL)
#

__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'


# Product configuration.

from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.utils import DisplayList
from DateTime import DateTime
FLOOR_DATE = DateTime() # always effective
CEILING_DATE = DateTime("2037/01/01") # never expires

PROJECTNAME = "slc.publications"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

product_globals = globals()

AUTHOR = u"European Agency for Safety and Health at Work" # Set your default author here
DFORMAT = '%Y/%m/%d' # date format for date-widgets
SHOW_HM = 1 # show hour and minute in edit-macro for date-widgets

# Used to store Link objects
ALLOWED_TYPES = ["Link"]