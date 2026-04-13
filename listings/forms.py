from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Property
from .models import Inquiry
from .models import Visit

class PropertyForm(forms.ModelForm):
    class MultipleFileInput(forms.ClearableFileInput):
        allow_multiple_selected = True

    class MultipleFileField(forms.FileField):
        def clean(self, data, initial=None):
            single_file_clean = super().clean
            if isinstance(data, (list, tuple)):
                return [single_file_clean(file_data, initial) for file_data in data]
            if data:
                return [single_file_clean(data, initial)]
            return []

    image_files = MultipleFileField(
        required=False,
        widget=MultipleFileInput(),
        help_text="Upload one or more images.",
        label="Property Images",
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
            "number_of_bathrooms",
            "size_sqft",
            "size_unit",
            "description",
            "walkthrough_video",
            "video_url",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "size_sqft": forms.NumberInput(attrs={"step": "0.01", "min": "0", "placeholder": "e.g. 1200"}),
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