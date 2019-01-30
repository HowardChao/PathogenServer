from django.contrib.auth.forms import UserCreationForm
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.contrib.auth.models import User
from email_hash import models
import uuid

class NewsletterUserSignUpForm(forms.ModelForm):
    helper = FormHelper()
    # helper.form_show_labels = False
    helper.form_class = 'form-vertical'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    # helper.layout = Layout(
    #     # 'email',
    #     'password',
    #     'remember_me',
    #     # StrictButton('Sign in', css_class='btn-default'),
    # )
    # helper.form_class = 'blueForms'
    # helper.update_attributes(maxlength="400")
    class Meta:
        model = models.NewsletterUser
        fields = ['project_name', 'email']

        # def clean_project_name(self):
        #     project_name = self.clean_data.get('project_name')
        #     return project_name
        # def clean_email(self):
        #     email = self.clean_data.get('email')
        #     return email


class NewsletterUserDeleteAnalysisForm(forms.ModelForm):
    helper = FormHelper()
    # helper.form_show_labels = False
    helper.form_class = 'form-vertical'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['project_name'] = ""
        kwargs['initial'] = initial
        super(NewsletterUserDeleteAnalysisForm, self).__init__(*args, **kwargs)


    class Meta:
        model = models.NewsletterUser
        # widgets = {'project_name': forms.HiddenInput(),
                #    'email': forms.HiddenInput(),}
        fields = ['project_name', 'email', 'analysis_code']


class NewsletterUserCheck(forms.ModelForm):
    helper = FormHelper()
    # helper.form_show_labels = False
    helper.form_class = 'form-vertical'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['project_name'] = ""
        kwargs['initial'] = initial
        super(NewsletterUserCheck, self).__init__(*args, **kwargs)

    class Meta:
        model = models.NewsletterUser
        # widgets = {'project_name': forms.HiddenInput(),'email': forms.HiddenInput(),}
        fields = ['analysis_code']
