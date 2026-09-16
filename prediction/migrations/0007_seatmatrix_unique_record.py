from django.db import migrations, models
from django.db.models import Count, Min


def remove_duplicate_seat_matrix_rows(apps, schema_editor):
    SeatMatrix = apps.get_model("prediction", "SeatMatrix")
    fields = [
        "course_id", "admission_year", "cap_round", "seat_type",
        "district_type", "category", "gender",
    ]
    duplicates = (
        SeatMatrix.objects.values(*fields)
        .annotate(keep_id=Min("id"), copies=Count("id"))
        .filter(copies__gt=1)
    )
    for record in duplicates.iterator():
        filters = {field: record[field] for field in fields}
        SeatMatrix.objects.filter(**filters).exclude(pk=record["keep_id"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("prediction", "0006_cutoff_unique_record"),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_seat_matrix_rows, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="seatmatrix",
            constraint=models.UniqueConstraint(
                fields=(
                    "course", "admission_year", "cap_round", "seat_type",
                    "district_type", "category", "gender",
                ),
                name="unique_seat_matrix_record",
            ),
        ),
    ]
