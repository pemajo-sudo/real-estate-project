from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Property
from .models import Inquiry
from .models import SellLead
from .models import VirtualTourScene
from .models import Visit
from .models import UserProfile

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
        widget=MultipleFileInput(attrs={'multiple': True}),
        help_text="Upload one or more images.",
        label="Property Images",
    )

    class Meta:
        model = Property
        fields = [
            "name",
            "location",
            "price",
            "listing_category",
            "property_type",
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
            "note": forms.Textarea(attrs={"rows": 3, "placeholder": "Note"}),
        }

    def clean_visit_date(self):
        visit_date = self.cleaned_data["visit_date"]
        if visit_date < timezone.localdate():
            raise forms.ValidationError("Visit date cannot be in the past.")
        return visit_date


class SellLeadForm(forms.ModelForm):
    class Meta:
        model = SellLead
        fields = ["name", "email", "phone", "property_type", "location", "message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell us about the unique features of your property..."}
            ),
        }


class VirtualTourSceneForm(forms.ModelForm):
    class Meta:
        model = VirtualTourScene
        fields = ["panorama_image", "panorama_url"]
        widgets = {
            "panorama_url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def clean(self):
        cleaned_data = super().clean()
        panorama_image = cleaned_data.get("panorama_image")
        panorama_url = cleaned_data.get("panorama_url")
        if not panorama_image and not panorama_url:
            raise forms.ValidationError("Please provide a panorama image or a panorama URL.")
        return cleaned_data


VirtualTourSceneFormSet = inlineformset_factory(
    Property,
    VirtualTourScene,
    form=VirtualTourSceneForm,
    extra=1,
    can_delete=True,
)

VirtualTourSceneUpdateFormSet = inlineformset_factory(
    Property,
    VirtualTourScene,
    form=VirtualTourSceneForm,
    extra=0,
    can_delete=True,
)


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email Address"}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "personal_contact_number",
            "whatsapp_number",
            "residential_address",
            "office_address",
            "city",
            "occupation",
            "preferred_property_interest",
            "short_bio",
        ]
        widgets = {
            "residential_address": forms.Textarea(attrs={"rows": 2}),
            "office_address": forms.Textarea(attrs={"rows": 2}),
            "short_bio": forms.Textarea(attrs={"rows": 3}),
        }