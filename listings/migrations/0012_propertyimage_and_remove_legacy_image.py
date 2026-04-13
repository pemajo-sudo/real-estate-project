import django.db.models.deletion
from django.db import migrations, models


def copy_legacy_images_to_propertyimage(apps, schema_editor):
    Property = apps.get_model("listings", "Property")
    PropertyImage = apps.get_model("listings", "PropertyImage")
    for prop in Property.objects.all():
        if prop.image:
            PropertyImage.objects.create(property=prop, image=prop.image, sort_order=0)


def restore_legacy_image_from_propertyimage(apps, schema_editor):
    Property = apps.get_model("listings", "Property")
    PropertyImage = apps.get_model("listings", "PropertyImage")
    seen_property_ids = set()
    for img in PropertyImage.objects.order_by("sort_order", "id"):
        if img.property_id in seen_property_ids:
            continue
        prop = Property.objects.get(pk=img.property_id)
        prop.image = img.image
        prop.save(update_fields=["image"])
        seen_property_ids.add(img.property_id)


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0011_visit"),
    ]

    operations = [
        migrations.CreateModel(
            name="PropertyImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="property_images/")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="listings.property",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.RunPython(copy_legacy_images_to_propertyimage, restore_legacy_image_from_propertyimage),
        migrations.RemoveField(
            model_name="property",
            name="image",
        ),
    ]
