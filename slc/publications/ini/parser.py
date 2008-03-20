import tempfile, logging, os, re, ConfigParser, StringIO
from types import *
from interfaces import IINIParser
from zope import interface
from zope import component
from zope.formlib import form
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('slc.publications.ini')

class INIParser(object):
    """ parses metadata and chapters from ini files """

    interface.implements(IINIParser)
    
    def parse(self, ini):
        """ parses the given ini file and writes on the object """
        
        request = self.REQUEST
        site = getSite()
        
        sio = StringIO.StringIO(str(ini))
        meta = ConfigParser.ConfigParser()
        meta.optionxform = str
        meta.readfp(sio)
        portal_languages = getToolByName(site, 'getToolByName')
        langs = portal_languages.getSupportedLanguages()

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

        if ERR != []:                  
            return "\n".join(ERR)        

    def updateChapterLinks(self):
        """ Read the chapternames and compair them to the Link objects inside the
            Publication for all translations. Add/Delete where they differ
        """

        translations = self.getTranslations()

        for T in translations.keys():
            updateChapterLinksForTranslation(translations[T][0])


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
        
        
        
    def retrieve(self, context):
        """ """
        meta = ConfigParser.ConfigParser()
        meta.optionxform = str
        portal_languages = getToolByName(context, 'portal_languages')
        default_language = portal_languages.getDefaultLanguage()
        
        
        from slc.publications.interfaces import IPublication
        form_fields = form.FormFields(IPublication)

        # the main object
        canonical = context.getCanonical()
        adapted = IPublication(canonical)
        for attr in form_fields:
            value = attr.field.get(adapted)
            value = _vTs(value)
            if not value: 
                continue
            meta.set('DEFAULT', attr.field.getName(), value)
        
            


        # the translations
        translations = canonical.getTranslations()
        for translation in translations.keys():
            if not translation:
                continue
                
            meta.add_section(translation)      
            adapted = IPublication(translations[translation][0])

            for attr in form_fields:
                value = attr.field.get(adapted)
                value = _vTs(value)
                if not value: 
                    continue
                meta.set( translation, attr.field.getName(), value )
        
        
                 
        
        
        
        
        out = StringIO.StringIO()
        meta.write(out)
        
        return out.getvalue()
        
        
def _vTs(value):
    """ parse a value into a string representation in one line """
    if type(value) in [StringType, UnicodeType]:
        return value
    elif type(value) in [IntType, FloatType]:
        return value
    elif type(value) in [ListType, TupleType]:
        return ";".join(value)
        
    return None
            
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





        