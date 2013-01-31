from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from slc.publications import HAVE_LINGUAPLONE, generateMethods
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

OSHAMessageFactory = MessageFactory('osha')

LANGUAGE_INDEPENDENT_INITIALIZED = '_languageIndependent_initialized_slc_publications'


class ExtensionFieldMixin:
    """ """
    def getMutator(self, instance):
        def mutator(value, **kw):
            self.set(instance, value, **kw)

        methodName = getattr(self, 'mutator', None)
        if methodName is None:  # Use default setter
            return mutator

        method = getattr(instance, methodName, None)
        if method is None:   # Use default setter
            return mutator
        return method


class ExtendedImageField(ExtensionFieldMixin, ExtensionField,
                         atapi.ImageField):
    """ """


class ExtendedBooleanField(ExtensionFieldMixin, ExtensionField,
                           atapi.BooleanField):
    """ """


class ExtendedLinesField(ExtensionFieldMixin, ExtensionField,
                         atapi.LinesField):
    """ """


class ExtendedFileField(ExtensionFieldMixin, ExtensionField, atapi.FileField):
    """ """


class ExtendedStringField(ExtensionFieldMixin, ExtensionField,
                          atapi.StringField):
    """ """


class ExtendedReferenceField(ExtensionFieldMixin, ExtensionField,
                             atapi.ReferenceField):
    """ """
    def get(self, instance, **kwargs):
        if HAVE_LINGUAPLONE:
            canonical = instance.getCanonical()
            canonical_refs = atapi.ReferenceField.get(
                self, canonical, **kwargs)
            portal_languages = getToolByName(instance, 'portal_languages')
            preflang = portal_languages.getPreferredLanguage()
            return [o.getTranslation(preflang) or o.getCanonical()
                    for o in canonical_refs]
        else:
            return atapi.ReferenceField.get(self, instance, **kwargs)


class SchemaExtender(object):
    """ Extend a file to get more publication related fields """
    implements(IOrderableSchemaExtender)

    _fields = [
            # Override relatedItems make it langauge independent and override
            # the accessor to return langage dependent references.
            ExtendedReferenceField('relatedItems',
                relationship='relatesTo',
                multiValued=True,
                isMetadata=True,
                languageIndependent=True,
                accessor='getRelatedItems',
                mutator='setRelatedItems',
                index='KeywordIndex',
                write_permission=permissions.ModifyPortalContent,
                widget=ReferenceBrowserWidget(
                    allow_search=True,
                    allow_browse=True,
                    show_indexes=False,
                    force_close_on_insert=True,
                    label=OSHAMessageFactory(u"Related Items"),
                    description='',
                    visible={'edit': 'visible', 'view': 'invisible' }
                ),
            ),
            ExtendedImageField('cover_image',
                schemata='publication',
                sizes={'cover': (70, 100)},
                languageIndependent=True,
                accessor='getCover_image',
                mutator='setCover_image',
                widget=atapi.ImageWidget(
                    label=_(
                        u'label_cover_image',
                        default=u'Cover Image'
                    ),
                    description=_(
                        u'description_cover_image',
                        default=u'Upload a cover image. Leave empty to have the system autogenerate one for you.'
                    ),
                ),
            ),
            ExtendedStringField('author',
                schemata='publication',
                languageIndependent=True,
                accessor='getAuthor',
                mutator='setAuthor',
                widget=atapi.StringWidget(
                    label=_(
                        u'label_author',
                        default=u'Author'
                    ),
                    description=_(
                        u'description_author',
                        default=u'Fill in the Name of the Author of this Publication.'
                    ),
                ),
            ),
            ExtendedStringField('isbn',
                schemata='publication',
                languageIndependent=False,
                widget=atapi.StringWidget(
                    label=_(u'label_isbn', default=u'ISBN'),
                    description=_(
                        u'description_isbn',
                        default=u'Fill in the ISBN Number of this Publication.'
                    ),
                ),
            ),
            ExtendedStringField('order_id',
                schemata='publication',
                languageIndependent=False,
                widget=atapi.StringWidget(
                    label=_(u'label_order_id', default=u'Order ID'),
                    description=_(
                        u'description_order_id',
                        default=u'Fill in the Order ID of this Publication.'
                    ),
                ),
            ),
            ExtendedBooleanField('for_sale',
                schemata='publication',
                languageIndependent=True,
                accessor='getFor_sale',
                mutator='setFor_sale',
                widget=atapi.BooleanWidget(
                    label=_(
                        u'label_for_sale',
                        default=u'For sale?'
                    ),
                    description=_(
                        u'description_for_sale',
                        default=u'Is this Publication for sale?'
                    ),
                ),
            ),
            ExtendedLinesField('chapters',
                schemata='publication',
                languageIndependent=True,
                accessor='getChapters',
                mutator='setChapters',
                widget=atapi.LinesWidget(
                    label=_(
                        u'label_chapters',
                        default=u'Chapters'
                    ),
                    description=_(
                        u'description_chapters',
                        default=u'Chapters of this Publication. Specify the Link targets defined in your pdf file, one per line.'
                    ),
                ),
            ),
            ExtendedFileField('metadata_upload',
                schemata='publication',
                languageIndependent=True,
                accessor='getMetadata_upload',
                mutator='setMetadata_upload',
                widget=atapi.FileWidget(
                    label=_(
                        u'label_metadata_upload',
                        default=u'Metadata INI upload'
                    ),
                    description=_(
                        u'description_metadata_upload',
                        default=u'Upload Metadata in INI style format.'
                    ),
                ),
            ),
            ExtendedStringField('owner_password',
                schemata='publication',
                languageIndependent=False,
                widget=atapi.StringWidget(
                    label=_(
                        u'label_owner_password',
                        default=u'Owner Password'
                    ),
                    description=_(
                        u'description_owner_password',
                        default=u'If this publication is protected, speciy the pdf owner password if you want to parse the file.'
                    ),
                ),
            ),
            ExtendedStringField('user_password',
                schemata='publication',
                languageIndependent=False,
                widget=atapi.StringWidget(
                    label=_(
                        u'label_user_password',
                        default=u'User Password'
                    ),
                    description=_(
                        u'description_user_password',
                        default=u'If this publication is protected, speciy the pdf user password if you want to parse the file.'
                    ),
                ),
            ),
            ]

    def __init__(self, context):
        """ init """
        self.context = context
        klass = context.__class__
        if HAVE_LINGUAPLONE and not getattr(
                klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
            fields = [field for field in self._fields
                      if field.languageIndependent]
            generateMethods(klass, fields)
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)

    def getFields(self):
        """ get fields """
        return self._fields

    def getOrder(self, original):
        """ new order """
        publication = original.get('publication', [])

        publication.insert(0, 'author')
        publication.insert(1, 'isbn')
        publication.insert(2, 'order_id')
        publication.insert(3, 'for_sale')
        publication.insert(4, 'chapters')
        publication.insert(5, 'cover_image')
        publication.insert(6, 'metadata_upload')
        publication.insert(7, 'owner_password')
        publication.insert(8, 'user_password')

        original['publication'] = publication

        return original
