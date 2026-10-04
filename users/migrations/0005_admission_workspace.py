from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("colleges", "0003_collegewebsite"),
        ("users", "0004_student_email_verified"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdmissionNotice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=220)),
                ("summary", models.TextField()),
                ("academic_year", models.CharField(blank=True, max_length=10)),
                ("published_on", models.DateField()),
                ("source_url", models.URLField(max_length=500)),
                ("is_published", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-published_on", "-id"]},
        ),
        migrations.CreateModel(
            name="ChecklistTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=50)),
                ("title", models.CharField(max_length=180)),
                ("description", models.CharField(max_length=400)),
                ("completed", models.BooleanField(default=False)),
                ("position", models.PositiveSmallIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="admission_checklist", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["position", "id"]},
        ),
        migrations.CreateModel(
            name="FavoriteCollege",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("saved_at", models.DateTimeField(auto_now_add=True)),
                ("college", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saved_by_users", to="colleges.college")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorite_colleges", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-saved_at"]},
        ),
        migrations.CreateModel(
            name="PersonalReminder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("note", models.CharField(blank=True, max_length=500)),
                ("due_date", models.DateField()),
                ("completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="personal_reminders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["completed", "due_date", "id"]},
        ),
        migrations.AddConstraint(
            model_name="checklisttask",
            constraint=models.UniqueConstraint(fields=("user", "key"), name="unique_user_checklist_task"),
        ),
        migrations.AddConstraint(
            model_name="favoritecollege",
            constraint=models.UniqueConstraint(fields=("user", "college"), name="unique_user_favorite_college"),
        ),
    ]
