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
                })

    def __call__(self):
        return self.template()

    def get_publications(self):
        brains = self.pc.searchResults(
            {'object_provides':
             'slc.publications.interfaces.IPublicationEnhanced',
             'review_state': "published",
             })
        publications = []
        for brain in brains:
            obj = brain.getObject()
            path = brain.getPath()

            publications.append(
                {"title"          : brain.Title,
                 "effective_date" : brain.effective,
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
