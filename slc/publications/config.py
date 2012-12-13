__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'

PROJECTNAME = "slc.publications"
product_globals = globals()

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"

from ordereddict import OrderedDict

from Products.CMFPlone import PloneMessageFactory as _
from slc.publications import HAVE_LINGUAPLONE

DEPENDENCIES = ['p4a.subtyper', ]

if HAVE_LINGUAPLONE:
    DEPENDENCIES.append('LinguaPlone')

combined_languages_EU = dict(
    da='da_DK',     # special!
    de='de_DE',
    et='et_EE',     # special!
    en='en_GB',     # special!
    es='es_ES',
    fr='fr_FR',
    it='it_IT',
    lv='lv_LV',
    lt='lt_LT',
    hu='hu_HU',
    mt='mt_MT',
    nl='nl_NL',
    pl='pl_PL',
    pt='pt_PT',
    ro='ro_RO',
    sk='sk_SK',
    sl='sl_SI',     # special!
    fi='fi_FI',
    sv='sv_SE',     # special!
    cs='cs_CZ',     # special!
    el='el_GR',     # special!
    bg='bg_BG',
    )

# The order of items in an OrderedDict cannot be set on
# creation, but the order items are added is maintained
pub_types = OrderedDict()

pub_types["reports"] = {
    "title": _(u"Reports"),
    "description": _(u"help_reports")}

pub_types["literature_reviews"] = {
    "title": _(u"Literature reviews"),
    "description": _(u"help_literature_reviews")}

pub_types["e-facts"] = {
    "title": _(u"E-facts"),
    "description": _(u"help_e-facts")}

pub_types["articles"] = {
    "title": _(u"Articles"),
    "description": _(u"help_articles")}

pub_types["promotional_material"] = {
    "title": _(u"Promotional Material"),
    "description": _(u"help_promotional_material")}

pub_types["factsheets"] = {
    "title": _(u"Factsheets"),
    "description": _(u"help_factsheets")}

pub_types["presentations"] = {
    "title": _(u"Presentations (PPT)"),
    "description": _(u"help_presentations")}

pub_types["magazine"] = {
    "title": _(u"Magazine"),
    "description": _(u"help_magazine")}

pub_types["other_publications"] = {
    "title": _(u"Other Publications"),
    "description": _(u"help_other_publications")}

pub_types["corporate_publications"] = {
    "title": _(u"Corporate publications"),
    "description": _(u"help_corporate_publications")}

pub_types["evaluation_reports"] = {
    "title": _(u"Evaluation reports"),
    "description": _(u"help_evaluation_reports")}

PUB_TYPES = pub_types.copy()
