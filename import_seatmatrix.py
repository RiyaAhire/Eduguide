"""Import seat-matrix CSV files while preserving known college/course details."""

import csv
import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from colleges.models import College, Course
from prediction.models import SeatMatrix

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data"
REGION_FILE = BASE_DIR / "colleges_with_region.csv"


def clean(value):
    return (value or "").strip()


with REGION_FILE.open(encoding="utf-8-sig", newline="") as source:
    regions = {clean(row["college_code"]): clean(row["region"]) for row in csv.DictReader(source) if clean(row["college_code"])}

imported = skipped = 0
for csv_file in DATA_PATH.rglob("*.csv"):
    if "seatmatrix" not in csv_file.parts:
        continue
    print(f"Processing: {csv_file}")
    with csv_file.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            try:
                college_code = clean(row["College Code"])
                course_code = clean(row["Course Code"])
                seat_count = int(float(clean(row["Seat Count"])))
                if not college_code or not course_code:
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                skipped += 1
                continue
            college, _ = College.objects.get_or_create(
                college_code=college_code,
                defaults={"college_name": f"College {college_code}", "region": regions.get(college_code), "status": "Unclassified"},
            )
            if regions.get(college_code) and college.region != regions[college_code]:
                college.region = regions[college_code]
                college.save(update_fields=["region"])
            course, _ = Course.objects.get_or_create(
                course_code=course_code,
                defaults={"course_name": f"Course {course_code}", "college": college},
            )
            SeatMatrix.objects.update_or_create(
                course=course, admission_year=clean(row["Admission Year"]), cap_round="INITIAL",
                seat_type=clean(row["Seat Type"]), district_type=clean(row["District Type"]),
                category=clean(row["Category"]), gender=clean(row["Gender"]), defaults={"seat_count": seat_count},
            )
            imported += 1
print(f"Seat-matrix import complete: {imported} records imported, {skipped} rows skipped.")
