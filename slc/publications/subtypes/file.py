from zope.interface import implements
from Products.CMFPlone import PloneMessageFactory as _
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import FileWidget
from Products.validation import V_REQUIRED
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from plone.app.blob.field import BlobField


class ExtensionBlobField(ExtensionField, BlobField):
    """ derivative of blobfield for extending schemas """


class SchemaExtender(object):
    """ Extend the file to make it not language independant """
    implements(ISchemaExtender)

    def __init__(self, context):
        """ init """
        self.context = context

    def getFields(self):
        """ change the field to be languageIndependant = False"""
        return [
            ExtensionBlobField('file',
                required = True,
                primary = True,
                default = '',
                accessor = 'getFile',
                mutator = 'setFile',
                languageIndependent = False,
                storage = AnnotationStorage(migrate=True),
                validators = (('isNonEmptyFile', V_REQUIRED),
                              ('checkFileMaxSize', V_REQUIRED)),
                widget = FileWidget(label = _(u'label_file', default=u'File'),
                                    description=_(u''),
                                    show_content_type = False,))
        ]

