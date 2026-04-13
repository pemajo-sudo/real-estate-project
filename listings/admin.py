from django.contrib import admin

from .models import Inquiry, Property, VirtualTourHotspot, VirtualTourScene, Visit, Wishlist


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "property_type", "price", "has_map_location", "has_video_walkthrough")
    search_fields = ("name", "location", "property_type")
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
                    "size_sqft",
                    "description",
                    "image",
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


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "property", "created_at")
    list_filter = ("created_at", "property")
    search_fields = ("name", "email", "message", "property__name")


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