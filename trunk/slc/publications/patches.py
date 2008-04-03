from Products.Archetypes.BaseObject import BaseObject
from zope import event
from adapter.events import ObjectInitializedEvent
import logging
logger = logging.getLogger('slc.publications')
#
# Patch BaseObject processForm
#
logger.debug("Patching BaseObject.processForm in order to raise ObjectInitializedEvent")
def wrap_processForm(original_method):
    def processForm(self, *args, **kwargs):
        """Processes the schema looking for data in the form.
        """
        # Is creation time
        is_new_object = self.checkCreationFlag()
        # Call original method
        original_method(self, *args, **kwargs)
        # Add new features to original method
        if is_new_object:
            event.notify(ObjectInitializedEvent(self))
    return processForm

BaseObject.processForm = wrap_processForm(BaseObject.processForm)
