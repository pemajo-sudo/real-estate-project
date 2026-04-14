from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

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


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"Image for {self.property.name}"


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


class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="inquiries")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150, default="Unknown")
    email = models.EmailField(default="unknown@example.com")
    message = models.TextField()
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