# Add i18n msgids here which do not exist in filesystem code so that
# the translation-extract script can find them

from slc.publications import SLCPublicationsMessageFactory as _

# browser/templates/publication.pt and estimate_template.pt use a
# method: getTranslatedString to handle the translation because of a
# bug. This may no longer be necessary, but I haven't verified it so
# I'm adding the labels here for extraction.\
_('label_download_full_publication',
  default='Download the full publication as PDF')
_('label_order_copy',
  default='Order a printed copy of this document!')
_('label_available_in', default='Available in')
_('heading_chapterlisting',
  default='Chapters in this Publication')
_('heading_related_resources', default='Related Resources')
_('box_show_more_publications',
  default='Show more publications on')
_('label_estimated_download_time',
  default='Estimated Download Time')
