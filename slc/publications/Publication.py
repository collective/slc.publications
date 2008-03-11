# -*- coding: utf-8 -*-
#
# File: Publication.py
#
# GNU General Public License (GPL)
#

__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *

try:
    from Products.LinguaPlone.public import *
except ImportError:
    HAS_LINGUAPLONE = False
else:
    HAS_LINGUAPLONE = True

import ConfigParser, StringIO, tempfile, os, urllib, logging, interfaces
from zope.interface import implements
from Acquisition import aq_base, aq_inner, aq_parent
from ComputedAttribute import ComputedAttribute
from DateTime import DateTime

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.file import ATFileSchema

from slc.publications.config import *

from plone.app.blob.interfaces import IATBlob
from plone.app.blob.field import BlobField

logger = logging.getLogger('Publications::Publication')
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer


schema = Schema((

    StringField(
        name='title',
        widget=StringWidget(
            label="Title",
            description="The Title of this publication. It is used as backup if the real title of the underlying PDF file displayed here is not set. It will then show up in listings and the breadcrumb trail.",
            size=50,
            label_msgid='publications_label_title',
            description_msgid='publications_help_title',
            i18n_domain='publications',
        ),
        write_permission=permissions.ModifyPortalContent,
        searchable=1,
        label="Title",
    ),
    StringField(
        name='description',
        widget=TextAreaWidget(
            label="Description",
            description="The description of this publication. It is used as backup if the real description of the underlying PDF file displayed here is not set.",
            label_msgid='publications_label_description',
            description_msgid='publications_help_description',
            i18n_domain='publications',
        ),
        write_permission=permissions.ModifyPortalContent,
        searchable=1,
        label="Description",
    ),
    ImageField(
        name='coverImage',
        widget=ImageWidget(
            label="Cover Image",
            description="A thumbnail image of this publication. It is used in overview listings and the publication view.",
            label_msgid='publications_label_coverImage',
            description_msgid='publications_help_coverImage',
            i18n_domain='publications',
        ),
        languageIndependent=1,
        original_size=(75,106),
        storage=AttributeStorage(),
        write_permission=permissions.ModifyPortalContent,
        label="Cover Image",
    ),
    BooleanField(
        name='parsePDF',
        default=0,
        widget=BooleanField._properties['widget'](
            label="Parse PDF Properties",
            description="Select this to reparse all contained PDF files for properties. Note that this might overwrite the currently set values.",
            label_msgid='publications_label_parsePDF',
            description_msgid='publications_help_parsePDF',
            i18n_domain='publications',
        ),
        languageIndependent=1,
        schemata="parse",
        write_permission=permissions.ModifyPortalContent,
    ),
    StringField(
        name='author',
        widget=StringField._properties['widget'](
            label="Author",
            description="The author of this publication. It is used as backup if the real author of the underlying PDF file displayed here is not set.",
            size=60,
            label_msgid='publications_label_author',
            description_msgid='publications_help_author',
            i18n_domain='publications',
        ),
        languageIndependent=1,
        searchable=1,
        default=AUTHOR,
        write_permission=permissions.ModifyPortalContent,
        size=60,
    ),
    DateTimeField(
        name='publication_date',
        widget=CalendarWidget(
            show_hm=False,
            label="Publication date",
            description="The date when this publication has been published.",
            label_msgid='publications_label_publication_date',
            description_msgid='publications_help_publication_date',
            i18n_domain='publications',
        ),
        searchable=1,
        default=DateTime(),
        imports="from DateTime import DateTime",
        write_permission=permissions.ModifyPortalContent,
    ),
    StringField(
        name='ISBN_number',
        widget=StringWidget(
            label="ISBN-Number",
            description="The ISBN Number to order the publication - if available.",
            label_msgid='publications_label_ISBN_number',
            description_msgid='publications_help_ISBN_number',
            i18n_domain='publications',
        ),
        write_permission=permissions.ModifyPortalContent,
        searchable=1,
        label="ISBN-Number",
    ),
    StringField(
        name='order_id',
        widget=StringWidget(
            label="Order-ID",
            description="Type the Order-Id (OPOCE) used to order the publication at the EU Bookshop. If you do so, a link to the EU Bookshop will be generated automatically.",
            label_msgid='publications_label_order_id',
            description_msgid='publications_help_order_id',
            i18n_domain='publications',
        ),
        write_permission=permissions.ModifyPortalContent,
        searchable=1,
        label="Order-ID",
    ),
    BooleanField(
        name='forsale',
        widget=BooleanField._properties['widget'](
            label="Publication for sale?",
            description="Check this if the publication can be bought in the bookshop as well.",
            label_msgid='publications_label_forsale',
            description_msgid='publications_help_forsale',
            i18n_domain='publications',
        ),
        languageIndependent=1,
        write_permission=permissions.ModifyPortalContent,
    ),
    BlobField(
        name='file',
        widget=FileWidget(
            label="Publication PDF File",
            description="Upload the PDF file containing your publication here.",
            label_msgid='publications_label_file',
            description_msgid='publications_help_file',
            i18n_domain='publications',
        ),
        label="Publication PDF File",
        primary=1,
        write_permission=permissions.ModifyPortalContent,
    ),
    LinesField(
        name='chapters',
        widget=LinesField._properties['widget'](
            label="Chapters",
            description="Add one chapter name per line. This will generate link objects pointing to anchors with that name inside the pdf document. Make sure that the chapternames are the same as the pdf web anchor names on your pdf.",
            label_msgid='publications_label_chapters',
            description_msgid='publications_help_chapters',
            i18n_domain='publications',
        ),
        languageIndependent=1,
        schemata="parse",
        write_permission=permissions.ModifyPortalContent,
    ),
    FileField(
        name='metadataUpload',
        widget=FileField._properties['widget'](
            title="Upload metadata using a metadata.txt file",
            description="Upload a textfile (ini style) where each section is named after a language abbreviation and contains the metadata keys and values that should be set on the publication files.",
            label='Metadataupload',
            label_msgid='publications_label_metadataUpload',
            description_msgid='publications_help_metadataUpload',
            i18n_domain='publications',
        ),
        languageIndependent=1,
        schemata="parse",
        searchable=0,
        storage=AttributeStorage(),
        write_permission=permissions.ModifyPortalContent,
    ),
    BooleanField(
        name='parsePDF',
        default=0,
        widget=BooleanField._properties['widget'](
            label="Parse PDF Properties",
            description="Select this to reparse this PDF file for properties. Note that this might overwrite the currently set values.",
            label_msgid='publications_label_parsePDF',
            description_msgid='publications_help_parsePDF',
            i18n_domain='publications',
        ),
        languageIndependent=1,
        schemata="settings",
        write_permission=permissions.ModifyPortalContent,
    ),
    StringField(
        name='ownerPassword',
        widget=PasswordWidget(
            label="Fallback Owner Password",
            description="Enter the owner password for the PDF if you want to parse its metadata and it is secured. This password is used as fallback if no password is specified on the publication file object itself.",
            label_msgid='publications_label_ownerPassword',
            description_msgid='publications_help_ownerPassword',
            i18n_domain='publications',
        ),
        schemata="settings",
        write_permission=permissions.ModifyPortalContent,
    ),
    StringField(
        name='userPassword',
        widget=PasswordWidget(
            label="Fallback User Password",
            description="Enter the user password for the PDF if you want to parse its metadata and it is secured. This password is used as fallback if no password is specified on the publication file object itself.",
            label_msgid='publications_label_userPassword',
            description_msgid='publications_help_userPassword',
            i18n_domain='publications',
        ),
        schemata="settings",
        write_permission=permissions.ModifyPortalContent,
    ),
),
)


Publication_schema = ATFolderSchema.copy() + \
    schema.copy()


class Publication(ATFile, ATFolder):
    """ Publications Content Type
    """
    implements(interfaces.IPublication)
    security = ClassSecurityInfo()

    archetype_name  = 'Publication'
    portal_type     = 'Publication'
    meta_type       = 'Publication'
    _at_rename_after_creation = True

    schema = Publication_schema


    security.declareProtected(permissions.ModifyPortalContent, 'parseMetadataUpload')
    def parseMetadataUpload(self):
        """
        Does the parsing of an uploaded metadata file in configparser style and sets those metadata on existing publications.
        """
        request = self.REQUEST

        sio = StringIO.StringIO(str(self.getMetadataUpload()))
        meta = ConfigParser.ConfigParser()
        meta.optionxform = str
        meta.readfp(sio)
        langs = self.portal_languages.getSupportedLanguages()

        ERR = []

        if meta.has_section('default'):
            err = _setMeta(TARGET=self, DATA=meta.items('default'))
            if err:
                ERR.append(err)
        for section in meta.sections():
            section = section.strip()

            if len(section)>2 and section.find('.')>-1:  # we have a section of type [webanchor.en]
                self._processChapterSection(section, meta)
            else: # section is only a language abbrev like [en]
                self._processMainSection(section, meta)
        return ERR

    security.declarePublic('generateImage')
    def generateImage(self):
        """
        try safely to generate the cover image if pdftk and imagemagick are present
        """
        tmp_pdfin = tmp_pdfout = tmp_gifin = None
        try:
            mainpub = self.getCanonical()
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
            self.setCoverImage(coverdata)
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

    security.declareProtected(permissions.ModifyPortalContent, 'parsePDFProperties')
    def parsePDFProperties(self):
        """
        looks in PDF files for metadata and set it to the object
        """

        def attrFallback(*args, **kwargs):
            for a in args:
                if a.strip() !='':
                    return a


        # helper to do some logging
        def log(level, error):
            error = 'File: '+error
            zLOG.LOG('Publication Product', level, 'Parsing PDF Metadata', detail=error)

        # Fetch some PDF Parsing Properties from us or the Publication object, if not set
        opass = self._fetchAttrValue('getOwnerPassword').strip()
        upass = self._fetchAttrValue('getUserPassword').strip()


        statement = "pdfinfo -meta"
        if opass !="":
            statement += ' -opw ' + opass
        if upass !="":
            statement += ' -upw ' + upass

        # write a file and start pdfinfo
        tmp_pdf = tempfile.mkstemp(suffix='.pdf')
        fd = open(tmp_pdf[1], 'w')
        fd.write(str(self.getFile()))
        fd.close()

        statement += ' '+tmp_pdf[1]
        log(zLOG.BLATHER, 'Statement: '+statement)
        ph = os.popen4(statement)

        # get the result
        result = ph[1].read()
        log(zLOG.BLATHER, 'METADATA:\n%s ' % result)
        ph[0].close()
        ph[1].close()

        os.remove(tmp_pdf[1])

        # check for errors or encryption
        if result.startswith('Error'):
            error =  result.split('\n')[0]
            log(zLOG.ERROR, error)
        crypt_patt = re.compile('Encrypted:.*?copy:no', re.I)
        mobj = crypt_patt.search(result, 1)
        if mobj is not None:
            error = "Error: PDF is encrypted"
            log(zLOG.ERROR, error)

        # everything is fine, parse the meta data
        # caution: do not use the metalist, it's not unicode!
        METADATA = result.split('Metadata:')
        if len(METADATA)>1:
            metalist, metaxml = METADATA
        else:
            metalist, metaxml = (result, '')
        meta_map = {}

        # Hooray, metadata in the list part is not the same as the metadata in xml. Uff.
        # But metalist may not be unicode. Unbelievable. Lets get it anyway..
        list_map = {}
        for line in metalist.split("\n"):
            elems = line.split(":")
            if len (elems)>1:
                k = elems[0].strip()
                v = ":".join(elems[1:]).strip()
            else:
                continue
            list_map[k] = v
        # get metadata out of the xml-part
        patt_list = []
        patt_list.append( ('Keywords', "<pdf:Keywords>(.*?)</pdf:Keywords>") )
        patt_list.append( ('Keywords', "pdf:Keywords='(.*?)'") )
        patt_list.append( ('Language', "<pdf:Language>(.*?)</pdf:Language>") )
        patt_list.append( ('Language', "pdf:Language='(.*?)'") )
        patt_list.append( ('UUID', "xapMM:DocumentID='uuid:(.*?)'") )
        patt_list.append( ('UUID', 'rdf:about="uuid:(.*?)"') )
        patt_list.append( ('CreationDate', "xap:CreateDate='(.*?)'") )
        patt_list.append( ('CreationDate', "<xap:CreateDate>(.*?)</xap:CreateDate>") )
        patt_list.append( ('ModificationDate', "xap:ModifyDate='(.*?)'") )
        patt_list.append( ('ModificationDate', "<xap:ModifyDate>(.*?)</xap:ModifyDate>") )
        patt_list.append( ('MetadataDate', "xap:MetadataDate='(.*?)'") )
        patt_list.append( ('MetadataDate', "<xap:MetadataDate>(.*?)</xap:MetadataDate>") )
        patt_list.append( ('Rights Webstatement', "<xapRights:WebStatement>(.*?)</xapRights:WebStatement>") )
        patt_list.append( ('Producer', "<pdf:Producer>(.*?)</pdf:Producer>") )
        patt_list.append( ('CreatorTool', "<xap:CreatorTool>(.*?)</xap:CreatorTool>") )
        patt_list.append( ('Title', "<dc:title>(.*?)</dc:title>") )
        patt_list.append( ('Description', "<dc:description>(.*?)</dc:description>") )
        patt_list.append( ('Rights', "<dc:rights>(.*?)</dc:rights>") )
        patt_list.append( ('Format', "<dc:format>(.*?)</dc:format>") )
        patt_list.append( ('Creator', "<dc:creator>(.*?)</dc:creator>") )
        patt_list.append( ('OPOCE', "pdfx:OPOCE='(.*?)'") )
        patt_list.append( ('OPOCE', "<pdfx:OPOCE>(.*?)</pdfx:OPOCE>") )

        for patt in patt_list:
            pobj = re.compile(patt[1], re.I | re.S)
            mobj = pobj.search(metaxml, 1)
            if mobj is not None:
                value = re.sub('<.*?>', '', mobj.group(1))
                meta_map[patt[0].strip()] = value.strip()
            else:
                blather = "No matches for "+ str(patt[1])
                log(zLOG.BLATHER, blather)



        # get the user-defined meta-data
        add_patt = re.compile("pdfx:(.*?)='(.*?)'", re.I|re.S)
        for name, value in add_patt.findall(metaxml):
            meta_map[name.strip()] = value
        # Another format
        add_patt = re.compile("pdfx:(.*?)>(.*?)</pdfx:", re.I|re.S)
        for name, value in add_patt.findall(metaxml):
            meta_map[name.strip()] = value

        # make the author and subject to a tuple of values
        if type(meta_map.get('Author', '')) != TupleType:
            kw = meta_map.get('Author', '').split(";")
            meta_map['Author'] = tuple(kw)
        if type(meta_map.get('Keywords', '')) != TupleType:
            kw = meta_map.get('Keywords', '').split(";")
            meta_map['Keywords'] = tuple(kw)


        for key in meta_map:
            meta_data = meta_map[key]
            if not meta_data:
                continue
            # use the appropriate dublin-core mutators
            if key.upper() == "TITLE":
                if not (self.getTitle() and meta_data ==''):
                    self.setTitle(meta_data)
            elif key.upper() in ["SUBJECT", "KEYWORDS"]:
                self.setSubject(meta_data)
            elif key.upper() == "DESCRIPTION":
                self.setDescription(meta_data)
            elif key.upper() == "CONTRIBUTORS":
                self.setContributors(meta_data)
            elif key.upper() in ("MODIFICATION_DATE", "MODIFICATIONDATE"):
                self.setModificationDate(meta_data)
            elif key.upper() in ("EXPIRATION_DATE", "EXPIRATIONDATE"):
                self.setExpirationDate(meta_data)
            elif key.upper() == "EFFECTIVE_DATE":
                self.setEffectiveDate(meta_data)
            elif key.upper() == "RIGHTS":
                self.setRights(meta_data)
            elif key.upper() == "PUBLISHER":
                self.setPublisher(meta_data)
            elif key.upper() == "LANGUAGE":
                self.setLanguage(meta_data)
            elif key.upper() == "FORMAT":
                self.setFormat(meta_data)
            elif key.upper() == "OPOCE":
                self.setOrder_id(meta_data)
#                if len(meta_data) > 3 and self.getLanguage()=='':


    security.declarePublic('importCoverImage')
    def importCoverImage(self):
        """
        returns the cover image. If not present it looks for an image object inside with name cover_image.*
        """
        I = self.getCoverImage()
        if I:
            return I

        # try to generate
        check = self.generateImage()
        if check==1:
            I = self.getCoverImage()
            if I:
                return I

        return self.getCoverImage()

    security.declareProtected(permissions.View, 'getImage')
    def getImage(self):
        """ Returns the name of an image within this object that can be used as eye catcher """
        return "coverImage"

    def _processMainSection(self, section, meta):
        """ parse the contents for a language Version of the publication
        """
        translations = self.getTranslations()
        langs = self.portal_languages.getSupportedLanguages()
        if section in langs:
            F = translations.get(section, None)
            if not F:
                return
            F = F[0]
            _setMeta(TARGET=F, DATA=meta.items(section))

    def _processChapterSection(self, section, meta):
        """ parse the contents for a chapter Version of the publication
        """
        translations = self.getTranslations()
        chapter, lang = section.rsplit('.')
        F = translations.get(lang, None)
        if not F:
            return
        F = F[0]
        if hasattr(aq_base(F), chapter):
            L = getattr(F, chapter)
            _setMeta(TARGET=L, DATA=meta.items(section))

    security.declareProtected(permissions.ModifyPortalContent, 'downloadMetadata')
    def downloadMetadata(self):
        """ Download the uploaded metadata """
        return self.getCanonical().getField('metadataUpload').download(self)

    security.declareProtected(permissions.ModifyPortalContent, 'viewMetadata')
    def viewMetadata(self):
        """ returns the currently safed metadata file """
        return self.getMetadataUpload()

    security.declareProtected(permissions.View, 'Publisher')
    def Publisher(self):
        """Dublin Core element - resource publisher
           This is a very local change to force the Publisher to be the same for all pubs.
        """
        portal = self.portal_url.getPortalObject()
        publisher = portal.Publisher()
        return publisher or 'No publisher'

    def _buildParsedParams(self, params):
        """ helper """

        np = {}
        for key in params.keys():
            key = key.strip()
            value = params[key].strip()
            if len(key)>2 and key[-2:]=='[]':
                # we have a list notation
                key = key[:-2]
                elems = value.split(",")
                nelems = []
                for e in elems:
                    nelems.append(e.strip())
                if MDMAP[key]=='split':
                    value = "\n".join(nelems)
                else:
                    value = nelems
            np[key] = value
        return np

    def getLinksByLanguage(self, language=None):
        """ returns a list of Chapter links by language
        """
        lang_tool = self.portal_languages
        if not language:
            language = self.Language()
        pc = self.portal_catalog
        res = pc(portal_type='Link', path="/".join(self.getPhysicalPath()), Language=language)
        return res

    def _fetchAttrValue(self, attrname):
        """ Tries to get an attribute Value from Publication if not set on File itself """
        try:
            val = getattr(self, attrname)()
        except:
            val = ''
        if val.strip() != '':
            return val
        try:
            val = getattr(aq_parent(self), attrname)()
        except:
            val = ''
        return val

    def at_post_edit_script(self):
        """ add the parse Properties mechanism in case the parse checkbox has been checked """
        pw = self.portal_workflow
#        print self.REQUEST.keys()
#        if self.REQUEST.get('file_file', ''):
#            # fixing the filename
#            filename = IUserPreferredFileNameNormalizer(self.REQUEST).normalize(self.Title())
#            blob = self.file.get(self)
#            if blob is not None:
#                blob.setFilename(filename)

        p = self.REQUEST.get('parsePDF', '')
        if p == '1':
            self.parsePDFProperties()
            self.setParsePDF('0')
        self.updateChapterLinks()
        metafile = self.REQUEST.get('metadataUpload_file', '')
        if metafile!='':
            self.parseMetadataUpload()

    def updateChapterLinks(self):
        """ Read the chapternames and compair them to the Link objects inside the
            Publication for all translations. Add/Delete where they differ
        """

        translations = self.getTranslations()

        for T in translations.keys():
            updateChapterLinksForTranslation(translations[T][0])

    def objectIds(self, spec=None):
        return ATFolder.objectIds(self, spec)

    def objectValues(self, spec=None):
        return ATFolder.objectValues(self, spec)

    def objectItems(self, spec=None):
        return ATFolder.objectItems(self, spec)

    security.declareProtected(permissions.View, 'get_size')
    def get_size(self):
        """ returns the size """
        return self.getFile().get_size()

    security.declareProtected(permissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline """
        field = self.getPrimaryField()

        return field.download(self, REQUEST, RESPONSE)



registerType(Publication, PROJECTNAME)
# end of class Publication




def updateChapterLinksForTranslation(ob):
    """ syncronizes the chapter links in ob to be compliant with the
        current portal languages and the chapters in getChapter
    """
    pw = getToolByName(ob, 'portal_workflow')

    links = ob.objectIds('ATLink')
    chapters = ob.getChapters()

    # remove all links which are not named in getChapters
    RM = []
    for l in links:
        if l not in chapters:
            RM.append(l)
    ob.manage_delObjects(ids=RM)

    for c in chapters:
        if c not in links:
            ob.invokeFactory('Link', c)
            L = getattr(ob, c)
            L.setTitle(c)
            L.setLanguage(ob.Language())
            remurl = "/%s#%s" % ( urllib.unquote(ob.absolute_url(1)), c )
            L.edit(remurl)
            pw.doActionFor(L, 'publish', comment='Publish publication link %s in language %s.' % (c, ob.Language()))


def _setMeta(TARGET, DATA):
    """ sets metadata from a config section
    """
    if not TARGET:
        return
    params = {}
    for elem in DATA:
        if elem[1].strip()=='':
            continue
        params[elem[0].strip()] = elem[1].strip()

    if TARGET.meta_type=='Link':
        TARGET._editMetadata(title=params.get('title', TARGET.Title()),
                      subject=params.get('subject', TARGET.Subject()),
                      description=params.get('description', TARGET.Description()),
                      contributors=params.get('contributors', TARGET.Contributors()),
                      effective_date=params.get('effective_date', TARGET.EffectiveDate()),
                      expiration_date=params.get('expiration_date', TARGET.ExpirationDate()),
                      format=params.get('format', TARGET.Format()),
                      language=params.get('language', TARGET.Language()),
                      rights=params.get('rights', TARGET.Rights()),
                      )
    else:
        TARGET._processForm(data=1, metadata=1, values=params)

    TARGET.reindexObject()





