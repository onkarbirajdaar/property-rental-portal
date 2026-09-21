from django import forms
from .models import Property, Interest, PROPERTY_TYPES, FURNISHED_CHOICES


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
            "status"
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
            "status": forms.Select(attrs={
            "class": "form-select",
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


class PropertySearchForm(forms.Form):
    SORT_CHOICES = [
        ("", "Sort By"),
        ("rent_low", "Lowest Rent"),
        ("rent_high", "Highest Rent"),
        ("latest", "Latest"),
    ]

    city = forms.CharField(required=False, max_length=100)
    area = forms.CharField(required=False, max_length=100)
    bhk = forms.IntegerField(required=False, min_value=1)
    min_rent = forms.DecimalField(required=False, min_value=0, max_digits=10, decimal_places=2)
    max_rent = forms.DecimalField(required=False, min_value=0, max_digits=10, decimal_places=2)
    property_type = forms.ChoiceField(required=False, choices=[("", "Any type"), *PROPERTY_TYPES])
    furnished = forms.ChoiceField(required=False, choices=[("", "Any furnishing"), *FURNISHED_CHOICES])
    sort = forms.ChoiceField(required=False, choices=SORT_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        min_rent = cleaned_data.get("min_rent")
        max_rent = cleaned_data.get("max_rent")

        if min_rent is not None and max_rent is not None and min_rent > max_rent:
            raise forms.ValidationError("Minimum rent cannot be higher than maximum rent.")

        return cleaned_data
