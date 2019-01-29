from django.contrib.auth.forms import UserCreationForm
from django import forms
from crispy_forms.helper import FormHelper
from django.contrib.auth.models import User
from email_hash import models
import uuid

class NewsletterUserSignUpForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_labels = False
    # helper.form_class = 'blueForms'
    # helper.update_attributes(maxlength="400")
    class Meta:
        model = models.NewsletterUser
        fields = ['project_name', 'email']

        def clean_project_name(self):
            project_name = self.clean_data.get('project_name')
            return project_name
        def clean_email(self):
            email = self.clean_data.get('email')
            return email



class UserRegisterForm(UserCreationForm):
    project_name = forms.CharField(
        max_length=100)
    email = forms.EmailField()
    # analysis_code = forms.CharField(
    #     max_length=32)
    class Meta:
        model = User
        fields = ['project_name', 'email']

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.username = self.cleaned_data["project_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # self.fields['password1'].required = False
        # self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        # self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        # self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        del self.fields['password1']
        del self.fields['password2']
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        # self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        # self.fields['password2'].widget.attrs['autocomplete'] = 'off'
