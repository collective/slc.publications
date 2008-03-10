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
DEFAULT_RIGHTS = "European Agency for Safety and Health at Work"


PROJECTNAME = "publications"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []


PUBLICATION_TYPES = DisplayList()
PUBLICATION_TYPES.add('full', 'Full Publication')
PUBLICATION_TYPES.add('chapter', 'Chapter of Publication')

PUBLICATION_SORT_CRITERIA = DisplayList()
PUBLICATION_SORT_CRITERIA.add('id', 'ID')
PUBLICATION_SORT_CRITERIA.add('Title', 'Title')
PUBLICATION_SORT_CRITERIA.add('getPublication_date', 'Publication Date')
PUBLICATION_SORT_CRITERIA.add('getOrder_id', 'Order-ID')

AUTHOR = "European Agency for Safety and Health at Work" # Set your default author here
DFORMAT = '%Y/%m/%d' # date format for date-widgets
SHOW_HM = 1 # show hour and minute in edit-macro for date-widgets


