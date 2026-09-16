# Generated manually to add the account-linked prediction profile.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0002_courseinfo"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="admission_year",
            field=models.CharField(default="2026-27", max_length=10),
        ),
        migrations.AddField(
            model_name="student",
            name="college_type",
            field=models.CharField(default="Any", max_length=50),
        ),
        migrations.AddField(
            model_name="student",
            name="preferred_location",
            field=models.CharField(default="Any", max_length=100),
        ),
        migrations.AddField(
            model_name="student",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
