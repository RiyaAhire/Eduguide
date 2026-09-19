"""Import cutoff CSV files without losing the authoritative college region."""

import csv
import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from colleges.models import College, Course
from prediction.models import Cutoff

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data"
REGION_FILE = BASE_DIR / "colleges_with_region.csv"


def clean(value):
    return (value or "").strip()


def load_regions():
    with REGION_FILE.open(encoding="utf-8-sig", newline="") as source:
        return {clean(row["college_code"]): clean(row["region"]) for row in csv.DictReader(source) if clean(row["college_code"])}


def cap_round_for(filename):
    for number in range(1, 5):
        if f"cap {number}" in filename.lower():
            return f"CAP{number}"
    return None


regions = load_regions()
imported = skipped = 0
for csv_file in DATA_PATH.rglob("*.csv"):
    if "cutoff" not in csv_file.parts:
        continue
    cap_round = cap_round_for(csv_file.name)
    if not cap_round:
        continue
    admission_year = csv_file.parents[1].name
    print(f"Processing: {csv_file}")
    with csv_file.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            try:
                college_code = clean(row["College Code"])
                course_code = clean(row["Course Code"])
                percentile = float(clean(row["Cutoff Percentile"]).replace("%", ""))
                merit_no = int(float(clean(row["Cutoff Merit No."])))
                if not college_code or not course_code:
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                skipped += 1
                continue
            if percentile > 1:
                percentile /= 100
            college, _ = College.objects.update_or_create(
                college_code=college_code,
                defaults={"college_name": clean(row["College Name"]), "status": clean(row["Status"])},
            )
            if regions.get(college_code) and college.region != regions[college_code]:
                college.region = regions[college_code]
                college.save(update_fields=["region"])
            course, _ = Course.objects.update_or_create(
                course_code=course_code,
                defaults={"course_name": clean(row["Course Name"]), "college": college},
            )
            Cutoff.objects.update_or_create(
                course=course, cap_round=cap_round, admission_year=admission_year,
                seat_category=clean(row["Seat Category"]), category_code=clean(row["Category Code"]),
                stage=clean(row["Stage"]), cutoff_merit_no=merit_no,
                defaults={"cutoff_percentile": percentile},
            )
            imported += 1
print(f"Cutoff import complete: {imported} records imported, {skipped} rows skipped.")
