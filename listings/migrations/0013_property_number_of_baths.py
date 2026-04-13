from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0012_propertyimage_and_remove_legacy_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="number_of_baths",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
