from django import forms

from mailfriend.models import MailedItem
from mailfriend.utils import generic_object_get

class MailedItemForm(forms.ModelForm):
    class Meta:
        model = MailedItem
        exclude = ('mailed_by','date_mailed')
    
    def __init__(self, *args, **kwargs):
        super(MailedItemForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].widget = forms.HiddenInput()
        self.fields['object_id'].widget = forms.HiddenInput()
    
    def check_generic_object(self):
        """
        Check that the generic object exists.
        
        If it doesn't, we bail early
        """
        ct_pk = int(self.data['content_type'])
        obj_pk = int(self.data['object_id'])
        return generic_object_get(ct_pk, obj_pk)
        