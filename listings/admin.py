from django.contrib import admin

from .models import Inquiry, Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "property_type", "price")
    search_fields = ("name", "location", "property_type")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "property", "created_at")
    list_filter = ("created_at", "property")
    search_fields = ("name", "email", "message", "property__name")