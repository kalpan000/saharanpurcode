from random import choices
from django import forms
from django.forms import fields, ModelForm


from .models import RaiseTicket

# class PagePermissionForGroupForm(ModelForm):
#     class Meta:
#         model = PagePermissionForGroup
#         fields = ('groupname', 'name_of_page', 'all_perm', 'read_perm', 'write_perm', 'delete_perm', 'update_perm', 'patch_perm',)


class RaiseTicketForm(ModelForm):
    class Meta:
        model = RaiseTicket
        fields = ('fname', 'lname', 'email','img','subject', 'msg',)