from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import NotRegistered

from .models import (
    Agent,
    Inquiry,
    Property,
    PropertyImage,
    SellLead,
    UserProfile,
    VirtualTourScene,
    Visit,
    Wishlist,
)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


class VirtualTourSceneInline(admin.StackedInline):
    model = VirtualTourScene
    extra = 1
    fields = ("panorama_image", "panorama_url")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location",
        "listing_category",
        "property_type",
        "price",
        "has_video_walkthrough",
    )
    list_filter = ("listing_category", "property_type")
    search_fields = ("name", "location", "listing_category", "property_type")
    inlines = [PropertyImageInline, VirtualTourSceneInline]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "owner",
                    "location",
                    "price",
                    "listing_category",
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
    )

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


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "can_post_property")
    list_filter = ("can_post_property",)
    search_fields = ("user__username", "user__email")


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


@admin.register(SellLead)
class SellLeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "user", "property_type", "status", "approval_notification_sent", "created_at")
    list_filter = ("status", "approval_notification_sent", "property_type", "created_at")
    search_fields = ("name", "email", "phone", "location", "message", "user__username")
    actions = ("approve_selected_leads", "reject_selected_leads")

    @staticmethod
    def _sync_posting_permission(user):
        if not user:
            return
        profile, _ = UserProfile.objects.get_or_create(user=user)
        has_approved_lead = SellLead.objects.filter(user=user, status=SellLead.STATUS_APPROVED).exists()
        if profile.can_post_property != has_approved_lead:
            profile.can_post_property = has_approved_lead
            profile.save(update_fields=["can_post_property"])

    @admin.action(description="Approve selected sell leads")
    def approve_selected_leads(self, request, queryset):
        user_ids = list(queryset.exclude(user__isnull=True).values_list("user_id", flat=True).distinct())
        queryset.update(status=SellLead.STATUS_APPROVED, approval_notification_sent=False)
        for user in User.objects.filter(id__in=user_ids):
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.can_post_property:
                profile.can_post_property = True
                profile.save(update_fields=["can_post_property"])
        self.message_user(request, f"Approved {queryset.count()} lead(s).")

    @admin.action(description="Reject selected sell leads")
    def reject_selected_leads(self, request, queryset):
        users = list(queryset.exclude(user__isnull=True).values_list("user", flat=True).distinct())
        queryset.update(status=SellLead.STATUS_REJECTED)
        for user_id in users:
            user = User.objects.filter(pk=user_id).first()
            self._sync_posting_permission(user)
        self.message_user(request, f"Rejected {queryset.count()} lead(s).")

    def save_model(self, request, obj, form, change):
        if obj.status == SellLead.STATUS_APPROVED and (not change or "status" in form.changed_data):
            obj.approval_notification_sent = False
        super().save_model(request, obj, form, change)
        self._sync_posting_permission(obj.user)

