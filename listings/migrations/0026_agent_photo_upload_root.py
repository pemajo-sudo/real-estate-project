from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0025_update_upload_paths_to_root"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agent",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
