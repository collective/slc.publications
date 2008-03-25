import App.Common
from Acquisition import aq_base, aq_inner, aq_parent
from OFS import Image as ofsimage, ObjectManager
from Products.ATContentTypes.content import folder as atctfolder
import ConfigParser, StringIO, tempfile, os, urllib, logging, interfaces, re
from types import *
from persistent.dict import PersistentDict
from zope import interface
from zope import component
from slc.publications import interfaces
from Products.ATContentTypes import interface as atctifaces
from Products.CMFCore.utils import getToolByName
from ComputedAttribute import ComputedAttribute
from DateTime import DateTime

from slc.publications.pdf.interfaces import IPDFParser
from slc.publications.ini.interfaces import IINIParser
from slc.publications.config import ALLOWED_TYPES

try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces

from p4a.common.descriptors import atfield
from p4a.fileimage import DictProperty
from p4a.subtyper.interfaces import ISubtyper

import logging
logger = logging.getLogger('slc.publications')

@interface.implementer(interfaces.IPublication)
@component.adapter(atctifaces.IATFile)
def ATCTFilePublication(context):
    if not interfaces.IPublicationEnhanced.providedBy(context):
        return None
    return _ATCTPublication(context)

_marker=[]

class _ATCTPublication(object):
    """ 
    """
    interface.implements(interfaces.IPublication)
    component.adapts(atctifaces.IATFile)
                                               
    def __init__(self, context):
        self.context = context

    def __str__(self):
        return '<slc.publication %s title=%s>' % (self.__class__.__name__, self.title)
    __repr__ = __str__


    def editChapter(self, chapter, metadata):
        """ add/edit a link object with the given chapter name and modify its metadata """
        additionals = _get_storage_folder(self.context)
        C = getattr(additionals, chapter, None)
        if C is None:
            return
        C.processForm(data=1, metadata=1, values=metadata)
        
    def setMetadataMap(self, metadata):
        """ sets a simple map with metadata on the current context. """
        self.context.processForm(data=1, metadata=1, values=metadata)
        #DEP: self._setPublicationMetadata(metadata)
    
    def setMetadataIniMap(self, metadata):
        """ Given a complex metadata map from e.g. the ini parser set the metadata on all translations and chapters """
        translations = self.context.getTranslations()
        canonical = self.context.getCanonical()
        subtyper = component.getUtility(ISubtyper)
        
        for lang in metadata.keys():
            if lang == 'default': 
                continue    # we skip the default section

            if translations.has_key(lang):
                translation = translations[lang][0]
                if not subtyper.existing_type(translation) or \
                   subtyper.existing_type(translation).name != 'slc.publications.Publication':
                   subtyper.change_type(translation, 'slc.publications.Publication')
                   
            else:
                canonical.addTranslation(lang)
                translation = canonical.getTranslation(lang)
                # make the translation a publication as well
                subtyper.change_type(translation, 'slc.publications.Publication')
                
                translations[lang] = [translation, None]

            langmap = metadata[lang]
            adapter = interfaces.IPublication(translation)
            for key in langmap.keys():
                if key == '':
                    adapter.setMetadataMap(langmap[key])
                    #DEP: adapter._setPublicationMetadata(langmap[key])
                else:
                    adapter.editChapter(key, langmap[key])

    def generateImage(self):
        """
        try safely to generate the cover image if pdftk and imagemagick are present
        """
        tmp_pdfin = tmp_pdfout = tmp_gifin = None
        try:
            mainpub = self.context.getCanonical()
            data = str(mainpub.getFile())
            if not data:
                return 0
            tmp_pdfin = tempfile.mkstemp(suffix='.pdf')
            tmp_pdfout = tempfile.mkstemp(suffix='.pdf')
            tmp_gifin = tempfile.mkstemp(suffix='.gif')
            fhout = open(tmp_pdfout[1], "w")
            fhimg = open(tmp_gifin[1], "r")
            fhout.write(data)
            fhout.seek(0)
            cmd = "pdftk %s cat 1 output %s" %(tmp_pdfout[1], tmp_pdfin[1])
            logger.info(cmd)
            res = os.popen(cmd)
            result = res.read()
            if result:
                logger.warn("popen-1: %s" % (result))
            cmd = "convert %s -resize 80x113 %s" %(tmp_pdfin[1], tmp_gifin[1])
            res = os.popen(cmd)
            result = res.read()
            if result:
                logger.warn("popen-2: %s" % (result))
            #fhimg.seek(0)
            coverdata = fhimg.read()
            self.context.getField('cover_image').getMutator(self.context)(coverdata)
            status = 1
        except Exception, e:
            logger.warn("generateImage: Could not autoconvert because: %s" %e)
            status = 0

        # try to clean up
        if tmp_pdfin is not None:
            try: os.remove(tmp_pdfin[1])
            except: pass
        if tmp_pdfout is not None:
            try: os.remove(tmp_pdfout[1])
            except: pass
        if tmp_gifin is not None:
            try: os.remove(tmp_gifin[1])
            except: pass

        return status


# Eventhandler
        
def generate_image(obj, evt):
    """ EVENT
        called on objectmodified. Tries to generate the cover image. 
    """
    # Make sure we execute this only on the canonical
    if obj != obj.getCanonical():
        return
        
    interfaces.IPublication(obj).generateImage()
        
def _get_storage_folder(ob):
    """ Helper Method to fetch the folder containing additional material like chapters and further pdf parts 
    """
    additionals_id = ob.getId().replace('.pdf', '')+'_data'

    if additionals_id == ob.getId():
        raise AttributeError, "Cannot get a unique name for the additionals folder"
        
    container = aq_parent(aq_inner(ob)) 
    
    if additionals_id not in container.objectIds():
        container.invokeFactory("Folder", additionals_id)
        additionals = getattr(container, additionals_id)
        additionals.setTitle('Additional material on %s' % ob.Title())
        additionals.setExcludeFromNav(True)
        additionals.reindexObject()
    else:    
        additionals = getattr(container, additionals_id)

    return additionals    
   
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
    
    

            
