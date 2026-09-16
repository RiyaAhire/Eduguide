from django.db import migrations, models
from django.db.models import Count, Min


def remove_duplicate_cutoffs(apps, schema_editor):
    """Keep one copy of records created by earlier repeatable imports."""
    Cutoff = apps.get_model("prediction", "Cutoff")
    fields = [
        "course_id", "cap_round", "admission_year", "seat_category",
        "category_code", "stage", "cutoff_merit_no",
    ]
    duplicates = (
        Cutoff.objects.values(*fields)
        .annotate(keep_id=Min("id"), copies=Count("id"))
        .filter(copies__gt=1)
    )
    for record in duplicates.iterator():
        filters = {field: record[field] for field in fields}
        Cutoff.objects.filter(**filters).exclude(pk=record["keep_id"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("prediction", "0005_cutoff_prediction_indexes"),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_cutoffs, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="cutoff",
            constraint=models.UniqueConstraint(
                fields=(
                    "course", "cap_round", "admission_year", "seat_category",
                    "category_code", "stage", "cutoff_merit_no",
                ),
                name="unique_cutoff_record",
            ),
        ),
    ]
