from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    PROPERTY_TYPES = [
        ("Residential", "Residential"),
        ("Apartment", "Apartment"),
        ("Commercial", "Commercial"),
        ("Land", "Land"),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(
        max_length=100,
        choices=PROPERTY_TYPES,
        default="Residential"
    )
    description = models.TextField()
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True)
    size_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="property_images/", null=True, blank=True)

    def __str__(self):
        return self.name
    
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
    panorama_image = models.ImageField(upload_to="virtual_tours/", null=True, blank=True)
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