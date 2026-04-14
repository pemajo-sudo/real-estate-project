from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0024_property_listing_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="walkthrough_video",
            field=models.FileField(blank=True, null=True, upload_to=""),
        ),
        migrations.AlterField(
            model_name="propertyimage",
            name="image",
            field=models.ImageField(upload_to=""),
        ),
        migrations.AlterField(
            model_name="virtualtourscene",
            name="panorama_image",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
