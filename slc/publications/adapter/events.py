from Acquisition import aq_base, aq_inner, aq_parent
import ConfigParser, StringIO, tempfile, os, urllib, logging, re
from types import *
from zope import interface
from zope import component
from slc.publications import interfaces
from slc.publications.utils import _get_storage_folder
from Products.CMFCore.utils import getToolByName
from p4a.subtyper.interfaces import ISubtyper
from Products.Archetypes.interfaces import IObjectInitializedEvent

try:
    from Products.LinguaPlone.config import RELATIONSHIP
    HAVE_LINGUAPLONE=True
except:
    HAVE_LINGUAPLONE=False
    RELATIONSHIP = ''

import logging
logger = logging.getLogger('slc.publications')
# Event handler methods

def _findAbbrev(id, langs):
    """ scan the id for an inplicitly given language abbreviation """
    
    id = id.rsplit(".", 1)[0]
    if len(id)>3 and id[2] in ['_', '-']:
        lang = id[0:2].lower()
        name = id[3:]
        if lang in langs:
            return (name, lang)
    if len(id)>3 and id[-3] in ['_', '-']:
        lang = id[-2:]
        name = id[:-3]
        if lang in langs:
            return (name, lang)
    return [id]


def object_added(evt):
    """ EVENT
        An object has been added to the pub folder. We make sure that
        a) that files are subtyped
        b) translation relations are set
        I have no idea about the performance of this. If adding objects in large pub folders 
        is too slow, consider disabling this.
    """
    obj = evt.object
    if not interfaces.IPublicationContainerEnhanced.providedBy(aq_parent(obj)):
        return
    portal_languages = getToolByName(obj, 'portal_languages')
    default_language = portal_languages.getDefaultLanguage()
    langs = portal_languages.getSupportedLanguages()
    
    # A mapping which stores {lang: obj} mappings under each common naming component
    # E.g. {'test': {'en': atfile1, 'de': atfile2}}
    GROUPS = {}

    subtyper = component.getUtility(ISubtyper)
    children = obj.aq_parent.objectValues(['ATFile', 'ATBlob'])
    for child in children:
        if subtyper.existing_type(child) is None:
            subtyper.change_type(child, 'slc.publications.Publication')

        comp = _findAbbrev(child.getId(), langs)
        childname = comp[0]
        if len(comp)==2:    # comp is a component tuple ('test', 'de')
            childlang = comp[1]
            if child.Language()!= comp[1]:
                pass
                #child.setLanguage('')
                #child.setLanguage(comp[1])
        elif child.Language() != '':
            childlang = child.Language()
        else:
            childlang = default_language
            
        namemap = GROUPS.get(childname, {})
        namemap[childlang] = child
        GROUPS[childname] = namemap


    # Set the proper linguaplone relations. 
    # But only if we already have a canonical
    if HAVE_LINGUAPLONE:
        canonical = namemap.get(default_language, None)
        if canonical is None:
            return         
        for key in GROUPS.keys():
            namemap = GROUPS[key]
            if canonical != canonical.getCanonical():
                canonical.setCanonical()
                
            for lang in namemap.keys():
                if lang == default_language:
                    continue

                o = namemap[lang] 

                if o.getCanonical() != canonical:
                    o.addReference(canonical, RELATIONSHIP)
                    o.invalidateTranslationCache()        
                    o.reindexObject()
    
def generate_image(obj, evt):
    """ EVENT
        called on objectmodified. Tries to generate the cover image. 
    """
    # Make sure we execute this only on the canonical
    #If the event is an ObjectInitializedEvent, we skip
    if IObjectInitializedEvent.providedBy(evt):
        return
        
    if hasattr(obj.aq_explicit, 'getCanonical') and obj != obj.getCanonical():
        return
        
    interfaces.IPublication(obj).generateImage()
    
   
def updateChapterLinksForTranslation(ob):
    """ Read the chapternames and compair them to the Link objects inside the
        Publication for all translations. Add/Delete where they differ
        syncronizes the chapter links in ob to be compliant with the
        current portal languages and the chapters in getChapter
    """
    pw = getToolByName(ob, 'portal_workflow')
    if ob is None:
        return 
    chapterfield = ob.getField('chapters')
    if chapterfield is None:
        logger.warn('Publication has no chapterfield: %s' % ob.absolute_url())
        return
    chapters = chapterfield.getAccessor(ob)()
    
    additionals = _get_storage_folder(ob)
    links = additionals.objectIds('ATLink')

    # remove all links which are not named in getChapters
    RM = []
    for l in links:
        if l not in chapters:
            RM.append(l)
    additionals.manage_delObjects(ids=RM)

    for c in chapters:
        c = c.encode('utf-8')
        if c not in links:
            additionals.invokeFactory('Link', c)
            L = getattr(additionals, c)
            L.setTitle(c)
            L.setLanguage(ob.Language())
            remurl = "/%s#%s" % ( urllib.unquote(ob.absolute_url(1)), c )
            L.edit(remurl)
            L.unmarkCreationFlag()
            pw.doActionFor(L, 'publish', comment='Publish publication link %s in language %s.' % (c, ob.Language()))   
            L.reindexObject()

def update_chapters(obj, evt):
    """ EVENT: 
        Update the chapter links based on the new set values in chapters
    """    
    # Make sure we execute this only on the canonical
    if HAVE_LINGUAPLONE:
        if obj != obj.getCanonical():
            return

            
    if HAVE_LINGUAPLONE:
        translations = obj.getTranslations()
    else:
        translations = {obj.Language(): (obj, obj.Language())}

    for T in translations.keys():
        updateChapterLinksForTranslation(translations[T][0])


# Event handler to catch our own patched event while translation named IObjectTranslationReferenceSetEvent
# We need this to be able to subtype an object while it is translated.
def subtype_on_translate(obj, evt):
    """ EVENT: 
        Update the chapter links based on the new set values in chapters
    """    
    canonical = aq_base(aq_inner(evt.object))
    target = aq_base(aq_inner(evt.target))
    subtyper = component.getUtility(ISubtyper)    
    subtype = subtyper.existing_type(canonical)
    if subtype is not None:
        subtyper.change_type(target, subtype.name)
