from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from .forms import InquiryForm

from .forms import CustomUserCreationForm, PropertyForm
from .models import Property, Inquiry


def home(request):
    featured_properties = Property.objects.all().order_by("-id")[:4]
    return render(request, "listings/home.html", {"featured_properties": featured_properties})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to Shelter & Soul!")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "listings/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect("home")
        else:
            messages.error(request, "Please enter a correct username and password.")
    else:
        form = AuthenticationForm()
    return render(request, "listings/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


def property_list(request):
    properties = Property.objects.all().order_by("-id")

    query = request.GET.get("q")
    location = request.GET.get("location")
    property_type = request.GET.get("property_type")

    if query:
        properties = properties.filter(name__icontains=query)

    if location:
        properties = properties.filter(location__icontains=location)

    if property_type:
        properties = properties.filter(property_type=property_type)

    context = {
        "properties": properties,
        "selected_query": query or "",
        "selected_location": location or "",
        "selected_type": property_type or "",
        "property_types": ["Residential", "Apartment", "Commercial", "Land"],
    }
    return render(request, "listings/properties.html", context)


def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    return render(request, "listings/property_detail.html", {"property": property_obj})


@login_required
def property_create(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Property added successfully!")
            return redirect("property_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PropertyForm()
    return render(request, "listings/property_form.html", {"form": form, "title": "Add Property"})


@login_required
def property_update(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Property updated successfully!")
            return redirect("property_detail", pk=property_obj.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PropertyForm(instance=property_obj)
    return render(request, "listings/property_form.html", {"form": form, "title": "Edit Property"})


@login_required
def property_delete(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        property_obj.delete()
        messages.success(request, "Property deleted successfully!")
        return redirect("property_list")
    return render(request, "listings/property_confirm_delete.html", {"property": property_obj})

@login_required
def send_inquiry(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)

    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.property = property_obj
            inquiry.save()
            messages.success(request, "Inquiry sent successfully!")
            return redirect('property_detail', pk=pk)
    else:
        form = InquiryForm()

    return render(request, 'listings/send_inquiry.html', {
        'form': form,
        'property': property_obj
    })