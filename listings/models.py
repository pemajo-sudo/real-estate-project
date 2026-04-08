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