import tempfile, logging, os, re, ConfigParser, StringIO
from types import *
from interfaces import IINIParser
from zope import interface
from zope import component
from zope.formlib import form
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from slc.publications.adapter import _get_storage_folder


logger = logging.getLogger('slc.publications.ini')

class INIParser(object):
    """ parses metadata and chapters from ini files """

    interface.implements(IINIParser)
    
    ##### Parser
    
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
        
    ######## Retriever        
        
        
       
        
    def retrieve(self, context):
        """ retrieves the metadata from the object, all translations and all chapters """
        meta = ConfigParser.ConfigParser()
        meta.optionxform = str
        portal_languages = getToolByName(context, 'portal_languages')
        default_language = portal_languages.getDefaultLanguage()
        
        
        from slc.publications.interfaces import IPublication
        form_fields = form.FormFields(IPublication)

        # the main object
        canonical = context.getCanonical()
            


        # the translations
        translations = canonical.getTranslations()
        for translation in translations.keys():
            if not translation:
                lang = canonical.Language() or default_language
            else:
                lang = translation
                            
            t_ob = translations[translation][0]
                    
            meta.add_section(lang)      
            adapted = IPublication(t_ob)

            for attr in form_fields:
                value = attr.field.get(adapted)
                value = _vTs(value)
                if not value: 
                    continue
                meta.set( lang, attr.field.getName(), value )
        
            _retrieve_chapter_attrs(adapted, meta)
        
                 
        
        
        
        
        out = StringIO.StringIO()
        meta.write(out)
        
        return out.getvalue()
       
       
       
def _retrieve_chapter_attrs(ob, meta):
    portal_languages = getToolByName(ob.context, 'portal_languages')
    default_language = portal_languages.getDefaultLanguage()
    suffix = ob.context.Language() or default_language

    additionals = _get_storage_folder(ob.context)
    chapters = ob.publication_data.get('chapters', [])
                    
    
    for chapter in chapters:
        section_name = "%s.%s" % (chapter, suffix)
        link = getattr(additionals, chapter)
        meta.add_section( section_name )   

        schema = link.Schema()
        for key in schema.keys():
            value = getattr(link, schema[key].accessor)()           
            value = _vTs(value)
            if not value:
                continue
            meta.set(section_name, key, value )          
            
               
        
def _vTs(value):
    """ parse a value into a string representation in one line """
    if type(value) in [StringType, UnicodeType]:
        return value
    elif type(value) in [IntType, FloatType]:
        return value
    elif type(value) in [ListType, TupleType]:
        return ";".join(value)
        
    return None
            
        
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





        