## Script (Python) "batchedPublications"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sortfunction='',batch_size=10
##title=wrapper method around PublicationFolder (batched)
##

contents = None
sortedcontents = []

contents = context.aq_explicit.getPublicationList()

if sortfunction!='':
    try:
    	sortedcontents = sequence.sort(contents, sortfunction)
    except:
        sortedcontents  = contents
else:
    sortedcontents = contents

from Products.CMFPlone import Batch
b_start = context.REQUEST.get('b_start', 0)
batch = Batch(sortedcontents, batch_size, int(b_start), orphan=0)
return batch
