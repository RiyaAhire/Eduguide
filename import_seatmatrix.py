"""Import the consolidated seat matrix, with a legacy CSV fallback."""

import csv
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from django.db import transaction  # noqa: E402
from colleges.models import College, Course  # noqa: E402
from prediction.models import SeatMatrix  # noqa: E402


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "data" / "seatmatrix_output.csv"
REGION_FILE = BASE_DIR / "colleges_with_region.csv"
CONSOLIDATED_COLUMNS = {
    "college_code", "college_name", "course_code", "course_name", "admission_year",
    "cap_seats", "ms_seats", "minority_seats", "institute_seats", "orphan_seats",
    "seat_type", "district_type", "category", "gender", "seat_count", "ews_seats",
    "pwd_seats", "def_seats",
}
COUNT_COLUMNS = (
    "seat_count", "cap_seats", "ms_seats", "minority_seats", "institute_seats",
    "orphan_seats", "ews_seats", "pwd_seats", "def_seats",
)
BATCH_SIZE = 1000
PROGRESS_INTERVAL = 10000


def clean(value):
    return (value or "").strip()


def parse_count(value):
    value = clean(value).replace(",", "")
    if not value:
        return 0
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid seat count: {value}") from exc
    if number < 0 or number != number.to_integral_value():
        raise ValueError(f"Seat counts must be non-negative whole numbers: {value}")
    return int(number)


def row_value(row, name, *legacy_names, default=""):
    normalized = {str(key).strip().lower().replace(" ", "_"): value for key, value in row.items() if key}
    for key in (name, *legacy_names):
        if key in normalized:
            return clean(normalized[key])
    return default


def record_key(row, consolidated):
    """Return the same natural key enforced by SeatMatrix's unique constraint."""
    return (
        row_value(row, "course_code", "Course Code"),
        row_value(row, "admission_year", "Admission Year"),
        row_value(
            row,
            "cap_round",
            "CAP Round",
            default="MATRIX" if consolidated else "INITIAL",
        ) or ("MATRIX" if consolidated else "INITIAL"),
        row_value(row, "seat_type", "Seat Type"),
        row_value(row, "district_type", "District Type"),
        row_value(row, "category", "Category"),
        row_value(row, "gender", "Gender"),
    )


def input_files():
    if OUTPUT_FILE.exists():
        return [(OUTPUT_FILE, True)]
    legacy_files = sorted(
        path for path in (BASE_DIR / "data").rglob("*.csv")
        if "seatmatrix" in {part.lower() for part in path.parts}
    )
    if not legacy_files:
        raise FileNotFoundError(f"Seat-matrix CSV not found: {OUTPUT_FILE}")
    print(f"{OUTPUT_FILE.name} is not present; importing the existing seat-matrix CSV files instead.")
    return [(path, False) for path in legacy_files]


def region_lookup():
    if not REGION_FILE.exists():
        return {}
    with REGION_FILE.open(encoding="utf-8-sig", newline="") as source:
        return {
            clean(row.get("college_code")): clean(row.get("region"))
            for row in csv.DictReader(source)
            if clean(row.get("college_code"))
        }


def make_record(row, consolidated, colleges, courses, regions):
    college_code = row_value(row, "college_code", "College Code")
    course_code = row_value(row, "course_code", "Course Code")
    college_name = row_value(row, "college_name", "College Name")
    course_name = row_value(row, "course_name", "Course Name")
    admission_year = row_value(row, "admission_year", "Admission Year")
    if not college_code or not course_code or not admission_year:
        raise ValueError("college_code, course_code and admission_year are required")

    college = colleges.get(college_code)
    if college is None:
        if not college_name:
            raise ValueError(f"No existing college or college_name for college code {college_code}")
        college, _ = College.objects.get_or_create(
            college_code=college_code,
            defaults={
                "college_name": college_name,
                "region": regions.get(college_code, ""),
                "status": "",
            },
        )
        colleges[college_code] = college

    course = courses.get(course_code)
    if course is None:
        if not course_name:
            raise ValueError(f"No existing course or course_name for course code {course_code}")
        course, _ = Course.objects.get_or_create(
            course_code=course_code,
            defaults={
                "course_name": course_name,
                "college": college,
            },
        )
        courses[course_code] = course

    counts = {"seat_count": parse_count(row_value(row, "seat_count", "Seat Count"))}
    # Old source CSVs contain only per-record seat_count; the consolidated file
    # carries the additional seat totals as separate columns. Unknown totals
    # stay NULL rather than being presented as confirmed zero-seat counts.
    for field in COUNT_COLUMNS[1:]:
        raw_count = row_value(row, field, field.replace("_", " "))
        counts[field] = parse_count(raw_count) if raw_count else None

    return SeatMatrix(
        college_code=college_code,
        college_name=college_name or college.college_name,
        course=course,
        course_code=course_code,
        course_name=course_name or course.course_name,
        admission_year=admission_year,
        cap_round=row_value(row, "cap_round", "CAP Round", default="MATRIX" if consolidated else "INITIAL") or ("MATRIX" if consolidated else "INITIAL"),
        seat_type=row_value(row, "seat_type", "Seat Type"),
        district_type=row_value(row, "district_type", "District Type"),
        category=row_value(row, "category", "Category"),
        gender=row_value(row, "gender", "Gender"),
        **counts,
    )


def main():
    files = input_files()
    regions = region_lookup()
    imported_count = 0
    skipped_count = 0
    source_duplicate_count = 0
    attempted_count = 0

    with transaction.atomic():
        before_count = SeatMatrix.objects.count()
        colleges = {obj.college_code: obj for obj in College.objects.all().only("id", "college_code", "college_name", "region", "status")}
        courses = {obj.course_code: obj for obj in Course.objects.select_related("college").only("id", "course_code", "course_name", "college_id")}
        batch = []
        rows_seen = 0
        seen_keys = set()

        for csv_path, consolidated in files:
            print(f"Processing {csv_path.relative_to(BASE_DIR)}")
            with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                headers = {str(header).strip().lower() for header in (reader.fieldnames or [])}
                if consolidated:
                    missing = sorted(CONSOLIDATED_COLUMNS - headers)
                    if missing:
                        raise ValueError(f"{csv_path.name} is missing required columns: {', '.join(missing)}")
                for row in reader:
                    rows_seen += 1
                    key = record_key(row, consolidated)
                    if all(key) and key in seen_keys:
                        source_duplicate_count += 1
                        continue
                    if all(key):
                        seen_keys.add(key)
                    try:
                        batch.append(make_record(row, consolidated, colleges, courses, regions))
                    except (ValueError, TypeError, OverflowError) as exc:
                        skipped_count += 1
                        print(f"Skipping row {rows_seen} in {csv_path.name}: {exc}")
                    if len(batch) >= BATCH_SIZE:
                        attempted_count += len(batch)
                        SeatMatrix.objects.bulk_create(batch, batch_size=BATCH_SIZE, ignore_conflicts=True)
                        batch.clear()
                    if rows_seen % PROGRESS_INTERVAL == 0:
                        print(f"Processed {rows_seen:,} rows; {skipped_count:,} invalid rows skipped.")

        if batch:
            attempted_count += len(batch)
            SeatMatrix.objects.bulk_create(batch, batch_size=BATCH_SIZE, ignore_conflicts=True)

        imported_count = SeatMatrix.objects.count() - before_count

    duplicate_count = source_duplicate_count + max(attempted_count - imported_count, 0)
    print("Seat-matrix import complete.")
    print(f"Rows processed: {rows_seen:,}")
    print(f"New rows imported: {imported_count:,}")
    print(f"Duplicate rows skipped: {duplicate_count:,}")
    print(f"Invalid rows skipped: {skipped_count:,}")


if __name__ == "__main__":
    main()
