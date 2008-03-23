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

try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces

from p4a.common.descriptors import atfield
from p4a.fileimage import DictProperty

from slc.publications.config import STORAGE_FOLDER, ALLOWED_TYPES

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

    ANNO_KEY = 'slc.publications.PublicationAnnotation'
                                               
    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.publication_data = annotations.get(self.ANNO_KEY, None)
        if self.publication_data is None:
            self.publication_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.publication_data
            

    title = DictProperty(interfaces.IPublication['title'], 'publication_data')
    description = DictProperty(interfaces.IPublication['description'], 'publication_data')
    cover_image = DictProperty(interfaces.IPublication['cover_image'], 'publication_data')
    file = DictProperty(interfaces.IPublication['file'], 'publication_data')
    author = DictProperty(interfaces.IPublication['author'], 'publication_data')
    publication_date = DictProperty(interfaces.IPublication['publication_date'], 'publication_data')
    isbn = DictProperty(interfaces.IPublication['isbn'], 'publication_data')
    order_id = DictProperty(interfaces.IPublication['order_id'], 'publication_data')
    for_sale = DictProperty(interfaces.IPublication['for_sale'], 'publication_data')
    chapters = DictProperty(interfaces.IPublication['chapters'], 'publication_data')
    metadata_upload = DictProperty(interfaces.IPublication['metadata_upload'], 'publication_data')
    owner_password = DictProperty(interfaces.IPublication['owner_password'], 'publication_data')
    user_password = DictProperty(interfaces.IPublication['user_password'], 'publication_data')
    
          
    # ??? necessary?
    file = None
    metadata_upload = None
    cover_image = None

    title = atfield('title', 'context')
    description = atfield('description', 'context')

    def _get_file(self):
        field = self.context.getPrimaryField()
        return field.getEditAccessor(self.context)()
    def _set_file(self, v):
        if v != interfaces.IPublication['file'].missing_value:
            field = self.context.getPrimaryField()
            field.getMutator(self.context)(v)
    file = property(_get_file, _set_file)


    def _get_cover_image(self):
        v = self.publication_data.get('cover_image', None)
        if v == None or v.get_size() == 0:
            return None
        return v
    def _set_cover_image(self, v):
        if v == interfaces.IPublication['cover_image'].missing_value:
            return
        upload = v
        if isinstance(upload, ofsimage.Image):
            image = upload
        else:
            image = ofsimage.Image(id=upload.filename,
                                   title=upload.filename,
                                   file=upload)
        self.publication_data['cover_image'] = image
    cover_image = property(_get_cover_image, _set_cover_image)


    def _get_metadata_upload(self):
        v = self.publication_data.get('metadata_upload', None)
        if v == None:
            return None
        return v
    def _set_metadata_upload(self, v):
        if v == interfaces.IPublication['metadata_upload'].missing_value:
            return
        upload = v
        if isinstance(upload, ofsimage.File):
            file = upload
        else:
            file = ofsimage.File(id=upload.filename,
                                   title=upload.filename,
                                   file=upload)
        self.publication_data['metadata_upload'] = file
    metadata_upload = property(_get_metadata_upload, _set_metadata_upload)

    def __str__(self):
        return '<slc.publication %s title=%s>' % (self.__class__.__name__, self.title)
    __repr__ = __str__


    def parsePDFProperties(self):
        """ parse the properties from the file contents and set them on the object """
        pdfparser = component.getUtility(IPDFParser)
        meta = pdfparser.parse(self._get_file())
     

        

                   
# Eventhandler
        
def _get_storage_folder(ob):

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
    chapters = adapter.publication_data['chapters']

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
            pw.doActionFor(L, 'publish', comment='Publish publication link %s in language %s.' % (c, ob.Language()))   


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
    
    

#class PDFHandler(object):
#    """ contains the methods to manipulate a pdf file """
#    

#            
#            
#    security.declarePublic('generateImage')
#    def generateImage(self):
#        """
#        try safely to generate the cover image if pdftk and imagemagick are present
#        """
#        tmp_pdfin = tmp_pdfout = tmp_gifin = None
#        try:
#            mainpub = self.context.getCanonical()
#            data = str(mainpub.getFile())
#            if not data:
#                return 0
#            tmp_pdfin = tempfile.mkstemp(suffix='.pdf')
#            tmp_pdfout = tempfile.mkstemp(suffix='.pdf')
#            tmp_gifin = tempfile.mkstemp(suffix='.gif')
#            fhout = open(tmp_pdfout[1], "w")
#            fhimg = open(tmp_gifin[1], "r")
#            fhout.write(data)
#            fhout.seek(0)
#            cmd = "pdftk %s cat 1 output %s" %(tmp_pdfout[1], tmp_pdfin[1])
#            logger.info(cmd)
#            res = os.popen(cmd)
#            result = res.read()
#            if result:
#                logger.warn("popen-1: %s" % (result))
#            cmd = "convert %s -resize 80x113 %s" %(tmp_pdfin[1], tmp_gifin[1])
#            res = os.popen(cmd)
#            result = res.read()
#            if result:
#                logger.warn("popen-2: %s" % (result))
#            #fhimg.seek(0)
#            coverdata = fhimg.read()
#            self._set_cover_image(coverdata)
#            status = 1
#        except Exception, e:
#            logger.warn("generateImage: Could not autoconvert because: %s" %e)
#            status = 0
#
#        # try to clean up
#        if tmp_pdfin is not None:
#            try: os.remove(tmp_pdfin[1])
#            except: pass
#        if tmp_pdfout is not None:
#            try: os.remove(tmp_pdfout[1])
#            except: pass
#        if tmp_gifin is not None:
#            try: os.remove(tmp_gifin[1])
#            except: pass
#
#        return status
#
#    def _set_cover_image(self, data):
#        """ implemented by the adapter """
#        pass
#
#
#
#    security.declarePublic('importCoverImage')
#    def importCoverImage(self):
#        """
#        returns the cover image. If not present it looks for an image object inside with name cover_image.*
#        """
#        I = self._get_cover_image()
#        if I:
#            return I
#
#        # try to generate
#        check = self.generateImage()
#        if check==1:
#            I = self._get_cover_image()
#            if I:
#                return I
#
#        return self._get_cover_image()
#
#    security.declareProtected(permissions.View, 'getImage')
#    def getImage(self):
#        """ Returns the name of an image within this object that can be used as eye catcher """
#        return "coverImage"

#
#    security.declareProtected(permissions.ModifyPortalContent, 'downloadMetadata')
#    def downloadMetadata(self):
#        """ Download the uploaded metadata """
#        return self.context.getCanonical().getField('metadataUpload').download(self)
#
#    security.declareProtected(permissions.ModifyPortalContent, 'viewMetadata')
#    def viewMetadata(self):
#        """ returns the currently safed metadata file """
#        return self.getMetadataUpload()
#

#
#    def getLinksByLanguage(self, language=None):
#        """ returns a list of Chapter links by language
#        """
#        if not language:
#            language = self.Language()
#        pc = self.portal_catalog
#        res = pc(portal_type='Link', path="/".join(self.getPhysicalPath()), Language=language)
#        return res
#
#    def _fetchAttrValue(self, attrname):
#        """ Tries to get an attribute Value from Publication if not set on File itself """
#        try:
#            val = getattr(self, attrname)()
#        except:
#            val = ''
#        if val.strip() != '':
#            return val
#        try:
#            val = getattr(aq_parent(self), attrname)()
#        except:
#            val = ''
#        return val
#

#    def updateChapterLinks(self):
#        """ Read the chapternames and compair them to the Link objects inside the
#            Publication for all translations. Add/Delete where they differ
#        """
#
#        translations = self.getTranslations()
#
#        for T in translations.keys():
#            updateChapterLinksForTranslation(translations[T][0])    
#            
#            
            
