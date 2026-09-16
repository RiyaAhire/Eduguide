from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_student_prediction_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="email_verified",
            field=models.BooleanField(default=False),
        ),
    ]
