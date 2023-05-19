from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm


class CreateUserForm(UserCreationForm):
    """
    La form de l'utilisateur qui possède un username, un email, un mot de passe et un nom
    cela détermine à quoi ressemble un user
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
