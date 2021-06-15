from django.contrib.auth.models import User
from django import forms
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(UserForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['email'].required = True