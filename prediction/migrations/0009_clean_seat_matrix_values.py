from django.db import migrations


MISSING_VALUES = {"", "nan", "n/a", "none", "null", "-"}
GENDER_VALUES = {
    "g": "Gents",
    "gent": "Gents",
    "gents": "Gents",
    "male": "Gents",
    "m": "Gents",
    "l": "Ladies",
    "lady": "Ladies",
    "ladies": "Ladies",
    "female": "Ladies",
    "f": "Ladies",
}


def clean_seat_matrix_values(apps, schema_editor):
    """Remove unusable records and replace G/L codes with full gender labels."""
    SeatMatrix = apps.get_model("prediction", "SeatMatrix")
    identity_fields = (
        "course_id", "admission_year", "cap_round", "seat_type",
        "district_type", "category",
    )

    for record in SeatMatrix.objects.all().iterator():
        required_values = (
            record.admission_year, record.seat_type, record.district_type,
            record.category, record.gender,
        )
        if any((value or "").strip().casefold() in MISSING_VALUES for value in required_values):
            record.delete()
            continue

        gender = GENDER_VALUES.get((record.gender or "").strip().casefold())
        if not gender:
            record.delete()
            continue
        if record.gender == gender:
            continue

        filters = {field: getattr(record, field) for field in identity_fields}
        if SeatMatrix.objects.filter(**filters, gender=gender).exclude(pk=record.pk).exists():
            record.delete()
        else:
            record.gender = gender
            record.save(update_fields=["gender"])


class Migration(migrations.Migration):

    dependencies = [
        ("prediction", "0008_seatmatrix_source_and_totals"),
    ]

    operations = [
        migrations.RunPython(clean_seat_matrix_values, migrations.RunPython.noop),
    ]
