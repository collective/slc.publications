import logging
import zope.interface
from slc.publications import interfaces 


log = logging.getLogger('slc.publications.events.py')

def process_uploaded_publications(file, event):
    """
    """
    container = event.object.aq_parent 
    file_obj = file.getFile()
    file_name, file_ext = file_obj.filename.split('.')
    l = file_name.split('_')
    if len(l[0]) == 2:
        lang = l[0]
    elif len(l[-1]) == 2:
        lang = l[-1]
    else:
        log.warn("File language could not be identified. Filename need to be" + 
                 "prepended or appended with the language identifier, i.e" + 
                 "en_factsheet.pdf' or 'factsheet_en.pdf'")
        return

    tcont =  container.getTranslation(lang) 
    if not tcont:
        tcont = container.addTranslation(lang)
        zope.interface.alsoProvides(tcont, 
                                    (interfaces.IPublicationContainerEnhanced,)
                                    )
        
    # Cannot cut here, gives permission error
    copy_data = container.manage_cutObjects(ids=[file.getId()])
    tcont.manage_pasteObjects(cb_copy_data=copy_data)
    file = getattr(tcont, file_obj.filename)
    zope.interface.alsoProvides(file, 
                                (interfaces.IPublicationEnhanced,)
                                )


        
