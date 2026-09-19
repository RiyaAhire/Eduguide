"""Report or remove duplicate cutoff and seat-matrix records safely.

Run without arguments first. Add --apply only after reviewing the report.
The oldest record is retained, matching the project's database migrations.
"""

import argparse
import os

import django
from django.db import transaction
from django.db.models import Count, Min

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from prediction.models import Cutoff, SeatMatrix


def duplicate_groups(model, fields):
    return list(
        model.objects.values(*fields)
        .annotate(keep_id=Min("id"), copies=Count("id"))
        .filter(copies__gt=1)
    )


def clean(model, fields, label, apply_changes):
    groups = duplicate_groups(model, fields)
    extra_rows = sum(group["copies"] - 1 for group in groups)
    print(f"{label}: {len(groups)} duplicate groups, {extra_rows} duplicate rows.")
    if not apply_changes or not groups:
        return 0

    removed = 0
    for group in groups:
        filters = {field: group[field] for field in fields}
        deleted, _ = model.objects.filter(**filters).exclude(pk=group["keep_id"]).delete()
        removed += deleted
    print(f"{label}: removed {removed} duplicate rows; oldest row in each group was kept.")
    return removed


parser = argparse.ArgumentParser(description="Safely clean duplicate admission records.")
parser.add_argument("--apply", action="store_true", help="Delete duplicates after reporting them.")
args = parser.parse_args()

cutoff_fields = [
    "course_id", "cap_round", "admission_year", "seat_category",
    "category_code", "stage", "cutoff_merit_no",
]
seat_matrix_fields = [
    "course_id", "admission_year", "cap_round", "seat_type",
    "district_type", "category", "gender",
]

with transaction.atomic():
    removed = clean(Cutoff, cutoff_fields, "Cutoffs", args.apply)
    removed += clean(SeatMatrix, seat_matrix_fields, "Seat matrices", args.apply)
    if not args.apply:
        transaction.set_rollback(True)

if args.apply:
    print(f"Cleanup complete: {removed} rows removed.")
else:
    print("Dry run only: no records were changed. Re-run with --apply to remove the reported duplicates.")
