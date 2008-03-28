## Script (Python) "fetchRelatedPublications"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=limit=0
##title=retrieves Publications which have the same keywords
##
from Products.AdvancedQuery import In, Eq, Le, Ge, And, Or
subject = context.Subject()
pc = context.portal_catalog
if hasattr(pc, 'getZCatalog'):
  pc = pc.getZCatalog()

PQ = Eq('portal_type', 'Publication') & In('Subject', subject) & Eq('review_state', 'published')
RES = pc.evalAdvancedQuery(PQ, (('effective','desc'),) )

PUBS = []
for R in RES:
    if R.getPath() == "/".join(context.getPhysicalPath()):
        continue
    PUBS.append(R)

if limit >0 and len(PUBS)>limit:
    PUBS = PUBS[:limit]

return PUBS
