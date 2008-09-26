from zope.component import getUtility

from Products.CMFCore.utils import getToolByName


def setupActions(self):
    # And now update the relevant portal_type actions
    tool = getToolByName(self, 'portal_types')
    filetype = getattr(tool, 'File')
    acts = filter(lambda x: x.id == 'generate_metadata', filetype.listActions())
    action = acts and acts[0] or None
    if action is None:
        filetype.addAction( 'generate_metadata',
                         'Generate Metadata INI',
                         'string:${object_url}/@@generate-metadata',
                         '',
                         'View',
                         'object_buttons',
                         visible=1
                       )
                               
def setupVarious(context):
    """ setup specials """
    if context.readDataFile('publications-various.txt') is None:
        return
                
    portal = context.getSite()
