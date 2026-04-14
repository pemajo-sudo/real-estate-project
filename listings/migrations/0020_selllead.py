from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0019_agent"),
    ]

    operations = [
        migrations.CreateModel(
            name="SellLead",
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
                ("name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=30)),
                (
                    "property_type",
                    models.CharField(
                        choices=[
                            ("Residential", "Residential"),
                            ("Apartment", "Apartment"),
                            ("Commercial", "Commercial"),
                            ("Land", "Land"),
                        ],
                        max_length=100,
                    ),
                ),
                ("location", models.CharField(max_length=255)),
                ("message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
