from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegisterFrom(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter username",
        }))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password",
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password",
        })
    )


class Meta:
    model = User
    fields = ["username", "password1", "password2"]

class LoginForm(AuthenticationForm):
    username= forms.CharField(
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder": "Enter username",
        })
    )
    password= forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "placeholder": "Enter password",

        })
    )
    