import uuid
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


def project_name_generator():
    return "Project" + uuid.uuid1().hex


class TmpUserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    # password1 = forms.BooleanField()
    # password1.hidden_widget
    # password2 = forms.BooleanField()
    # password2.hidden_widget
    # password2 = forms.CharField(forms.PasswordInput(
        # attrs={'class': 'form-control', 'placeholder': 'Password Again'}))
    password1 = None  # Standard django password input
    password2 = None  # Standard django password confirmation input
    class Meta:
        model = User
        fields = ['email']
        # widgets = {
        #     'password1': forms.HiddenInput(),
        #     'password2': forms.HiddenInput(),
        # }
    # def save(self, commit=True):
    #     # Save the provided password in hashed format
    #     user = super(TmpUserRegisterForm, self).save(commit=False)
    #     default_password = "qwertyuiopasdfghjkl"  # Generate the default password
    #     user.set_password(default_password)  # Set de default password
    #     if commit:
    #         user.save()
    #     return user
        # form.fields['password1'].widget = forms.HiddenInput()
        # form.fields['password2'].widget = forms.HiddenInput()



    def __init__(self, *args, **kwargs):
        super(TmpUserRegisterForm, self).__init__(*args, **kwargs)
        # self.fields['username'] = project_name_generator()
        # del self.fields['password1']
        # del self.fields['password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
