from django import forms
from crispy_forms.helper import FormHelper
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.layout import Submit, Layout, ButtonHolder
from django.contrib.auth.models import User

class UserRegisteredForms(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password',widget=forms.PasswordInput)
    

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        help_texts = {k:"" for k in fields}