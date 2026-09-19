"""Fill College.region from the versioned college-region source file."""

import csv
import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from colleges.models import College

source_file = Path(__file__).resolve().parent / "colleges_with_region.csv"
updated = 0
with source_file.open(encoding="utf-8-sig", newline="") as source:
    for row in csv.DictReader(source):
        updated += College.objects.filter(college_code=row["college_code"].strip()).exclude(region=row["region"].strip()).update(region=row["region"].strip())
print(f"College regions synchronised: {updated} records updated.")
