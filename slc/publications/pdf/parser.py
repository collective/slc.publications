from Acquisition import aq_base, aq_inner
import tempfile, logging, os, re, StringIO
from types import *
from interfaces import IPDFParser
from zope import interface
from zope import component
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('slc.publications.pdf')

class PDFParser(object):
    """ parses metadata from pdf files """

    interface.implements(IPDFParser)
    
    def parse(self, pdf, owner_password='', user_password=''):
        """ parses the given pdf file and returns a mapping of attributes """
        
        # This will store the parsed metadata
        META_MAP = {}
      
        statement = "pdfinfo -meta"
        if owner_password !="":
            statement += ' -opw ' + owner_password
        if user_password !="":
            statement += ' -upw ' + user_password

        # pdfinfo needs to work on a file. Write the file and start pdfinfo
        tmp_pdf = tempfile.mkstemp(suffix='.pdf')
        fd = open(tmp_pdf[1], 'w')
        if type(pdf) == InstanceType and pdf.__class__ == StringIO.StringIO:
            fd.write( pdf.getvalue() )
        elif type(pdf) in [StringType, UnicodeType]:
            fd.write( pdf )
        elif type(pdf) == FileType:
            fd.write( str(pdf) )
        else:
            raise ValueError, 'Cannot determine type of pdf variable'
        fd.close()

        statement += ' '+tmp_pdf[1]
        logger.debug('pdfinfo commandline: %s' % statement)
        ph = os.popen4( statement )

        # get the result
        result = ph[1].read()
        logger.debug('metadata extracted by pdfinfo :\n--------------------------------\n%s ' % result)

        ph[0].close()
        ph[1].close()
        
        # cleanup the tempfile
        os.remove(tmp_pdf[1])

        # check for errors or encryption
        if result.startswith('Error: No paper information available - using defaults'):
            # Irritating error if libpaper is not configured correctly. For our case this is irrelevant
            pass
        elif result.startswith('Error'):
            error =  result.split('\n')[0]
            logger.error("Error in pdfinfo conversion: %s" % error)
            return False
            
        crypt_patt = re.compile('Encrypted:.*?copy:no', re.I)
        mobj = crypt_patt.search(result, 1)
        if mobj is not None:
            error = "Error: PDF is encrypted"
            logger.error(error)
            return False
            
        # Everything seems fine, parse the metadata
        # Caution: do not use the metalist, it's not unicode!
        # Note that pdfinfo returns a ini style list and an xml version.
        METADATA = result.split('Metadata:')
        if len(METADATA)>1:
            metalist, metaxml = METADATA
        else:
            metalist, metaxml = (result, '')


        # Hooray, metadata in the list part is not the same as the metadata in xml. Uff.
        # But metalist may not be unicode. Lets get it anyway..

#        list_map = {}
#        for line in metalist.split("\n"):
#            elems = line.split(":")
#            if len (elems)>1:
#                k = elems[0].strip()
#                v = ":".join(elems[1:]).strip()
#            else:
#                continue                
#            list_map[k] = v
            
            
        # Get metadata out of the xml-part
        # XXX: There is probably a proper definition what to expect here. 
        # If would be a good idea to make this generic
        # It even would be smart to use an xml parser here.
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
                value = re.sub('<.*?>', '', mobj.group(1)).strip()
                # acrobat separates keywords with a semicolon. There is no datatyping
                # so we assume it is a list if a semicolon appears.
                if ";" in value:
                    kw = value.split(";")
                    value = tuple([x.strip() for x in kw])
                    
                META_MAP[patt[0].strip().lower()] = value
            else:
                logger.debug("No matches for "+ str(patt[1]))


        # Get the user-defined meta-data
        add_patt = re.compile("pdfx:(.*?)='(.*?)'", re.I|re.S)

        for name, value in add_patt.findall(metaxml):
            # acrobat separates keywords with a semicolon. There is no datatyping
            # so we assume it is a list if a semicolon appears.
            if ";" in value:
                kw = value.split(";")
                value = tuple([x.strip() for x in kw])
            META_MAP[name.strip().lower()] = value

        # And another format
        add_patt = re.compile("pdfx:(.*?)>(.*?)</pdfx:", re.I|re.S)
        for name, value in add_patt.findall(metaxml):
            # acrobat separates keywords with a semicolon. There is no datatyping
            # so we assume it is a list if a semicolon appears.
            if ";" in value:
                kw = value.split(";")
                value = tuple([x.strip() for x in kw])
            META_MAP[name.strip().lower()] = value
        
        
        # If the language is given in the filename extension, we consider that as 
        # most explicit
        
        l = self._guessLanguage(pdf)
        if l and not META_MAP.has_key('language'):
            META_MAP['language'] = l
        
        # Finally we'll do some plone specific rewritings
        # It would be smart to hook some kind of adapter here so that one can define his own rewritings 
        if META_MAP.has_key('keywords'):
            META_MAP['subject_keywords'] = list(META_MAP['keywords'])
        
        return META_MAP


    def _guessLanguage(self, file):
        """
        try to find a language abbreviation in the string
        acceptable is a two letter language abbreviation at the start of the string followed by an _
        or at the end of the string prefixed by an _ just before the extension
        """
        if hasattr(file, 'filename'):
            filename = file.filename
        elif hasattr(file, 'id'):
            filename = file.id
        elif hasattr(file, 'getId'):
            filename = file.getId
        else:
            return None

        if callable(filename):
            filename = filename()            
                    
        def findAbbrev(id):
            if len(id)>3 and id[2] in ['_', '-']:
                lang = id[0:2].lower()
                if lang in langs:
                    return lang
            if len(id)>3 and '.' in id:
                elems = id.split('.')
                filename = ".".join(elems[:-1])
                if len(filename)>3 and filename[-3] in ['_', '-']:
                    lang = filename[-2:].strip()
                    if lang in langs:
                        return lang
                elif len(filename)==2:
                    lang = filename
                    if lang in langs:
                        return lang


        site = getSite()
        portal_languages = getToolByName(site, 'portal_languages')
        langs = portal_languages.getSupportedLanguages()

        langbyfileid = findAbbrev(filename)
        if langbyfileid in langs:
            return langbyfileid

        return ''        