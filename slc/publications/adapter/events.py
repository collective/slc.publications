import logging

from Acquisition import aq_base, aq_inner, aq_parent
import ConfigParser, StringIO, tempfile, os, urllib, logging, re
from types import *

from zope import interface
from zope import component

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IObjectInitializedEvent

from p4a.subtyper.interfaces import ISubtyper

from slc.publications import interfaces
from slc.publications.utils import _get_storage_folder

try:
    from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
    HAVE_LINGUAPLONE=True
except ImportError:
    HAVE_LINGUAPLONE=False
    class AlreadyTranslated(Exception):
        """Raised when trying to create an existing translation."""
        pass


logger = logging.getLogger('slc.publications')

def object_added(evt):
    """ An object has been added to the pub folder. Make sure that that files are subtyped
    """
    obj = evt.object
    if not interfaces.IPublicationContainerEnhanced.providedBy(aq_parent(obj)):
        return

    subtyper = component.getUtility(ISubtyper)
    children = obj.aq_parent.objectValues(['ATFile', 'ATBlob'])
    for child in children:
        if subtyper.existing_type(child) is None:
            subtyper.change_type(child, 'slc.publications.Publication')


def remove_additionals(ob, evt):
    """ An object has been removed from the pub folder. Ensure that the 
        additional supporting folder is also removed
    """
    additionals_id = ob.getId().replace('.pdf', '')+'_data'
    container = aq_parent(aq_inner(ob)) 
    if additionals_id not in container.objectIds():
        return

    container.manage_delObjects([additionals_id])


def generate_image(obj, evt):
    """ EVENT
        called on objectmodified. Tries to generate the cover image. 
    """
    # Make sure we execute this only on the canonical
    #If the event is an ObjectInitializedEvent, we skip
    if IObjectInitializedEvent.providedBy(evt):
        return
        
    if hasattr(obj.aq_explicit, 'getCanonical') and obj != obj.getCanonical():
        return
        
    interfaces.IPublication(obj).generateImage()
    
# Event handler to catch our own patched event while translation named IObjectTranslationReferenceSetEvent
# We need this to be able to subtype an object while it is translated.
def subtype_on_translate(obj, evt):
    """ EVENT: 
        Update the chapter links based on the new set values in chapters
    """    
    canonical = aq_base(aq_inner(evt.object))
    target = aq_base(aq_inner(evt.target))
    subtyper = component.getUtility(ISubtyper)    
    subtype = subtyper.existing_type(canonical)
    if subtype is not None:
        subtyper.change_type(target, subtype.name)

class ChapterUpdater:
    """
    This adapter will take care of updating the Chapters
    of a publication
    """
    def __init__(self, publication, event):
        # skip this step if we're in the portal_factory
        if hasattr(publication, '_p_jar') and publication._p_jar is None:
            return

        self.publication = publication
        self.event = event
        # Make sure we only do this on canonical version
        if HAVE_LINGUAPLONE:
            if self.publication != self.publication.getCanonical():
                return
        
        if HAVE_LINGUAPLONE:
            translations = [publication] + [x[0] for x in publication.getTranslations().values()
                            if (x[0] is not None and x[0] != publication)]
        else:
            translations = [self.publication]

        for translation in translations:
            self._manage_chapters(translation)

    def _manage_chapters(self, translation):
        chapterfield = translation.getField('chapters')
        if chapterfield is None:
            logger.warn('Publication has no chapterfield: %s' % 
                        translation.absolute_url())
            return
        chapters = chapterfield.getAccessor(translation)()

        reference_container = _get_storage_folder(translation)
        references = self.getReferences(reference_container)

        outdated = []
        for reference in references:
            if reference not in chapters:
                outdated.append(reference)
        reference_container.manage_delObjects(ids = outdated)

        for chapter in chapters:
            chapter = chapter.encode('utf-8')
            if chapter not in references:
                self.addChapter(translation, chapter)

    def getReferences(self, reference_container):
        return reference_container.objectIds('ATLink')

    def addChapter(self, translation, chapter):
        if HAVE_LINGUAPLONE and not translation.isCanonical():
            can = translation.getCanonical()
            can_reference_container = _get_storage_folder(can)
            link = getattr(can_reference_container, chapter, None)
            if not link:
                # XXX what to do in this case (chapter not available in the
                # canonical folder)? Should not happen
                return
            try:
                new_chapter = link.addTranslation(translation.Language())
                new_chapter.setTitle(link.Title())
            except AlreadyTranslated:
                logger.error('We have an illegal translation in Publication %(pub)s '\
                'for chapter %(chapter)s in language %(lang)s. The illegal '\
                'translation can be found here: %(bad)s' % dict(pub=can.absolute_url(),
                chapter=link.absolute_url(), lang=translation.Language(), bad=
                link.getTranslation(translation.Language()).absolute_url()))
                return
        else:
            reference_container = _get_storage_folder(translation)
            reference_container.invokeFactory('Link', chapter)
            new_chapter = getattr(reference_container, chapter)
            new_chapter.setTitle(chapter)
            new_chapter.setLanguage(translation.Language())
        remote_url = "/%s#%s" % (urllib.unquote(translation.absolute_url(1)), 
                                 chapter)
        new_chapter.edit(remote_url)
        new_chapter.unmarkCreationFlag()
        self.setState(new_chapter, translation.Language())
        new_chapter.reindexObject()

    @property
    def portal_workflow(self):
        if not hasattr(self, '__portal_workflow'):
            self.__portal_workflow = getToolByName(self.publication, 
                                                   'portal_workflow')
        return self.__portal_workflow

    def setState(self, chapter, language):
        comment = "Publish publication in %s in language %s" % \
                  (chapter, language)
        self.portal_workflow.doActionFor(chapter, 'publish', comment=comment)

class TranslationChapterUpdater(ChapterUpdater):
    """
    This adapter will take care of updating the Chapters
    of a publication
    """
    def __init__(self, publication, event):
        # skip this step if we're in the portal_factory
        if hasattr(publication, '_p_jar') and publication._p_jar is None:
            return

        self.publication = event.target
        self._manage_chapters(self.publication)
