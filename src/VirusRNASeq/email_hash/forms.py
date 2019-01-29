from django import forms
from crispy_forms.helper import FormHelper
from email_hash import models

class NewsletterUserSignUpForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_labels = False
    helper.form_class = 'blueForms'
    # helper.update_attributes(maxlength="400")

    class Meta:
        model = models.NewsletterUser
        fields = ['email']

        def clean_email(self):
            email = self.clean_data.get('email')
            return email
