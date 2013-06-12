__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'

PROJECTNAME = "slc.publications"
product_globals = globals()

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"

from ordereddict import OrderedDict
from slc.publications import HAVE_LINGUAPLONE
from slc.publications import SLCPublicationsMessageFactory as _

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

pub_types["corporate"] = {
    "title": _(u"Corporate publications"),
    "description": _(
        u"help_corporate_publications",
        default=u"The Agency's strategy, annual management plan and annual "
            "report (full and summary versions) provide a comprehensive "
            "overview of EU-OSHA's activities and governance.")}

pub_types["reports"] = {
    "title": _(u"Reports"),
    "description": _(
        u"help_reports",
        default="Present the outcome of research, which will help to inform "
            "discussion among EU and national authorities, trade unions and "
            "experts on how to take forward issues in health and safety.")}

pub_types["literature_reviews"] = {
    "title": _(u"Literature reviews"),
    "description": _(
        u"help_literature_reviews",
        default="Provide an overview of the most important issues related "
        "to this topic.")}

pub_types["e-facts"] = {
    "title": _(u"E-facts"),
    "description": _(
        u"help_e-facts",
        default="Online only articles aimed at workers, employers and "
            "occupational safety and health professionals.")}

pub_types["articles"] = {
    "title": _(u"Articles"),
    "description": _(
        u"help_articles",
        default="Articles from leading safety and health experts on issues "
            "of topical concern.")}

pub_types["promotional_material"] = {
    "title": _(u"Promotional Material"),
    "description": _(
        u"help_promotional_material",
        default="A selection of promotional literature presenting Agency "
            "projects and services and mainly used at exhibitions and "
            "events.")}

pub_types["factsheets"] = {
    "title": _(u"Factsheets"),
    "description": _(
        u"help_factsheets",
        default="Provide brief introductions to the Agency and to our "
            "activities.")}

#7694 temporarily remove PPTs from the publication types
# pub_types["presentations"] = {
#     "title": _(u"Presentations (PPT)"),
#     "description": _(
#         u"help_presentations",
#         default="PPT presentations on various safety and health topics and "
#             "EU-OSHA projects which can be freely adapted and reused. All "
#             "English versions are also available on Slideshare "
#             "(<a href='http://www.slideshare.net/euosha'>"
#             "http://www.slideshare.net/euosha</a>)")}

pub_types["magazine"] = {
    "title": _(u"Magazine"),
    "description": _(
        u"help_magazine",
        default="In-depth information and analysis from leading experts and "
            "practitioners in occupational safety and health.")}

pub_types["evaluation_reports"] = {
    "title": _(u"Evaluation reports"),
    "description": _(
        u"help_evaluation_reports",
        default="An independent assessment of our work and contribute to "
            "improving our performance.")}

PUB_TYPES = pub_types.copy()
