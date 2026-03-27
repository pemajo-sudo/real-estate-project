from django.db import models


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
    image = models.ImageField(upload_to="property_images/", null=True, blank=True)

    def __str__(self):
        return self.name