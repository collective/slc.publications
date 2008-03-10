## Script (Python) "getFolderPublications"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None
##title=wrapper method around getFolderContents to return only publications
##

contents = context.getFolderContents(contentFilter)

return contents
