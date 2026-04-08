from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Property
from .models import Inquiry

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "name",
            "location",
            "price",
            "property_type",
            "number_of_rooms",
            "size_sqft",
            "description",
            "image",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    

class InquiryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].initial = ""
        self.fields["email"].initial = ""

    class Meta:
        model = Inquiry
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(),
            "email": forms.EmailInput(),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Write your message here..."})
        }
    