from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Property


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ["name", "location", "price", "property_type", "description", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]