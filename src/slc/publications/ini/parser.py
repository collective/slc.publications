import tempfile, logging, os, re, ConfigParser, StringIO
from types import *
from interfaces import IINIParser
from zope import interface
from zope import component
from zope.formlib import form
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from slc.publications.utils import _get_storage_folder


logger = logging.getLogger('slc.publications.ini')

class INIParser(object):
    """ parses metadata and chapters from ini files """

    interface.implements(IINIParser)
    
    ##### Parser
    
    def parse(self, ini):
        """ parses the given ini file and writes on the object """
        site = getSite()
        portal_languages = getToolByName(site, 'portal_languages')
        langs = portal_languages.getSupportedLanguages()
        
        sio = None
        if type(ini) in [StringType, UnicodeType]:
            sio = StringIO.StringIO(ini)
        elif type(ini) == FileType:
            sio = ini
        elif type(ini) == InstanceType and ini.__class__ == StringIO.StringIO:
            sio = ini
        else:
            raise TypeError, 'Cannot determine type of ini paramenter'
        sio.seek(0)
        meta = ConfigParser.ConfigParser()
        meta.optionxform = str
        meta.readfp(sio)
        
        metadata = {}
        
        for section in meta.sections():
            section = section.strip()
            if len(section)>2 and section.find('.')>-1:  # we have a section of type [webanchor.en]
                (chapter,lang) = section.rsplit(".", 1)
                langmap = metadata.get(lang, {})
                langmap[chapter] = _getMeta( meta.items(section) )
                metadata[lang] = langmap
            else: # section is a language abbrev like [en] ad therefore a main section
                lang = section
                langmap = metadata.get(lang, {})
                langmap[''] = _getMeta( meta.items(section) ) 
                metadata[lang] = langmap 
        
        return metadata
        
    ######## Retriever        
        
    def retrieve(self, context):
        """ retrieves the metadata from the object, all translations and all chapters """
        meta = ConfigParser.ConfigParser()
        meta.optionxform = str
        portal_languages = getToolByName(context, 'portal_languages')
        default_language = portal_languages.getDefaultLanguage()
        
        
        from slc.publications.interfaces import IPublication
        #form_fields = form.FormFields(IPublication)

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

            schema = t_ob.Schema()
            
            for key in schema.keys():
                value = t_ob.getField(key).getAccessor(t_ob)()
                value = _vTs(value)
                if not value or key=='id':
                    continue
                meta.set(lang, key, value )          

       
            _retrieve_chapter_attrs(adapted, meta)
        
        out = StringIO.StringIO()
        meta.write(out)
        
        return out.getvalue()
       
       
       
def _retrieve_chapter_attrs(ob, meta):
    """ get the attributes for the chapters """
    portal_languages = getToolByName(ob.context, 'portal_languages')
    default_language = portal_languages.getDefaultLanguage()
    suffix = ob.context.Language() or default_language

    additionals = _get_storage_folder(ob.context)
    #DEP: chapters = ob.publication_data.get('chapters', [])
    chapters = ob.context.getField('chapters').getAccessor(ob)()                
    
    for chapter in chapters:
        section_name = "%s.%s" % (chapter, suffix)
        link = getattr(additionals, chapter)
        meta.add_section( section_name )   

        schema = link.Schema()
        for key in schema.keys():
            value = link.getField(key).getAccessor(link)()
            #value = getattr(link, schema[key].accessor)()           
            value = _vTs(value)
            if not value or key=='id':
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
            

def _getMeta(section):
    """ convert meta info """
    params = {}
    for elem in section:
        key = elem[0].strip()
        value = elem[1].strip()

        if key=='' or value=='':
            continue
            
        if len(key)>2 and key[-2:]=='[]':
            # we have a list notation
            key = key[:-2]
            if ";" in value:
                elems = value.split(";")
            else:
                elems = value.split(",")
                
            value = []
            for e in elems:
                value.append(e.strip())
            value = tuple(value)
            
        params[key] = value    
    return params

