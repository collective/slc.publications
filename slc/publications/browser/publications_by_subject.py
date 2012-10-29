 # -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from types import ListType
from types import TupleType

import Acquisition
import os


class PublicationsBySubjectView(BrowserView):
    """View for displaying the publications by Subject overview page
    """
    template = ViewPageTemplateFile('templates/publications_by_subject.pt')

    def __call__(self):
        """ call - XXX: we should think about caching here..."""
        self.request.set('disable_border', True)

        context = Acquisition.aq_inner(self.context)
        subject = self.request.get('subject', [])

        portal_languages = getToolByName(context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()

        portal_catalog = getToolByName(context, 'portal_catalog')
        if hasattr(portal_catalog, 'getZCatalog'):
            portal_catalog = portal_catalog.getZCatalog()

        # PQ = Eq('portal_type', 'File') & \
        #      In('object_provides', 'slc.publications.interfaces.IPublicationEnhanced') & \
        #      In('Subject', subject) & \
        #      Eq('review_state', 'published') & \
        #      In('Language', [preflang, ''])
        # PUBS = portal_catalog.evalAdvancedQuery(PQ, (('getObjectPositionInParent','desc'),) )

        query = {
            'portal_type': 'File',
            'object_provides': 'slc.publications.interfaces.IPublicationEnhanced',
            'Subject': subject,
            'review_state': 'published',
            'Language': [preflang, ''],
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending',
        }
        PUBS = portal_catalog(query)

        publist = {}
        parentlist = []

        # we implement a simple sorting by folder id to have a grouping.
        # This is not too nice yet

        for P in PUBS:
            path = P.getPath()
            parentpath = os.path.dirname(path)
            parentlist.append(parentpath)
            section = publist.get(parentpath, [])
            section.append(P)
            publist[parentpath] = section

        # Q = In('portal_type', ['Folder', 'Large Plone Folder']) & \
        #     In('object_provides', 'slc.publications.interfaces.IPublicationContainerEnhanced')& \
        #     In('Language', [preflang, ''])
        # PARENTS = portal_catalog.evalAdvancedQuery(Q, (('getObjPositionInParent','asc'),) )

        query = {
            'portal_type': ['Folder', 'Large Plone Folder'],
            'object_provides': 'slc.publications.interfaces.IPublicationContainerEnhanced',
            'Language': [preflang, ''],
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending',
        }
        PARENTS = portal_catalog(query)

        self.publist = publist
        self.parents = [(x.getPath(), x) for x in PARENTS]

        return self.template()

    def subject(self):
        """ return the list of subjects """
        subject = self.request.get('subject', [])
        if type(subject) not in [ListType, TupleType]:
            subject = [subject]

        # XXX: implement keyword translation here
        return ", ".join([x for x in subject])

    def subject_label(self):
        """ return the list of pretty subjects """
        subject_label = self.request.get('subject_label', [])
        if type(subject_label) not in [ListType, TupleType]:
            subject_label = [subject_label]

        return ", ".join([x for x in subject_label])
