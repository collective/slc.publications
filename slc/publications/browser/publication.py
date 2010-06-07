import Acquisition
import AccessControl
import datetime
import urllib

from zope import event
from zope import component
from zope import interface
from zope import schema
from zope.formlib import form
from zope.app.event import objectevent

from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from Products.AdvancedQuery import In, Eq, Le, Ge, And, Or

from Products.CMFCore import utils as cmfutils
from Products.CMFDefault.formlib.form import getLocale
from zope.i18n import translate

from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages import interfaces as statusmessages_ifaces

from Products.Five.browser import pagetemplatefile
from Products.Five.formlib import formbase

from slc.publications import HAVE_LINGUAPLONE
from slc.publications import interfaces
from slc.publications.ini.interfaces import IINIParser
from slc.publications.utils import _get_storage_folder


from p4a.common import at
from p4a.common import formatting

from zope.app.form.browser import TextAreaWidget, DateDisplayWidget, CollectionInputWidget, OrderedMultiSelectWidget

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('slc.publications')

class PublicationPageView(object):
    """Page for displaying a publication.
    """
    adapted_interface = interfaces.IPublication
    media_field = 'file'

    estimate_template = pagetemplatefile.ViewPageTemplateFile('templates/estimate_template.pt')

    label = u'View Publication Info'

    @property
    def template(self):
        """ return the template """
        return self.index

    def available_translations(self, context=None):
        """ list all available translations for this publication """
        context = context or Acquisition.aq_inner(self.context)
        portal_languages = cmfutils.getToolByName(context, 'portal_languages')
        default_language = portal_languages.getDefaultLanguage()
        ali = portal_languages.getAvailableLanguageInformation()

        if HAVE_LINGUAPLONE:
            translations = context.getTranslations()
        else:
            translations = {context.Language(): (context, context.Language())}

        if len(translations.keys())<1:
            return

        lang_codes = translations.keys()
        lang_codes.sort()

        sm = getSecurityManager()
        R = []
        for lang in lang_codes:
            trans = translations[lang][0]
            if not sm.checkPermission('View', trans):
                continue
            url = trans.absolute_url()

            name = ali.get(lang, {'native': lang})['native']
            R.append( (name, url) )
        return R

    def chapters(self):
        """ get the chapters """
        additionals = _get_storage_folder(self.context)
        if additionals is None:
            return []
        chapterlinks = additionals.objectValues('ATLink')
        return chapterlinks

    def fetchRelatedPublications(self, limit=3):
        """ Query the catalog for related publications """
        context = Acquisition.aq_inner(self.context)
        subject = context.Subject()

        pc = cmfutils.getToolByName(context, 'portal_catalog')
        if hasattr(pc, 'getZCatalog'):
            pc = pc.getZCatalog()

        portal_languages = cmfutils.getToolByName(context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()

        PQ = Eq('portal_type', 'File') & \
             In('object_provides', 'slc.publications.interfaces.IPublicationEnhanced') & \
             In('Subject', subject) & \
             Eq('review_state', 'published') 

        if HAVE_LINGUAPLONE:
           PQ = PQ & In('Language', [preflang, ''])

        RES = pc.evalAdvancedQuery(PQ, (('effective','desc'),) )

        PUBS = []
        mypath = "/".join(context.getPhysicalPath())

        for R in RES:
            # dont show myself
            if R.getPath() == mypath:
                continue
            PUBS.append(R)

        if limit >0 and len(PUBS)>limit:
            PUBS = PUBS[:limit]

        return PUBS

    def update(self):
        pass


    def estimated_download_time(self):
        return self.estimate_template()

    def _format_timestring(self, secs):
        const = {'sec':1,
                 'mins':60*60,
                 'hours':24*60*60}
        order = ('hours', 'mins', 'sec')
        smaller = order[-1]

        if type(secs) in [type(0), type(0L)]:
            if secs < const[smaller]:
                return '1 %s' % smaller
            for c in order:
                if secs/const[c] > 0:
                    break
            return '%.1f %s' % (float(secs/float(const[c])), c)

        return "%s secs" % secs

    def get_initial_downloadtime(self):
        return self._format_timestring( int(self.context.get_size()/57344.0))

    def generate_estimation_js(self):
        lines = []
        objsize = float(self.context.get_size())
        du56 = self._format_timestring(int(objsize/57344.0))
        dsl256 = self._format_timestring(int(objsize/262144.0))
        dsl768 = self._format_timestring(int(objsize/786432.0))
        t1 = self._format_timestring(int(objsize/1536000.0))



        lines.append("var du56 = '%s';" % du56)
        lines.append("var dsl256 = '%s';" % dsl256)
        lines.append("var dsl768 = '%s';" % dsl768)
        lines.append("var t1 = '%s';" % t1)
        return "\n".join(lines)

    def getFormattedKeywords(self):
        """ returns keywords (Subject) set on the Publication formatted in a friendly way"""
        keywords = self.context.Subject()
        pf = interfaces.IPrettyFormatter(self.context)
        keywords = [dict(id=key, label=pf.formatKeyword(key)) for key in keywords]

        return keywords

    def getTranslatedString(self, value, preflang, default=u''):
        msg = _(value, default)
        return translate(msg, target_language=preflang)


    def get_additional_info(self):
        """ Method for injecting custom content into the view of a Publication
            Just define an adapter for IPublicationEnhanced that implements IAdditionalPublicationInfo.
        """
        adapter = component.queryAdapter(self.context, interfaces.IAdditionalPublicationInfo)
        if adapter:
            try:
                return adapter()
            except:
                pass
        return u""


class IPublicationView(interface.Interface):
    """Interface  for the Publication View """

class PublicationView(object):
    """ Publication View
    """

    def __init__(self, context, request):
        self.publication_info = interfaces.IPublication(context)



def applyChanges(context, form_fields, data, adapters=None):
    """ apply changes """
    if adapters is None:
        adapters = {}

    changed = []

    for form_field in form_fields:
        field = form_field.field
        # Adapt context, if necessary
        interface = field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if (newvalue is not form_field) and (field.get(adapter) != newvalue):
            changed.append(name)
            field.set(adapter, newvalue)

    return changed


class PublicationEditForm(formbase.EditForm):
    """Form for editing publication fields.
    """

    template = pagetemplatefile.ViewPageTemplateFile('templates/publication-edit.pt')
    form_fields = form.FormFields(interfaces.IPublication)
    #form_fields['chapters'].custom_widget = CollectionInputWidget

    label = u'Edit Publication Data'
    priority_fields = ['title']

    def update(self):
        """ update the form """
        self.adapters = {}
        form_fields = self.form_fields
        # here we can fiddle...
        self.form_fields = form_fields
        super(PublicationEditForm, self).update()

    def setUpWidgets(self, ignore_request=False):
        """ setup edit widgets """
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        """ handle edit """
        changed = applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            attrs = objectevent.Attributes(interfaces.IPublication, *changed)
            event.notify(
                objectevent.ObjectModifiedEvent(self.context, attrs)
                )
            # TODO: Needs locale support. See also Five.form.EditView.
            self.status = _("Successfully updated")
        else:
            self.status = _('No changes')
        statusmessages_ifaces.IStatusMessage(
            self.request).addStatusMessage(self.status, 'info')
        redirect = self.request.response.redirect
        return redirect(self.context.absolute_url()+'/view')

class PublicationEditMacros(formbase.PageForm):
    # short cut to get to macros more easily
    def __getitem__(self, name):
        """ get item """
        if hasattr(self.template, 'macros'):
            template = self.template
        elif hasattr(self.template, 'default_template'):
            template = self.template.default_template
        else:
            raise TypeError('Could not lookup macros on the configured '
                            'template')

        if getattr(template.macros, '__get__', None):
            macros = template.macros.__get__(template)
        else:
            macros = template.macros

        if name == 'macros':
            return macros
        return macros[name]

class PublicationContainerView(object):
    """View for publication containers.
    """

    def __init__(self, context, request):
        """ init the container view """
        self.context = context
        self.request = request

    def folderContents(self):
        """ customized folder contents """
        query = {}
        portal_languages = cmfutils.getToolByName(self.context, 'portal_languages')
        portal_catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        preflang = portal_languages.getPreferredLanguage()

        currpath = "/".join(self.context.getPhysicalPath())
        if HAVE_LINGUAPLONE:
            canonical = self.context.getCanonical()
        else:
            canonical = self.context
            
        canonicalpath = "/".join(canonical.getPhysicalPath())

        if self.context.portal_type=='Topic':
            query = {'portal_type': 'File', 'sort_on': 'effective', 'sort_order': 'reverse'}
            results = self.context.queryCatalog(contentFilter=query)
        else:
            query = dict(object_provides='slc.publications.interfaces.IPublicationEnhanced',
                         sort_on='effective',
                         sort_order='reverse',
                         Language=['', preflang],
                         path=[currpath, canonicalpath]
                         )
            results = portal_catalog(query)

        return results


    def has_syndication(self):
        """ support syndication? """
        try:
            view = self.context.restrictedTraverse('@@rss.xml')
            return True
        except:
            # it's ok if this doesn't exist, just means no syndication
            return False



class IGenerateMetadata(interface.Interface):
    """ Interface for Metadata Generation """
    def __call__():
        """ download the generated metadata """

class GenerateMetadataView(object):
    """ Metadata Generation """

    def __init__(self, context, request):
        """ init """
        self.context = context
        self.request = request

    def __call__(self):
        """ download the generated metadata """
        iniparser = component.getUtility(IINIParser)

        return iniparser.retrieve(self.context)


class ICoverImage(interface.Interface):
    """ Can have a cover image """
    def __call__():
        """ generate the cover image """

class CoverImageView(object):
    """ Cover image generation """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ generate the cover image """
        field = self.context.getField('cover_image')
        if field is None:
            return None
        image = field.getAccessor(self.context)()
        if not image:
            adapter = interfaces.IPublication(self.context)
            adapter.generateImage()
            image = field.getAccessor(self.context)()
        return image
