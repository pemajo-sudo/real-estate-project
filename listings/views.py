from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserCreationForm, InquiryForm, PropertyForm
from .models import Inquiry, Property, VirtualTourScene, Wishlist

COMPARE_SESSION_KEY = "compare_properties"
MAX_COMPARE_ITEMS = 3


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

    compared_ids = request.session.get(COMPARE_SESSION_KEY, [])
    context = {
        "properties": properties,
        "selected_query": query or "",
        "selected_location": location or "",
        "selected_type": property_type or "",
        "property_types": ["Residential", "Apartment", "Commercial", "Land"],
        "compared_ids": compared_ids,
    }
    return render(request, "listings/properties.html", context)


def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    inquiry_form = InquiryForm()
    in_wishlist = False
    compared_ids = request.session.get(COMPARE_SESSION_KEY, [])
    scenes = (
        VirtualTourScene.objects.filter(property=property_obj)
        .prefetch_related("hotspots", "hotspots__target_scene")
        .order_by("sort_order", "id")
    )
    tour_config = {}
    default_scene = ""

    for scene in scenes:
        panorama_source = scene.get_panorama_source()
        if not panorama_source:
            continue

        if not default_scene:
            default_scene = scene.scene_key

        scene_hotspots = []
        for hotspot in scene.hotspots.all():
            hotspot_payload = {
                "pitch": hotspot.pitch,
                "yaw": hotspot.yaw,
                "createTooltipFunc": "hotspotLabelTooltip",
                "createTooltipArgs": hotspot.label,
            }
            if hotspot.target_scene:
                hotspot_payload["type"] = "scene"
                hotspot_payload["text"] = hotspot.label
                hotspot_payload["sceneId"] = hotspot.target_scene.scene_key
            else:
                hotspot_payload["type"] = "info"
                hotspot_payload["text"] = hotspot.label
            scene_hotspots.append(hotspot_payload)

        tour_config[scene.scene_key] = {
            "title": scene.title,
            "type": "equirectangular",
            "panorama": panorama_source,
            "hotSpots": scene_hotspots,
        }

    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, property=property_obj).exists()
    return render(
        request,
        "listings/property_detail.html",
        {
            "property": property_obj,
            "inquiry_form": inquiry_form,
            "in_wishlist": in_wishlist,
            "is_compared": property_obj.pk in compared_ids,
            "compare_count": len(compared_ids),
            "tour_scenes": tour_config,
            "default_tour_scene": default_scene,
        },
    )


def send_inquiry(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)

    if request.method != "POST":
        return redirect("property_detail", pk=pk)

    inquiry_form = InquiryForm(request.POST)
    if inquiry_form.is_valid():
        inquiry = inquiry_form.save(commit=False)
        inquiry.property = property_obj
        if request.user.is_authenticated:
            inquiry.user = request.user
        inquiry.save()
        messages.success(request, "Your inquiry has been sent successfully.")
        return redirect("property_detail", pk=pk)

    messages.error(request, "Please correct the errors below and try again.")
    return render(
        request,
        "listings/property_detail.html",
        {"property": property_obj, "inquiry_form": inquiry_form},
    )


@login_required
def add_to_wishlist(request, pk):
    if request.method != "POST":
        return redirect("property_detail", pk=pk)

    property_obj = get_object_or_404(Property, pk=pk)
    _, created = Wishlist.objects.get_or_create(user=request.user, property=property_obj)
    if created:
        messages.success(request, "Property added to your wishlist.")
    else:
        messages.info(request, "This property is already in your wishlist.")
    return redirect("property_detail", pk=pk)


@login_required
def wishlist_view(request):
    wishlist_items = (
        Wishlist.objects.filter(user=request.user)
        .select_related("property")
        .order_by("-created_at")
    )
    return render(request, "listings/wishlist.html", {"wishlist_items": wishlist_items})


@login_required
def remove_from_wishlist(request, pk):
    if request.method != "POST":
        return redirect("wishlist")

    property_obj = get_object_or_404(Property, pk=pk)
    deleted_count, _ = Wishlist.objects.filter(user=request.user, property=property_obj).delete()
    if deleted_count:
        messages.success(request, "Property removed from your wishlist.")
    else:
        messages.info(request, "Property was not in your wishlist.")
    return redirect("wishlist")


def add_to_compare(request, pk):
    if request.method != "POST":
        return redirect("property_list")

    get_object_or_404(Property, pk=pk)
    compared_ids = request.session.get(COMPARE_SESSION_KEY, [])

    if pk in compared_ids:
        messages.info(request, "This property is already selected for comparison.")
    elif len(compared_ids) >= MAX_COMPARE_ITEMS:
        messages.error(request, f"You can compare up to {MAX_COMPARE_ITEMS} properties.")
    else:
        compared_ids.append(pk)
        request.session[COMPARE_SESSION_KEY] = compared_ids
        messages.success(request, "Property added to comparison.")

    return redirect(request.POST.get("next") or "property_list")


def remove_from_compare(request, pk):
    if request.method != "POST":
        return redirect("compare_properties")

    compared_ids = request.session.get(COMPARE_SESSION_KEY, [])
    if pk in compared_ids:
        compared_ids.remove(pk)
        request.session[COMPARE_SESSION_KEY] = compared_ids
        messages.success(request, "Property removed from comparison.")
    return redirect(request.POST.get("next") or "compare_properties")


def compare_properties(request):
    compared_ids = request.session.get(COMPARE_SESSION_KEY, [])
    compared_properties = list(Property.objects.filter(id__in=compared_ids))
    order_map = {property_id: index for index, property_id in enumerate(compared_ids)}
    compared_properties.sort(key=lambda property_obj: order_map.get(property_obj.id, 0))
    return render(
        request,
        "listings/compare_properties.html",
        {
            "properties": compared_properties,
            "compare_count": len(compared_properties),
        },
    )


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