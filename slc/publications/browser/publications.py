from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ordereddict import OrderedDict
from slc.publications.config import PUB_TYPES
from zope.app.component.hooks import getSite
from zope.i18n import translate

import json
import locale
import logging

logger = logging.getLogger('slc.publications.publications.publications.py')

# Constants
CAROUSEL_ITEMS = 4
MAX_RESULTS = 10
IGNORE_KEYWORDS = (u'publications',)


class PublicationsView(BrowserView):
    """ Filter/Search for Publications """

    template = ViewPageTemplateFile('templates/publications.pt')
    has_more_results = False

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.now = DateTime()
        self.portal = getSite()
        self.pc = self.portal.portal_catalog
        self.path = '/'.join(context.getPhysicalPath())
        self.publication_types = PUB_TYPES

    def __call__(self):
        return self.template()

    def get_publications(self):
        form = self.request.form
        typelist = form.get("typelist", "")
        search_path = self.path
        if typelist:
            search_path += "/" + typelist
        keywords = form.get("keywords")
        query = {
            'object_provides':
                'slc.publications.interfaces.IPublicationEnhanced',
            'review_state': 'published',
            'SearchableText': form.get("SearchableText", ''),
            'path': search_path,
            'sort_on': 'effective',
            'sort_order': 'descending'
            }
        if keywords:
            query['Subject'] = keywords

        brains = self.pc.searchResults(query)

        show_all = form.get("show-all", False)
        results = show_all and brains or brains[:MAX_RESULTS]
        if len(brains) > MAX_RESULTS and show_all == False:
            self.has_more_results = True

        publications = []

        for result in results:
            path = result.getPath()
            title = result.Title.replace("'", "&#39;")

            # Searches without SearchableText are sent to the normal
            # portal_catalog and the Title returned is a string
            if not isinstance(title, unicode):
                title.decode("utf-8")

            pub_type = self.get_publication_type(path)
            type_info = self.publication_types.get(pub_type)
            type_title = type_info and type_info['title'] or u''

            portal_languages = getToolByName(
                self.context, 'portal_languages')
            preflang = portal_languages.getPreferredLanguage()

            # Need to translate the type_name here for the JSON version
            translated_type_title = translate(
                type_title,
                domain="slc.publications",
                target_language=preflang,
                )
            publications.append({
                "title": title,
                "year": result.effective.year(),
                "size": result.getObjSize,
                "path": path + "/view",
                "type": pub_type,
                "type_title": translated_type_title,
            })
        return publications

    def get_carousel_details(self):
        query = {
            'object_provides':
                'slc.publications.interfaces.IPublicationEnhanced',
            'review_state': 'published',
            'path': self.path,
            'sort_on': 'Date',
            'sort_order': 'descending'
        }
        pubs = [i.getObject() for i in
                self.pc.searchResults(query)[:CAROUSEL_ITEMS]]
        pub_details = []
        for pub in pubs:
            pub_details.append({
                "absolute_url": pub.absolute_url(),
                "title": pub.Title(),
                "description": pub.Description(),
                "date": pub.Date()
            })
        return pub_details

    def get_publication_type(self, path):
        """The publication type is determined by the folder"""
        for pub_type in self.publication_types.keys():
            if pub_type in path:
                return pub_type
        return "unknown"

    def get_keywords(self):
        """Return keyword ids, sorted alphabetically by keyword titles
        (multi-lingual aware).

        :returns: List of keyword ids
        """
        brains = self.pc.searchResults({
            'object_provides':
            'slc.publications.interfaces.IPublicationEnhanced',
            'review_state': "published",
            'path': self.path,
        })
        keywords = set()
        for brain in brains:
            for keyword in brain.Subject:
                if keyword not in IGNORE_KEYWORDS:
                    keywords.add(keyword)

        # this reads the environment and inits the right locale
        locale.setlocale(locale.LC_ALL, "")

        # sort the keywords by translated keyword title, properly handling
        # unicode characters
        # XXX: This could probably be written a little cleaner and more
        # efficient
        translation_tool = getToolByName(self.context, 'translation_service')
        language_tool = getToolByName(self.context, 'portal_languages')
        lang = language_tool.getPreferredLanguage()
        results = {}
        for keyword in keywords:
            title = translation_tool.translate(
                keyword, 'osha', target_language=lang)
            results[title] = keyword
        sorted_titles = sorted(results.iterkeys(), cmp=locale.strcoll)

        ordered_keywords = OrderedDict()
        for title in sorted_titles:
            keyword_id = results[title]
            ordered_keywords[keyword_id] = title

        return ordered_keywords


class PublicationsJSONView(PublicationsView):
    """Return search results in JSON"""

    def __call__(self):
        return json.dumps(self.get_publications())
