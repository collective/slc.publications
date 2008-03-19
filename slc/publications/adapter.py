from Acquisition import aq_base, aq_inner, aq_parent
import ConfigParser, StringIO, tempfile, os, urllib, logging, interfaces, re
from types import *
from persistent.dict import PersistentDict
from zope import interface
from zope import component
from slc.publications import interfaces
from Products.ATContentTypes import interface as atctifaces
from Products.CMFCore.utils import getToolByName
from plone.app.blob.interfaces import IATBlobFile
from ComputedAttribute import ComputedAttribute
from DateTime import DateTime

try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces

from p4a.common.descriptors import atfield
from p4a.fileimage import DictProperty


class AnnotationPublication(object):
    """An IPublication adapter designed to handle ATCT based file content.
    """

    interface.implements(interfaces.IPublication)
    component.adapts(atctifaces.IATFile)           
    ANNO_KEY = 'slc.publications.AnnotationPublication'
                                               
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


@interface.implementer(interfaces.IPublication)
@component.adapter(atctifaces.IATFile)
def ATCTFilePublication(context):
    if not interfaces.IPublicationEnhanced.providedBy(context):
        return None
    return _ATCTPublication(context)

    
class _ATCTPublication(AnnotationPublication):
    """ 
    """
    interface.implements(interfaces.IPublication)
    component.adapts(atctifaces.IATFile)
       
    ANNO_KEY = 'slc.publications.ATCTFilePublication'

    file = None
    isbn = ''
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


    def _get_isbn(self):
        v = self.publication_data.get('isbn', '')
        return v
    def _set_isbn(self, v):
        self.publication_data['isbn'] = v
    isbn = property(_get_isbn, _set_isbn)

    def __str__(self):
        return '<slc.publication %s title=%s>' % (self.__class__.__name__, self.title)
    __repr__ = __str__



#class PDFHandler(object):
#    """ contains the methods to manipulate a pdf file """
#    
#
#    def parseMetadataUpload(self):
#        """
#        Does the parsing of an uploaded metadata file in configparser style and sets those metadata on existing publications.
#        """
#        request = self.REQUEST
#
#        sio = StringIO.StringIO(str(self.getMetadataUpload()))
#        meta = ConfigParser.ConfigParser()
#        meta.optionxform = str
#        meta.readfp(sio)
#        portal_languages = getToolByName(self.context, 'portal_languages')
#        langs = portal_languages.getSupportedLanguages()
#
#        ERR = []
#
#        if meta.has_section('default'):
#            err = _setMeta(TARGET=self, DATA=meta.items('default'))
#            if err:
#                ERR.append(err)
#        for section in meta.sections():
#            section = section.strip()
#
#            if len(section)>2 and section.find('.')>-1:  # we have a section of type [webanchor.en]
#                self._processChapterSection(section, meta)
#            else: # section is only a language abbrev like [en]
#                self._processMainSection(section, meta)
#
#        if ERR != []:                  
#            return "\n".join(ERR)
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
#    def _processMainSection(self, section, meta):
#        """ parse the contents for a language Version of the publication
#        """
#        portal_languages = getToolByName(self.context, 'portal_languages')
#        translations = self.getTranslations()
#        langs = portal_languages.getSupportedLanguages()
#        if section in langs:
#            F = translations.get(section, None)
#            if not F:
#                return
#            F = F[0]
#            _setMeta(TARGET=F, DATA=meta.items(section))
#
#    def _processChapterSection(self, section, meta):
#        """ parse the contents for a chapter Version of the publication
#        """
#        translations = self.getTranslations()
#        chapter, lang = section.rsplit('.')
#        F = translations.get(lang, None)
#        if not F:
#            return
#        F = F[0]
#        if hasattr(aq_base(F), chapter):
#            L = getattr(F, chapter)
#            _setMeta(TARGET=L, DATA=meta.items(section))
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
#    def _buildParsedParams(self, params):
#        """ helper """
#
#        np = {}
#        for key in params.keys():
#            key = key.strip()
#            value = params[key].strip()
#            if len(key)>2 and key[-2:]=='[]':
#                # we have a list notation
#                key = key[:-2]
#                elems = value.split(",")
#                nelems = []
#                for e in elems:
#                    nelems.append(e.strip())
#                if MDMAP[key]=='split':
#                    value = "\n".join(nelems)
#                else:
#                    value = nelems
#            np[key] = value
#        return np
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
##    def at_post_edit_script(self):
##        """ add the parse Properties mechanism in case the parse checkbox has been checked """
##        pw = self.portal_workflow
###        print self.REQUEST.keys()
###        if self.REQUEST.get('file_file', ''):
###            # fixing the filename
###            filename = IUserPreferredFileNameNormalizer(self.REQUEST).normalize(self.Title())
###            blob = self.file.get(self)
###            if blob is not None:
###                blob.setFilename(filename)
##
##        p = self.REQUEST.get('parsePDF', '')
##        if p == '1':
##            self.parsePDFProperties()
##            self.setParsePDF('0')
##        self.updateChapterLinks()
##        metafile = self.REQUEST.get('metadataUpload_file', '')
##        if metafile!='':
##            self.parseMetadataUpload()
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
#
#def updateChapterLinksForTranslation(ob):
#    """ syncronizes the chapter links in ob to be compliant with the
#        current portal languages and the chapters in getChapter
#    """
#    pw = getToolByName(ob, 'portal_workflow')
#
#    links = ob.objectIds('ATLink')
#    chapters = ob.getChapters()
#
#    # remove all links which are not named in getChapters
#    RM = []
#    for l in links:
#        if l not in chapters:
#            RM.append(l)
#    ob.manage_delObjects(ids=RM)
#
#    for c in chapters:
#        if c not in links:
#            ob.invokeFactory('Link', c)
#            L = getattr(ob, c)
#            L.setTitle(c)
#            L.setLanguage(ob.Language())
#            remurl = "/%s#%s" % ( urllib.unquote(ob.absolute_url(1)), c )
#            L.edit(remurl)
#            pw.doActionFor(L, 'publish', comment='Publish publication link %s in language %s.' % (c, ob.Language()))
#
#
#def _setMeta(TARGET, DATA):
#    """ sets metadata from a config section
#    """
#    if not TARGET:
#        return
#    params = {}
#    for elem in DATA:
#        if elem[1].strip()=='':
#            continue
#        params[elem[0].strip()] = elem[1].strip()
#
#    if TARGET.meta_type=='Link':
#        TARGET._editMetadata(title=params.get('title', TARGET.Title()),
#                      subject=params.get('subject', TARGET.Subject()),
#                      description=params.get('description', TARGET.Description()),
#                      contributors=params.get('contributors', TARGET.Contributors()),
#                      effective_date=params.get('effective_date', TARGET.EffectiveDate()),
#                      expiration_date=params.get('expiration_date', TARGET.ExpirationDate()),
#                      format=params.get('format', TARGET.Format()),
#                      language=params.get('language', TARGET.Language()),
#                      rights=params.get('rights', TARGET.Rights()),
#                      )
#    else:
#        TARGET._processForm(data=1, metadata=1, values=params)
#
#    TARGET.reindexObject()
#
#
#
#
#
#            