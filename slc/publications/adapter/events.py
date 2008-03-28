from Acquisition import aq_base, aq_inner, aq_parent
import ConfigParser, StringIO, tempfile, os, urllib, logging, re
from types import *
from zope import interface
from zope import component
from slc.publications import interfaces
from slc.publications.utils import _get_storage_folder
from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.config import RELATIONSHIP
from p4a.subtyper.interfaces import ISubtyper

import logging
logger = logging.getLogger('slc.publications')
# Event handler methods

def _findAbbrev(id, langs):
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
    return []


#def objectevent(obj, evt):
#    print [obj], [evt]

    
def object_initialized(obj, evt):
    """ EVENT
        An object has been added to the pub folder. We make sure that
        a) that files are subtyped
        b) translation relations are set
        I have no idea about the perormance of this. If adding objects in large pub folders 
        is too slow, consider disabling this.
    """
    if not interfaces.IPublicationContainerEnhanced.providedBy(obj.aq_parent):
        return

    portal_languages = getToolByName(obj, 'portal_languages')
    default_language = portal_languages.getDefaultLanguage()
    langs = portal_languages.getSupportedLanguages()
    
    # A mapping which stores {lang: obj} mappings under each common naming component
    # E.g. {'test': {'en': atfile1, 'de': atfile2}}
    GROUPS = {}
    
    subtyper = component.getUtility(ISubtyper)
    for child in obj.aq_parent.objectValues(['ATFile', 'ATBlob']):
        if subtyper.existing_type(child) is None:
            subtyper.change_type(child, 'slc.publications.Publication')
        comp = _findAbbrev(child.getId(), langs)
        if len(comp)==2:    # comp is a component tuple ('test', 'de')
            namemap = GROUPS.get(comp[0], {})
            namemap[comp[1]] = child
            GROUPS[comp[0]] = namemap
            if child.Language()!= comp[1]:
                child.setLanguage(comp[1])
            
    for key in GROUPS.keys():
        namemap = GROUPS[key]
        canonical = namemap.get(default_language, None)
        if canonical is None:
            continue
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
    if obj != obj.getCanonical():
        return
        
    interfaces.IPublication(obj).generateImage()
    
   
def updateChapterLinksForTranslation(ob):
    """ Read the chapternames and compair them to the Link objects inside the
        Publication for all translations. Add/Delete where they differ
        syncronizes the chapter links in ob to be compliant with the
        current portal languages and the chapters in getChapter
    """
    pw = getToolByName(ob, 'portal_workflow')

    adapter = component.getAdapter(ob, interfaces.IPublication)    
    chapters = ob.getField('chapters').getAccessor(ob)()
    #DEP: chapters = adapter.publication_data.get('chapters', [])

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
    if obj != obj.getCanonical():
        return
            
    translations = obj.getTranslations()

    for T in translations.keys():
        updateChapterLinksForTranslation(translations[T][0])
