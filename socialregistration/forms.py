"""
Created on 22.09.2009

@author: alen
"""
from django import forms
from django.utils.translation import gettext as _

from django.contrib.auth.models import User

attrs_dict = {'class': 'required'}

class UserForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers and underscores.')})
    email = forms.EmailField(required=True)

    def __init__(self, user, profile, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user = user
        self.profile = profile

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        else:
            raise forms.ValidationError(_('This username is already in use.'))

    def save(self):
        self.user.username = self.cleaned_data.get('username')
        self.user.email = self.cleaned_data.get('email')
        self.user.save()
        self.profile.user = self.user
        self.profile.save()
        return self.user
