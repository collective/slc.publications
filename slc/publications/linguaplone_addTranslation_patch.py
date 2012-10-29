# -*- coding: utf-8 -*-
from Products.LinguaPlone.I18NBaseObject import I18NBaseObject
from Products.LinguaPlone.config import RELATIONSHIP
from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
from zope.event import notify
from zope.interface import implements
from zope.interface import Attribute
from zope.component.interfaces import IObjectEvent


class IObjectTranslationReferenceSetEvent(IObjectEvent):
    """Sent after an object was translated."""

    object = Attribute("The object that was translated.")
    language = Attribute("Target language.")


class ObjectTranslationReferenceSetEvent(object):
    """Sent before an object is translated."""
    implements(IObjectTranslationReferenceSetEvent)

    def __init__(self, context, language):
        self.object = context
        self.language = language


def addTranslationReference(self, translation):
    """Adds the reference used to keep track of translations."""
    language = translation.Language()
    if self.hasTranslation(language):
        double = self.getTranslation(language)
        raise AlreadyTranslated(double.absolute_url())
    self.addReference(translation, RELATIONSHIP)
    referencesetevent = ObjectTranslationReferenceSetEvent(
        self, self.Language())
    notify(referencesetevent)

I18NBaseObject.addTranslationReference = addTranslationReference
