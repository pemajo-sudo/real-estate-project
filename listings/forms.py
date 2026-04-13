from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Property
from .models import Inquiry
from .models import Visit


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = dict(attrs or ())
        attrs.setdefault("multiple", True)
        super().__init__(attrs)


class PropertyForm(forms.ModelForm):
    images = forms.FileField(
        label="Photos",
        required=False,
        widget=MultipleFileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = Property
        fields = [
            "name",
            "location",
            "price",
            "property_type",
            "address",
            "latitude",
            "longitude",
            "number_of_rooms",
            "number_of_baths",
            "size_sqft",
            "description",
            "walkthrough_video",
            "video_url",
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


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ["visit_date", "visit_time", "note"]
        widgets = {
            "visit_date": forms.DateInput(attrs={"type": "date"}),
            "visit_time": forms.TimeInput(attrs={"type": "time"}),
            "note": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional note"}),
        }

    def clean_visit_date(self):
        visit_date = self.cleaned_data["visit_date"]
        if visit_date < timezone.localdate():
            raise forms.ValidationError("Visit date cannot be in the past.")
        return visit_date