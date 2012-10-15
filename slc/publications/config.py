
__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'

PROJECTNAME = "slc.publications"
product_globals = globals()

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"

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
