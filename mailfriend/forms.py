from django import forms

from mailfriend.models import MailedItem

class MailedItemForm(forms.ModelForm):
    class Meta:
        model = MailedItem
        exclude = ('mailed_by','date_mailed')