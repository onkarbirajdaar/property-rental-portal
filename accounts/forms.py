from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile


class RegisterFrom(UserCreationForm):
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select",
        }),
    )
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

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.role = self.cleaned_data["role"]
            user.profile.save(update_fields=["role"])
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter username",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password",

        })
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter first name",

            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter last name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email",

            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "city", "role", "photo"]
        widgets = {
    "phone": forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter phone number",   
    }),
    "city": forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter city",
    }),
    "role": forms.Select(attrs={
        "class": "form-select",
    }),
    "photo": forms.ClearableFileInput(attrs={
        "class": "form-control",
    }),
}
        
