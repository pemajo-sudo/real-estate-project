from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from urllib.parse import parse_qs, urlparse
import logging

logger = logging.getLogger(__name__)

from .forms import (
    CustomUserCreationForm,
    InquiryForm,
    PropertyForm,
    SellLeadForm,
    VirtualTourSceneFormSet,
    VisitForm,
)
from .models import Agent, Inquiry, Property, PropertyImage, SearchLog, SellLead, UserProfile, VirtualTourScene, Visit, Wishlist, RecentlyViewedProperty

COMPARE_SESSION_KEY = "compare_properties"
MAX_COMPARE_ITEMS = 3


def _can_user_post_property(user):
    if not user.is_authenticated:
        return False
    approved_leads_count = SellLead.objects.filter(user=user, status=SellLead.STATUS_APPROVED).count()
    properties_count = Property.objects.filter(owner=user).count()
    can_post = properties_count < approved_leads_count
    
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.can_post_property != can_post:
        profile.can_post_property = can_post
        profile.save(update_fields=["can_post_property"])
    return can_post


def _notify_user_on_sell_approval(request, user):
    pending_notifications = SellLead.objects.filter(
        user=user,
        status=SellLead.STATUS_APPROVED,
        approval_notification_sent=False,
    )
    if not pending_notifications.exists():
        return

    pending_notifications.update(approval_notification_sent=True)
    messages.success(
        request,
        "Good news! Your request has been approved. Now you can add property",
    )


def _youtube_embed_url(url):
    if not url:
        return ""

    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().replace("www.", "")
    path_parts = [part for part in parsed.path.split("/") if part]
    video_id = ""

    if host in {"youtube.com", "m.youtube.com"}:
        if path_parts and path_parts[0] == "watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif path_parts and path_parts[0] in {"shorts", "live", "embed"} and len(path_parts) > 1:
            video_id = path_parts[1]
    elif host == "youtu.be" and path_parts:
        video_id = path_parts[0]

    if video_id:
        return f"https://www.youtube.com/embed/{video_id}?rel=0"

    return ""


def _wants_json_response(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def home(request):
    featured_properties = Property.objects.prefetch_related("images").order_by("-id")[:4]
    wishlisted_ids = []
    if request.user.is_authenticated:
        wishlisted_ids = list(
            Wishlist.objects.filter(user=request.user).values_list("property_id", flat=True)
        )
    return render(
        request,
        "listings/home.html",
        {
            "featured_properties": featured_properties,
            "wishlisted_ids": wishlisted_ids,
        },
    )


def find_agent(request):
    """Renders the Find an Agent directory page."""
    search_query = request.GET.get("q", "").strip()
    agents = Agent.objects.filter(is_active=True).order_by("name")
    if search_query:
        agents = agents.filter(name__icontains=search_query)
    return render(request, "listings/find_agent.html", {"agents": agents, "search_query": search_query})


@login_required
def sell_property(request):
    """Renders the Sell property lead capture page."""
    if request.method == "POST":
        db_engine = settings.DATABASES['default']['ENGINE']
        db_name = str(settings.DATABASES['default'].get('NAME', 'unknown'))
        print("===" * 15)
        print(f"[SellLead] Request received from host: {request.get_host()}")
        print(f"[SellLead] User: {request.user.username} | Authenticated: {request.user.is_authenticated}")
        print(f"[SellLead] DB Engine: {db_engine} | DB Name: {db_name}")
        print("===" * 15)
        
        logger.debug(f"SellLead POST data received from user {request.user.username}")
        post_data = request.POST.copy()
        if not post_data.get("name"):
            post_data["name"] = request.user.get_full_name().strip() or request.user.username
        if not post_data.get("email"):
            post_data["email"] = request.user.email or "unknown@example.com"
            
        form = SellLeadForm(post_data, request.FILES)
        if form.is_valid():
            try:
                lead = form.save(commit=False)
                lead.user = request.user
                lead.status = SellLead.STATUS_PENDING
                lead.save()
                logger.info(f"SellLead saved successfully: {lead}")
                print("Saved successfully:", lead)
                messages.success(request, "Thank you! Your request has been received. We’ll contact you shortly.")
                return render(request, "listings/sell.html", {"success": True, "form": SellLeadForm()})
            except Exception as e:
                logger.error(f"Error saving SellLead form: {e}")
                print("Error saving SellLead form:", e)
                messages.error(request, "An unexpected error occurred while saving your request. Please try again.")
        else:
            logger.warning(f"SellLeadForm validation failed for user {request.user.username}. Errors: {form.errors}")
            print("SellLeadForm errors:", form.errors)
            messages.error(request, "Please correct the highlighted fields and submit again.")
    else:
        form = SellLeadForm()
    return render(request, "listings/sell.html", {"form": form})


def about(request):
    """Renders the professional About Us page."""
    return render(request, "listings/about.html")


@login_required
def dashboard_view(request):
    """Renders the User Dashboard with wishlists, inquiries, etc."""
    wishlist_items = (
        Wishlist.objects.filter(user=request.user)
        .select_related("property")
        .order_by("-created_at")[:5]
    )
    inquiries = Inquiry.objects.filter(user=request.user).order_by("-created_at")[:5]
    
    # Placeholders for features not yet in the DB model
    my_posts = Property.objects.filter(owner=request.user).order_by("-id")[:5]
    recent_views = RecentlyViewedProperty.objects.filter(user=request.user).select_related("property").prefetch_related("property__images").order_by("-viewed_at")[:5]
    
    context = {
        "wishlist_items": wishlist_items,
        "inquiries": inquiries,
        "my_posts": my_posts,
        "recent_views": recent_views,
        "can_post_property": _can_user_post_property(request.user),
    }
    return render(request, "listings/dashboard.html", context)


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
            _notify_user_on_sell_approval(request, user)
            return redirect("home")
        else:
            messages.error(request, "Please enter a correct username and password.")
    else:
        form = AuthenticationForm()
    return render(request, "listings/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


def property_list(request):
    properties = Property.objects.prefetch_related("images").order_by("-id")

    listing_type = request.GET.get("type", "").strip().lower()
    query = request.GET.get("q")
    location = request.GET.get("location", "").strip()
    property_type = request.GET.get("property_type")
    bedrooms = request.GET.get("bedrooms")
    bathrooms = request.GET.get("bathrooms")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    sort = request.GET.get("sort", "").strip()

    if query:
        properties = properties.filter(name__icontains=query)

    if location:
        properties = properties.filter(location__icontains=location)

    if property_type:
        properties = properties.filter(property_type=property_type)

    if listing_type in {"rent"}:
        properties = properties.filter(listing_category="Rent")
    elif listing_type in {"sell", "buy"}:
        properties = properties.filter(listing_category="Sell")

    if bedrooms:
        properties = properties.filter(number_of_rooms__gte=bedrooms)

    if bathrooms:
        properties = properties.filter(number_of_bathrooms__gte=bathrooms)

    if price_min:
        properties = properties.filter(price__gte=price_min)

    if price_max:
        properties = properties.filter(price__lte=price_max)

    if sort == "price_low":
        properties = properties.order_by("price", "-id")
    elif sort == "price_high":
        properties = properties.order_by("-price", "-id")
    elif sort == "newest":
        properties = properties.order_by("-id")

    if request.user.is_authenticated and (query or location or property_type or listing_type):
        last_search = SearchLog.objects.filter(user=request.user).first()
        current_query = query or ""
        current_type = property_type or ""
        if not (last_search and last_search.query == current_query and last_search.location == location and last_search.property_type == current_type and last_search.listing_category == listing_type):
            SearchLog.objects.create(
                user=request.user,
                query=current_query,
                location=location,
                property_type=current_type,
                listing_category=listing_type,
            )

    compared_ids = request.session.get(COMPARE_SESSION_KEY, [])
    wishlisted_ids = []
    if request.user.is_authenticated:
        wishlisted_ids = list(
            Wishlist.objects.filter(user=request.user).values_list("property_id", flat=True)
        )
    map_properties = [
        {
            "id": property_obj.id,
            "name": property_obj.name,
            "location": property_obj.location,
            "price": float(property_obj.price),
            "listing_category": property_obj.listing_category,
            "detail_url": reverse("property_detail", args=[property_obj.id]),
            "latitude": float(property_obj.latitude) if property_obj.latitude is not None else None,
            "longitude": float(property_obj.longitude) if property_obj.longitude is not None else None,
        }
        for property_obj in properties
    ]
    context = {
        "properties": properties,
        "selected_query": query or "",
        "selected_location": location or "",
        "selected_type": property_type or "",
        "selected_listing_type": listing_type,
        "property_types": ["Residential", "Apartment", "Commercial", "Land"],
        "compared_ids": compared_ids,
        "compare_count": len(compared_ids),
        "wishlisted_ids": wishlisted_ids,
        "map_properties": map_properties,
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, "listings/properties.html", context)


def _get_property_detail_context(request, property_obj):
    property_images = property_obj.images.all()
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

    youtube_embed_url = _youtube_embed_url(property_obj.video_url)

    return {
        "property": property_obj,
        "in_wishlist": in_wishlist,
        "is_compared": property_obj.pk in compared_ids,
        "compare_count": len(compared_ids),
        "tour_scenes": tour_config,
        "default_tour_scene": default_scene,
        "youtube_embed_url": youtube_embed_url,
        "property_images": property_images,
    }


def property_detail(request, pk):
    property_obj = get_object_or_404(Property.objects.prefetch_related("images"), pk=pk)
    context = _get_property_detail_context(request, property_obj)
    
    inquiry_form = InquiryForm()
    if request.user.is_authenticated:
        inquiry_form = InquiryForm()
        obj, created = RecentlyViewedProperty.objects.get_or_create(user=request.user, property=property_obj)
        if not created:
            obj.save()
        
    context["inquiry_form"] = inquiry_form

    return render(
        request,
        "listings/property_detail.html",
        context,
    )


@login_required
def send_inquiry(request, pk):
    property_obj = get_object_or_404(Property.objects.prefetch_related("images"), pk=pk)

    if request.method != "POST":
        return redirect("property_detail", pk=pk)

    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = str(settings.DATABASES['default'].get('NAME', 'unknown'))
    print("===" * 15)
    print(f"[Inquiry] Request received from host: {request.get_host()}")
    print(f"[Inquiry] User: {request.user.username} | Authenticated: {request.user.is_authenticated}")
    print(f"[Inquiry] DB Engine: {db_engine} | DB Name: {db_name}")
    print("===" * 15)

    logger.debug(f"Inquiry POST data received from user {request.user.username} for property {pk}")
    post_data = request.POST.copy()
    if not post_data.get("name"):
        post_data["name"] = request.user.get_full_name().strip() or request.user.username
    if not post_data.get("email"):
        post_data["email"] = request.user.email or "unknown@example.com"

    inquiry_form = InquiryForm(post_data, request.FILES)
    if inquiry_form.is_valid():
        try:
            inquiry = inquiry_form.save(commit=False)
            inquiry.property = property_obj
            inquiry.user = request.user
            inquiry.save()
            logger.info(f"Inquiry saved successfully: {inquiry}")
            print("Saved successfully:", inquiry)
            messages.success(request, "Your inquiry has been sent successfully.")
            return redirect("property_detail", pk=pk)
        except Exception as e:
            logger.error(f"Error saving Inquiry form: {e}")
            print("Error saving Inquiry form:", e)
            messages.error(request, "An unexpected error occurred while saving your inquiry. Please try again.")
    else:
        logger.warning(f"InquiryForm validation failed for user {request.user.username}. Errors: {inquiry_form.errors}")
        print("InquiryForm errors:", inquiry_form.errors)
        messages.error(request, "Please correct the errors below and try again.")
    
    context = _get_property_detail_context(request, property_obj)
    context["inquiry_form"] = inquiry_form
    return render(
        request,
        "listings/property_detail.html",
        context,
    )


@login_required
def schedule_visit(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.user = request.user
            visit.property = property_obj
            visit.save()
            messages.success(request, "Visit scheduled successfully.")
            return redirect("property_detail", pk=pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = VisitForm()

    return render(
        request,
        "listings/schedule_visit.html",
        {"form": form, "property": property_obj},
    )


@login_required
def add_to_wishlist(request, pk):
    if request.method != "POST":
        return redirect("property_detail", pk=pk)

    property_obj = get_object_or_404(Property, pk=pk)
    _, created = Wishlist.objects.get_or_create(user=request.user, property=property_obj)
    if _wants_json_response(request):
        return JsonResponse(
            {
                "success": True,
                "is_wishlisted": True,
                "created": created,
                "property_id": property_obj.pk,
            }
        )
    if created:
        messages.success(request, "Property added to your wishlist.")
    else:
        messages.info(request, "This property is already in your wishlist.")
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
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
def wishlist_status(request):
    raw_ids = request.GET.getlist("ids")
    property_ids = []
    for raw_id in raw_ids:
        try:
            property_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue

    if not property_ids:
        return JsonResponse({"wishlisted_ids": []})

    wishlisted_ids = list(
        Wishlist.objects.filter(user=request.user, property_id__in=property_ids).values_list(
            "property_id", flat=True
        )
    )
    return JsonResponse({"wishlisted_ids": wishlisted_ids})


@login_required
def remove_from_wishlist(request, pk):
    if request.method != "POST":
        return redirect("wishlist")

    property_obj = get_object_or_404(Property, pk=pk)
    deleted_count, _ = Wishlist.objects.filter(user=request.user, property=property_obj).delete()
    if _wants_json_response(request):
        return JsonResponse(
            {
                "success": True,
                "is_wishlisted": False,
                "removed": bool(deleted_count),
                "property_id": property_obj.pk,
            }
        )
    if deleted_count:
        messages.success(request, "Property removed from your wishlist.")
    else:
        messages.info(request, "Property was not in your wishlist.")
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
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


def clear_compare(request):
    if request.method != "POST":
        return redirect("compare_properties")

    request.session[COMPARE_SESSION_KEY] = []
    messages.success(request, "Comparison list cleared.")
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
    if not _can_user_post_property(request.user):
        messages.error(request, "Your seller account is not approved yet. Please submit a Sell With Us request.")
        return redirect("sell")

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            scene_formset = VirtualTourSceneFormSet(
                request.POST,
                request.FILES,
                instance=property_obj,
                prefix="scenes",
            )
            if scene_formset.is_valid():
                property_obj.save()
                form.save_m2m()
                scene_formset.save()
                _can_user_post_property(request.user)
            else:
                messages.error(request, "Please correct the virtual tour scene errors below.")
                return render(
                    request,
                    "listings/property_form.html",
                    {"form": form, "scene_formset": scene_formset, "title": "Add Property"},
                )
            for image_file in request.FILES.getlist("image_files"):
                PropertyImage.objects.create(property=property_obj, image=image_file)
            messages.success(request, "Property added successfully!")
            return redirect("property_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PropertyForm()
    scene_formset = VirtualTourSceneFormSet(instance=Property(owner=request.user), prefix="scenes")
    return render(
        request,
        "listings/property_form.html",
        {"form": form, "scene_formset": scene_formset, "title": "Add Property"},
    )


@login_required
def property_update(request, pk):
    property_obj = get_object_or_404(Property.objects.prefetch_related("images"), pk=pk)
    if not (request.user.is_staff or request.user.is_superuser or property_obj.owner == request.user):
        raise PermissionDenied("You can only edit your own properties.")

    if property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied("You can only manage virtual tour scenes for your own properties.")

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        scene_formset = VirtualTourSceneFormSet(
            request.POST,
            request.FILES,
            instance=property_obj,
            prefix="scenes",
        )
        if form.is_valid() and scene_formset.is_valid():
            property_obj = form.save()
            scene_formset.save()
            for image_file in request.FILES.getlist("image_files"):
                PropertyImage.objects.create(property=property_obj, image=image_file)
            messages.success(request, "Property updated successfully!")
            return redirect("property_detail", pk=property_obj.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PropertyForm(instance=property_obj)
        scene_formset = VirtualTourSceneFormSet(instance=property_obj, prefix="scenes")
    return render(
        request,
        "listings/property_form.html",
        {"form": form, "scene_formset": scene_formset, "title": "Edit Property"},
    )


@login_required
def property_delete(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if not (request.user.is_staff or request.user.is_superuser or property_obj.owner == request.user):
        raise PermissionDenied("You can only delete your own properties.")
    if request.method == "POST":
        property_obj.delete()
        _can_user_post_property(request.user)
        messages.success(request, "Property deleted successfully!")
        return redirect("property_list")
    return render(request, "listings/property_confirm_delete.html", {"property": property_obj})


@login_required
def view_inquiries(request):
    inquiries = Inquiry.objects.filter(user=request.user).order_by("-id")
    return render(request, "listings/view_inquiries.html", {"inquiries": inquiries})