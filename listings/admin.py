from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import NotRegistered

from .models import Agent, Inquiry, Property, PropertyImage, VirtualTourHotspot, VirtualTourScene, Visit, Wishlist


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "property_type", "price", "has_map_location", "has_video_walkthrough")
    search_fields = ("name", "location", "property_type")
    inlines = [PropertyImageInline]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "location",
                    "price",
                    "property_type",
                    "number_of_rooms",
                    "number_of_bathrooms",
                    "size_sqft",
                    "size_unit",
                    "description",
                )
            },
        ),
        (
            "Video Walkthrough",
            {
                "fields": ("walkthrough_video", "video_url"),
                "description": "Add either an uploaded video file or a YouTube/external video URL.",
            },
        ),
        (
            "Map Location",
            {
                "fields": ("address", "latitude", "longitude"),
                "description": "Add an address and precise coordinates to show an interactive map on the property page.",
            },
        ),
    )

    @admin.display(boolean=True, description="Has Map")
    def has_map_location(self, obj):
        return obj.latitude is not None and obj.longitude is not None

    @admin.display(boolean=True, description="Has Video")
    def has_video_walkthrough(self, obj):
        return bool(obj.walkthrough_video or obj.video_url)


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "date_joined", "last_login")
    ordering = ("-date_joined",)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "property", "created_at")
    list_filter = ("created_at", "property")
    search_fields = ("name", "email", "message", "property__name")


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "specialization", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "email", "specialization")
    fieldsets = (
        ("Basic Information", {"fields": ("name", "specialization", "email", "is_active")}),
        ("Profile", {"fields": ("bio", "deals_closed", "rating", "volume")}),
        ("Images", {"fields": ("photo", "photo_url")}),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "property", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "property__name")


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("user", "property", "visit_date", "visit_time", "created_at")
    list_filter = ("visit_date", "created_at")
    search_fields = ("user__username", "property__name", "note")


class VirtualTourHotspotInline(admin.TabularInline):
    model = VirtualTourHotspot
    extra = 1
    fk_name = "scene"


@admin.register(VirtualTourScene)
class VirtualTourSceneAdmin(admin.ModelAdmin):
    list_display = ("title", "property", "scene_key", "sort_order")
    list_filter = ("property",)
    search_fields = ("title", "scene_key", "property__name")
    inlines = [VirtualTourHotspotInline]