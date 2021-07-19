from django import forms
from requests import HTTPError

from demo.services import auth_login


class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=100)
    password = forms.CharField(label='Password', max_length=100)
    access_token = None
    refresh_token = None

    def is_valid(self):
        is_valid = super().is_valid()
        if not is_valid:
            return False
        try:
            data = auth_login(self.cleaned_data['login'], self.cleaned_data['password'])
        except HTTPError as e:
            self.errors.update({'auth': str(e)})
            return False

        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']

        return True
