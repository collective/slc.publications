from zope import interface
from zope.formlib import form
from slc.publications import interfaces
try:
    from zope.app.annotation import interfaces as annointerfaces
except ImportError, err:
    # Zope 2.10 support
    from zope.annotation import interfaces as annointerfaces

_marker = object()

class ToggleEnhancementsView(object):
    """ Toggle the view for Enhancements
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        was_activated = self.media_activated
        self.media_activated = not was_activated
        response = self.request.response

        if was_activated:
            activated = 'Media+deactivated'
        else:
            activated = 'Media+activated'

        response.redirect(self.context.absolute_url() + \
                          '/view?portal_status_message='+activated)

    def _set_media_activated(self, v):
        interfaces.IMediaActivator(self.context).media_activated = v
    def _get_media_activated(self):
        return interfaces.IMediaActivator(self.context).media_activated
    media_activated = property(_get_media_activated, _set_media_activated)

