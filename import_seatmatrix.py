
"""Clean + import seat-matrix data so the database keeps only UNIQUE records.
 
What it does, in order:
  1. (optional) Deletes the SeatMatrix rows of REPLACE_YEAR so that year is loaded fresh.
     Asks you to type YES first. Set REPLACE_YEAR = None to skip.
  2. Removes duplicate SeatMatrix rows already in the database (keeps the oldest one).
  3. Imports every CSV found under SOURCE_DIR. Duplicate rows (same key) are ignored,
     whether they repeat inside the files or already exist in the database.
  4. Rows that cannot be stored (no college/course code, bad seat count) are written to
     seatmatrix_rejected_rows.csv, never silently dropped.
 
Duplicate key = course + admission_year + cap_round + seat_type + district_type
                + category + gender
"""
 
import csv
import os
import sys
from pathlib import Path
 
import django
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()
 
from django.db import transaction
 
from colleges.models import College, Course
from prediction.models import SeatMatrix
 
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "data" / "2026-27" / "seatmatrix"
REGION_FILE = BASE_DIR / "colleges_with_region.csv"
REJECT_FILE = BASE_DIR / "seatmatrix_rejected_rows.csv"
CAP_ROUND = "INITIAL"
REPLACE_YEAR = "2026-27"   # year to wipe and reload; use None to keep existing rows
BATCH_SIZE = 900
 
 
def clean(value):
    return (value or "").strip()
 
 
def pick(row, *names):
    """First matching column, so 'college_code' and 'College Code' headers both work."""
    for name in names:
        if name in row:
            return clean(row[name])
    raise KeyError(names[0])
 
 
def remove_db_duplicates():
    """Delete duplicate rows already in the table; the oldest row of each key stays."""
    seen, dup_ids = set(), []
    rows = SeatMatrix.objects.order_by("pk").values_list(
        "pk", "course_id", "admission_year", "cap_round",
        "seat_type", "district_type", "category", "gender",
    )
    for pk, *key in rows.iterator(chunk_size=5000):
        key = tuple(key)
        if key in seen:
            dup_ids.append(pk)
        else:
            seen.add(key)
    for i in range(0, len(dup_ids), BATCH_SIZE):
        SeatMatrix.objects.filter(pk__in=dup_ids[i:i + BATCH_SIZE]).delete()
    return len(dup_ids)
 
 
if not SOURCE_DIR.exists():
    sys.exit(f"Folder not found: {SOURCE_DIR}")
csv_files = sorted(SOURCE_DIR.rglob("*.csv"))
if not csv_files:
    sys.exit(f"No CSV files found in {SOURCE_DIR}")
 
# ---- Step 1: optional wipe of one year -------------------------------------
if REPLACE_YEAR:
    old = SeatMatrix.objects.filter(admission_year=REPLACE_YEAR, cap_round=CAP_ROUND)
    print(f"{old.count()} existing rows for {REPLACE_YEAR} will be deleted and reloaded.")
    if input("Type YES to continue: ").strip() != "YES":
        sys.exit("Cancelled. Nothing was changed.")
    old.delete()
 
# ---- Step 2: remove duplicates already stored -------------------------------
removed = remove_db_duplicates()
print(f"Duplicates removed from database: {removed}")
 
# ---- Step 3: import ----------------------------------------------------------
with REGION_FILE.open(encoding="utf-8-sig", newline="") as source:
    regions = {
        clean(r["college_code"]): clean(r["region"])
        for r in csv.DictReader(source)
        if clean(r["college_code"])
    }
 
seen = {
    (code, year, seat_type, district, category, gender): count
    for code, year, seat_type, district, category, gender, count in SeatMatrix.objects.filter(
        cap_round=CAP_ROUND
    ).values_list(
        "course__course_code", "admission_year", "seat_type",
        "district_type", "category", "gender", "seat_count",
    )
}
 
college_cache = {c.college_code: c for c in College.objects.all()}
course_cache = {c.course_code: c for c in Course.objects.all()}
 
total_rows = imported = duplicates = conflicting = 0
rejected, pending = [], []
 
 
def flush():
    if pending:
        SeatMatrix.objects.bulk_create(pending, batch_size=BATCH_SIZE)
        pending.clear()
 
 
with transaction.atomic():
    for csv_file in csv_files:
        print(f"Processing: {csv_file}")
        with csv_file.open(encoding="utf-8-sig", newline="") as source:
            for line_no, row in enumerate(csv.DictReader(source), start=2):
                total_rows += 1
                try:
                    college_code = pick(row, "college_code", "College Code")
                    course_code = pick(row, "course_code", "Course Code")
                    year = pick(row, "admission_year", "Admission Year")
                    seat_type = pick(row, "seat_type", "Seat Type")
                    district = pick(row, "district_type", "District Type")
                    category = pick(row, "category", "Category")
                    gender = pick(row, "gender", "Gender")
                    seat_count = int(float(pick(row, "seat_count", "Seat Count")))
                except (KeyError, TypeError, ValueError) as exc:
                    rejected.append([str(csv_file), line_no, f"unreadable value: {exc!r}"])
                    continue
                if not college_code or not course_code:
                    rejected.append([str(csv_file), line_no, "missing college_code or course_code"])
                    continue
 
                key = (course_code, year, seat_type, district, category, gender)
                if key in seen:
                    duplicates += 1
                    if seen[key] != seat_count:
                        conflicting += 1  # same key, different count: first value is kept
                    continue
                seen[key] = seat_count
 
                college = college_cache.get(college_code)
                if college is None:
                    college = College.objects.create(
                        college_code=college_code,
                        college_name=clean(row.get("college_name")) or f"College {college_code}",
                        region=regions.get(college_code),
                        status="Unclassified",
                    )
                    college_cache[college_code] = college
                elif regions.get(college_code) and college.region != regions[college_code]:
                    college.region = regions[college_code]
                    college.save(update_fields=["region"])
 
                course = course_cache.get(course_code)
                if course is None:
                    course = Course.objects.create(
                        course_code=course_code,
                        course_name=clean(row.get("course_name")) or f"Course {course_code}",
                        college=college,
                    )
                    course_cache[course_code] = course
 
                pending.append(SeatMatrix(
                    course=course, admission_year=year, cap_round=CAP_ROUND,
                    seat_type=seat_type, district_type=district,
                    category=category, gender=gender, seat_count=seat_count,
                ))
                imported += 1
                if len(pending) >= BATCH_SIZE:
                    flush()
    flush()
 
if rejected:
    with REJECT_FILE.open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["file", "line", "reason"])
        writer.writerows(rejected)
 
print(f"Rows read:            {total_rows}")
print(f"New records stored:   {imported}")
print(f"Duplicates ignored:   {duplicates} ({conflicting} had a different seat count; first value kept)")
print(f"Rows needing review:  {len(rejected)}" + (f" -> see {REJECT_FILE.name}" if rejected else ""))
print(f"Check: {imported} + {duplicates} + {len(rejected)} = {imported + duplicates + len(rejected)} (should equal rows read)")
print(f"Total rows now in SeatMatrix: {SeatMatrix.objects.count()}")
 
