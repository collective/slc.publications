from DateTime import DateTime

from ordereddict import OrderedDict

from zope.app.component.hooks import getSite

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PublicationsView(BrowserView):
    """ Filter/Search for Publications """

    template = ViewPageTemplateFile('templates/publications.pt')
    template.id = "publications-view"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.now = DateTime()
        self.portal = getSite()
        self.pc = self.portal.portal_catalog
        self.path = '/'.join(context.getPhysicalPath())
        self.publication_types = OrderedDict({
                "factsheets": _(u"Factsheets"),
                "reports": _(u"Reports"),
                "literature_reviews": _(u"Literature reviews"),
                "e-facts": _(u"E-facts"),
                "outlook": _(u"Outlook"),
                "forum": _(u"Forum"),
                "magazine": _(u"Magazine"),
                "annual_report": _(u"Annual report"),
                "work_programmes": _(u"Work programmes"),
                "evaluation_reports": _(
                    u"Evaluation reports of Agency activities "),
                "other": _(u"Other Publications")
                })
        self.keywords = self.get_keywords()

    def __call__(self):
        return self.template()

    def get_publications(self):
        form = self.request.form
        type_path = self.path+"/"+form.get('typelist', '')
        query = {
            'object_provides':
                'slc.publications.interfaces.IPublicationEnhanced',
            'review_state'   : 'published',
            'SearchableText' : form.get("SearchableText", ''),
            'path'       : type_path,
                 }
        brains = self.pc.searchResults(query)
        publications = []
        for brain in brains:
            obj = brain.getObject()
            path = brain.getPath()
            date = self.context.toLocalizedTime(brain.effective)

            publications.append(
                {"title"          : brain.Title,
                 "effective_date" : date,
                 "size"           : obj.getObjSize(),
                 "path"           : path,
                 "type"           : self.get_publication_type(path),
                 })
        return publications

    def get_publication_type(self, path):
        """The publication type is determined by the folder"""
        for pub_type in self.publication_types.keys():
            pub_type_path = self.path+"/"+pub_type
            if pub_type_path in path:
                return self.publication_types[pub_type]
        return _(u"Unknown")

    def get_keywords(self):
        brains = self.pc.searchResults(
            {'object_provides':
             'slc.publications.interfaces.IPublicationEnhanced',
             'review_state': "published",
             })
        keywords = set()
        for brain in brains:
            for keyword in brain.Subject:
                keywords.add(keyword)
        return keywords

class PublicationsJSONView(PublicationsView):
    """Return search results in JSON"""

    def __call__(self):
        """JSON"""
        pubs = self.get_publications()
        return str(pubs).replace("'", '"').replace('u"', '"')
