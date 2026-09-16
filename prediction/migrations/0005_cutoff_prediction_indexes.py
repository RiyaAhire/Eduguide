from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prediction", "0004_cutoff_admission_year_seatmatrix_admission_year_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="cutoff",
            index=models.Index(
                fields=["admission_year", "category_code"],
                name="cutoff_year_category_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="cutoff",
            index=models.Index(
                fields=["course", "admission_year"],
                name="cutoff_course_year_idx",
            ),
        ),
    ]
