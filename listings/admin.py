from django.contrib import admin

from .models import Inquiry, Property, VirtualTourHotspot, VirtualTourScene, Wishlist


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "property_type", "price")
    search_fields = ("name", "location", "property_type")


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