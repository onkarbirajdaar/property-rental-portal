from django import forms
from .models import Property, Interest


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "title",
            "property_type",
            "rent",
            "deposit",
            "bhk",
            "furnished",
            "address",
            "city",
            "area",
            "description",
            "contact_number",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter property name",
            }),
            "property_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "rent": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter monthly rent",
            }),
            "deposit": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter deposit amount",
            }),
            "bhk": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter BHK",
            }),
            "furnished": forms.Select(attrs={
                "class": "form-select",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter full address",
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter city",
            }),
            "area": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter area",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe the property",
            }),
            "contact_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter contact number",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }
        
    def clean_rent(self):
        rent = self.cleaned_data.get("rent")

        if rent <= 0:
            raise forms.ValidationError("Rent must be greater than 0.")

        return rent

    def clean_deposit(self):
        deposit = self.cleaned_data.get("deposit")

        if deposit < 0:
            raise forms.ValidationError("Deposit cannot be negative.")

        return deposit

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get("contact_number")

        if contact_number and not contact_number.isdigit():
            raise forms.ValidationError("Contact number should contain only digits.")

        if contact_number and len(contact_number) != 10:
            raise forms.ValidationError("Contact number must be 10 digits.")

        return contact_number    



class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ["message"]  
        widgets = {
            "message": forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Write a message to the owner (optional)",
                }),
            
        }    