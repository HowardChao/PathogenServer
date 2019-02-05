from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import uuid

def project_name_generator():
    return "Project" + uuid.uuid1().hex

class TmpUserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    # password1 = None  # Standard django password input
    # password2 = None  # Standard django password confirmation input
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(TmpUserRegisterForm, self).__init__(*args, **kwargs)
        # del self.fields['password1']
        # del self.fields['password2']
