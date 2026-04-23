from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify
from pathlib import Path
import hashlib

class Property(models.Model):
    LISTING_CATEGORIES = [
        ("Sell", "Sell"),
        ("Rent", "Rent"),
    ]

    PROPERTY_TYPES = [
        ("Residential", "Residential"),
        ("Apartment", "Apartment"),
        ("Commercial", "Commercial"),
        ("Land", "Land"),
    ]
    SIZE_UNITS = [
        ("sqft", "sqft"),
        ("acres", "Acres"),
        ("perch", "Perch"),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    listing_category = models.CharField(max_length=20, choices=LISTING_CATEGORIES, default="Sell")
    property_type = models.CharField(
        max_length=100,
        choices=PROPERTY_TYPES,
        default="Residential"
    )
    description = models.TextField()
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True)
    number_of_bathrooms = models.PositiveIntegerField(null=True, blank=True)
    size_sqft = models.DecimalField("Size", max_digits=12, decimal_places=2, null=True, blank=True)
    size_unit = models.CharField(max_length=20, choices=SIZE_UNITS, default="sqft")
    walkthrough_video = models.FileField(upload_to="", null=True, blank=True)
    video_url = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="properties")

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        return self.images.first()

    def save(self, *args, **kwargs):
        _deduplicate_uploaded_field(self, "walkthrough_video")
        
        if self.location and (not self.latitude or not self.longitude):
            import urllib.request
            import urllib.parse
            import json

            text = self.location.lower()
            lookup = {
                "colombo": (6.9271, 79.8612),
                "rajagiriya": (6.9069, 79.8952),
                "dehiwala": (6.8510, 79.8653),
                "mount lavinia": (6.8389, 79.8651),
                "moratuwa": (6.7730, 79.8825),
                "negombo": (7.2084, 79.8358),
                "kandy": (7.2906, 80.6337),
                "galle": (6.0535, 80.2210),
                "matara": (5.9549, 80.5550),
                "kurunegala": (7.4863, 80.3647),
                "jaffna": (9.6615, 80.0255),
                "anuradhapura": (8.3114, 80.4037),
                "batticaloa": (7.7170, 81.7000),
                "trincomalee": (8.5874, 81.2152),
                "nuwara eliya": (6.9497, 80.7891),
                "badulla": (6.9934, 81.0550),
                "ratnapura": (6.6828, 80.3992),
            }
            
            found = False
            for key, coords in lookup.items():
                if key in text:
                    self.latitude, self.longitude = coords
                    found = True
                    break
            
            if not found:
                try:
                    url = f"https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=lk&q={urllib.parse.quote(self.location)}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'ShelterAndSoulApp/1.0'})
                    with urllib.request.urlopen(req, timeout=3) as response:
                        data = json.loads(response.read().decode())
                        if data:
                            self.latitude = data[0]['lat']
                            self.longitude = data[0]['lon']
                except Exception:
                    pass

        super().save(*args, **kwargs)


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Image for {self.property.name}"

    def save(self, *args, **kwargs):
        _deduplicate_uploaded_field(self, "image")
        super().save(*args, **kwargs)


class Agent(models.Model):
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120, blank=True)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    deals_closed = models.CharField(max_length=30, blank=True)
    rating = models.CharField(max_length=20, blank=True)
    volume = models.CharField(max_length=40, blank=True)
    photo = models.ImageField(upload_to="", null=True, blank=True)
    photo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_photo_source(self):
        if self.photo:
            return self.photo.url
        return self.photo_url

    def save(self, *args, **kwargs):
        _deduplicate_uploaded_field(self, "photo")
        super().save(*args, **kwargs)


class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="inquiries")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150, default="Unknown")
    email = models.EmailField(default="unknown@example.com")
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True, help_text="Admin's reply to this inquiry")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry from {self.name} on {self.property}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "property"], name="unique_user_property_wishlist")
        ]

    def __str__(self):
        return f"{self.user} -> {self.property}"


class VirtualTourScene(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="tour_scenes")
    title = models.CharField(max_length=120)
    scene_key = models.SlugField(max_length=80)
    panorama_image = models.ImageField(upload_to="", null=True, blank=True)
    panorama_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["property", "scene_key"], name="unique_scene_key_per_property")
        ]

    def __str__(self):
        return f"{self.property.name} - {self.title}"

    def get_panorama_source(self):
        if self.panorama_image:
            return self.panorama_image.url
        return self.panorama_url

    def save(self, *args, **kwargs):
        _deduplicate_uploaded_field(self, "panorama_image")

        if not self.title:
            self.title = "Virtual Tour Scene"

        if not self.scene_key:
            base_key = slugify(self.title) or "virtual-tour-scene"
            candidate_key = base_key
            suffix = 2
            while VirtualTourScene.objects.filter(
                property=self.property,
                scene_key=candidate_key,
            ).exclude(pk=self.pk).exists():
                candidate_key = f"{base_key}-{suffix}"
                suffix += 1
            self.scene_key = candidate_key

        if not self.sort_order:
            max_sort_order = (
                VirtualTourScene.objects.filter(property=self.property)
                .exclude(pk=self.pk)
                .aggregate(models.Max("sort_order"))["sort_order__max"]
            )
            self.sort_order = (max_sort_order or 0) + 1

        super().save(*args, **kwargs)


def _get_file_sha256(file_obj):
    current_pos = None
    try:
        current_pos = file_obj.tell()
    except Exception:
        current_pos = None

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
    except Exception:
        pass

    hasher = hashlib.sha256()
    for chunk in file_obj.chunks() if hasattr(file_obj, "chunks") else iter(lambda: file_obj.read(8192), b""):
        if not chunk:
            break
        hasher.update(chunk)

    try:
        if current_pos is not None and hasattr(file_obj, "seek"):
            file_obj.seek(current_pos)
    except Exception:
        pass

    return hasher.hexdigest()


def _find_existing_media_file(uploaded_file):
    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.exists():
        return None

    uploaded_size = getattr(uploaded_file, "size", None)
    uploaded_hash = _get_file_sha256(uploaded_file)

    for existing_path in media_root.rglob("*"):
        if not existing_path.is_file():
            continue
        if uploaded_size is not None and existing_path.stat().st_size != uploaded_size:
            continue

        with existing_path.open("rb") as existing_file:
            existing_hash = _get_file_sha256(existing_file)
            if existing_hash == uploaded_hash:
                return existing_path.relative_to(media_root).as_posix()
    return None


def _deduplicate_uploaded_field(instance, field_name):
    field_file = getattr(instance, field_name, None)
    if not field_file:
        return
    if getattr(field_file, "_committed", True):
        return

    uploaded_file = getattr(field_file, "file", None)
    if not uploaded_file:
        return

    existing_relative_path = _find_existing_media_file(uploaded_file)
    if existing_relative_path:
        setattr(instance, field_name, existing_relative_path)


class VirtualTourHotspot(models.Model):
    scene = models.ForeignKey(VirtualTourScene, on_delete=models.CASCADE, related_name="hotspots")
    pitch = models.FloatField(help_text="Vertical position, from -90 to 90")
    yaw = models.FloatField(help_text="Horizontal position, from -180 to 180")
    label = models.CharField(max_length=120)
    target_scene = models.ForeignKey(
        VirtualTourScene,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_hotspots",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.scene.title}: {self.label}"


class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visits")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="visits")
    visit_date = models.DateField()
    visit_time = models.TimeField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} visit for {self.property.name} on {self.visit_date}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    can_post_property = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} profile"


class SellLead(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_APPROVED = "Approved"
    STATUS_REJECTED = "Rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    PROPERTY_TYPES = [
        ("Residential", "Residential"),
        ("Apartment", "Apartment"),
        ("Commercial", "Commercial"),
        ("Land", "Land"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sell_leads")
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    property_type = models.CharField(max_length=100, choices=PROPERTY_TYPES)
    location = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approval_notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.property_type} ({self.location})"


class SearchLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recent_searches")
    query = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    property_type = models.CharField(max_length=100, blank=True)
    listing_category = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Search by {self.user.username} on {self.created_at}"

    @property
    def display_text(self):
        parts = []
        if self.query:
            parts.append(f'"{self.query}"')
        if self.location:
            parts.append(f"in {self.location}")
        if self.property_type:
            parts.append(f"Type: {self.property_type}")
        if self.listing_category:
            parts.append(f"For {self.listing_category.capitalize()}")
        
        return ", ".join(parts) if parts else "All Properties"

    @property
    def search_url(self):
        from django.urls import reverse
        from urllib.parse import urlencode
        
        base_url = reverse("property_list")
        params = {}
        if self.query:
            params["q"] = self.query
        if self.location:
            params["location"] = self.location
        if self.property_type:
            params["property_type"] = self.property_type
        if self.listing_category:
            params["type"] = self.listing_category
            
            return f"{base_url}?{urlencode(params)}"
        return base_url


class RecentlyViewedProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recently_viewed")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="viewed_by")
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-viewed_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "property"], name="unique_user_recently_viewed")
        ]

    def __str__(self):
        return f"{self.user.username} viewed {self.property.name}"