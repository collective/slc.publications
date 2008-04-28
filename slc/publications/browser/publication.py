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
from zope.app.i18n import ZopeMessageFactory as _

from Products.AdvancedQuery import In, Eq, Le, Ge, And, Or
from Products.CMFCore import utils as cmfutils
from Products.CMFDefault.formlib.form import getLocale

from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages import interfaces as statusmessages_ifaces

from Products.Five.browser import pagetemplatefile
from Products.Five.formlib import formbase

from slc.publications import interfaces 
from slc.publications.ini.interfaces import IINIParser
from slc.publications.utils import _get_storage_folder


from p4a.common import at
from p4a.common import formatting

from zope.app.form.browser import TextAreaWidget, DateDisplayWidget, CollectionInputWidget, OrderedMultiSelectWidget



class PublicationPageView(object):
    """Page for displaying a publication.
    """
    adapted_interface = interfaces.IPublication
    media_field = 'file'

    #form_fields = form.FormFields(interfaces.IPublication)
    #datewidget = DateDisplayWidget
    #datewidget.displayStyle = "medium"
    #form_fields['publication_date'].custom_widget = datewidget
    
    label = u'View Publication Info'

    @property
    def template(self):
        return self.index

    def available_translations(self):
        portal_languages = cmfutils.getToolByName(self.context, 'portal_languages')
        default_language = portal_languages.getDefaultLanguage()
        
        translations = self.context.getTranslations()
        if len(translations)<1:
            return
        
        lang_codes = translations.keys()
        lang_codes.sort()
        
        R = []
        for lang in lang_codes:
            trans = translations[lang][0]
            url = trans.absolute_url()
            name = portal_languages.getNameForLanguageCode(lang or default_language)
            R.append( (name, url) )
        return R
                
    def chapters(self):
        additionals = _get_storage_folder(self.context)
        if additionals is None:
            return []
        chapterlinks = additionals.objectValues('ATLink')
        return chapterlinks
        
        
    def fetchRelatedPublications(self, limit=3):
        context = Acquisition.aq_inner(self.context)
        subject = context.Subject()
        
        pc = cmfutils.getToolByName(context, 'portal_catalog')
        portal_languages = cmfutils.getToolByName(context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()
        
        if hasattr(pc, 'getZCatalog'):
            pc = pc.getZCatalog()
        
        PQ = Eq('portal_type', 'File') & \
             In('object_provides', 'slc.publications.interfaces.IPublicationEnhanced') & \
             In('Subject', subject) & \
             Eq('review_state', 'published') & \
             Eq('Language', preflang)

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


class IPublicationView(interface.Interface):
    """ """
    
class PublicationView(object):
    """
    """

    def __init__(self, context, request):
        self.publication_info = interfaces.IPublication(context)




def applyChanges(context, form_fields, data, adapters=None):
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

    template = pagetemplatefile.ViewPageTemplateFile('publication-edit.pt')
    form_fields = form.FormFields(interfaces.IPublication)
    #form_fields['chapters'].custom_widget = CollectionInputWidget

    label = u'Edit Publication Data'
    priority_fields = ['title']

    def update(self):
        self.adapters = {}
        form_fields = self.form_fields
        # here we can fiddle...
        self.form_fields = form_fields
        super(PublicationEditForm, self).update()

    def setUpWidgets(self, ignore_request=False):
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
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
        self.context = context
        self.request = request
        
    def folderContents(self):
        query = {'portal_type': 'File', 'sort_on': 'effective', 'sort_order': 'reverse'}        
        
        if self.context.portal_type=='Topic':
            meth = self.context.queryCatalog
        else:
            meth = self.context.getFolderContents
        
        results = meth(contentFilter=query)
        return results
        
        
    def has_syndication(self):
        try:
            view = self.context.restrictedTraverse('@@rss.xml')
            return True
        except:
            # it's ok if this doesn't exist, just means no syndication
            return False
            


class IGenerateMetadata(interface.Interface):
    def __call__():
        """ download the generated metadata """
            
class GenerateMetadataView(object):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request    
        
    def __call__(self):
        """ download the generated metadata """
        iniparser = component.getUtility(IINIParser)

        return iniparser.retrieve(self.context)
