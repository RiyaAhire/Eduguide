"""Import seat-matrix CSV data without deleting existing records.

The consolidated ``data/seatmatrix_output.csv`` is preferred when present. If
it is absent, the original CSV files under ``data/**/seatmatrix/`` are used.
Rows already present in the database or repeated in the input are skipped.
Invalid input rows are written to ``seatmatrix_rejected_rows.csv``.
"""

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
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "seatmatrix_output.csv"
REGION_FILE = BASE_DIR / "colleges_with_region.csv"
REJECT_FILE = BASE_DIR / "seatmatrix_rejected_rows.csv"
BATCH_SIZE = 1000
PROGRESS_INTERVAL = 10000

CONSOLIDATED_COLUMNS = {
    "college_code", "college_name", "course_code", "course_name", "admission_year",
    "cap_seats", "ms_seats", "minority_seats", "institute_seats", "orphan_seats",
    "seat_type", "district_type", "category", "gender", "seat_count", "ews_seats",
    "pwd_seats", "def_seats",
}
OPTIONAL_TOTAL_COLUMNS = (
    "cap_seats", "ms_seats", "minority_seats", "institute_seats", "orphan_seats",
    "ews_seats", "pwd_seats", "def_seats",
)
MISSING_VALUES = frozenset({"nan", "n/a", "none", "null", "-"})
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


def clean(value):
    cleaned = str(value or "").strip()
    return "" if cleaned.casefold() in MISSING_VALUES else cleaned


def normalize_gender(value):
    """Convert source abbreviations to the labels shown throughout the site."""
    cleaned = clean(value)
    if not cleaned:
        return ""
    try:
        return GENDER_VALUES[cleaned.casefold()]
    except KeyError as exc:
        raise ValueError(f"Invalid gender: {cleaned}") from exc


def normalized_headers(row):
    """Normalize CSV headers so title case and underscore variants both work."""
    return {
        str(key).strip().lower().replace(" ", "_"): value
        for key, value in row.items()
        if key is not None
    }


def row_value(row, name, *aliases, default=""):
    values = normalized_headers(row)
    for key in (name, *aliases):
        normalized = key.strip().lower().replace(" ", "_")
        if normalized in values:
            return clean(values[normalized])
    return default


def parse_count(value, field_name="seat count", *, optional=False):
    raw = clean(value).replace(",", "")
    if not raw:
        if optional:
            return None
        raise ValueError(f"{field_name} is required")
    try:
        number = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid {field_name}: {raw}") from exc
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError(f"{field_name} must be a non-negative whole number: {raw}")
    return int(number)


def input_files():
    if OUTPUT_FILE.is_file():
        return [(OUTPUT_FILE, True)]

    legacy_files = sorted(
        path for path in DATA_DIR.rglob("*.csv")
        if any(part.lower() == "seatmatrix" for part in path.relative_to(DATA_DIR).parts[:-1])
    )
    if not legacy_files:
        raise FileNotFoundError(
            f"No seat-matrix CSV found. Expected {OUTPUT_FILE} or CSVs under {DATA_DIR}/.../seatmatrix/"
        )
    print(f"{OUTPUT_FILE.name} not found; using the existing seat-matrix CSV files.")
    return [(path, False) for path in legacy_files]


def region_lookup():
    if not REGION_FILE.is_file():
        return {}
    with REGION_FILE.open(encoding="utf-8-sig", newline="") as source:
        return {
            clean(row.get("college_code")): clean(row.get("region"))
            for row in csv.DictReader(source)
            if clean(row.get("college_code"))
        }


def natural_key(course_code, year, cap_round, seat_type, district_type, category, gender):
    return (course_code, year, cap_round, seat_type, district_type, category, gender)


def make_record(row, consolidated, colleges, courses, regions):
    college_code = row_value(row, "college_code", "College Code")
    course_code = row_value(row, "course_code", "Course Code")
    college_name = row_value(row, "college_name", "College Name")
    course_name = row_value(row, "course_name", "Course Name")
    admission_year = row_value(row, "admission_year", "Admission Year")
    cap_round = row_value(
        row, "cap_round", "CAP Round", default="MATRIX" if consolidated else "INITIAL"
    ) or ("MATRIX" if consolidated else "INITIAL")
    seat_type = row_value(row, "seat_type", "Seat Type")
    district_type = row_value(row, "district_type", "District Type")
    category = row_value(row, "category", "Category")
    gender = normalize_gender(row_value(row, "gender", "Gender"))

    required = {
        "college_code": college_code,
        "course_code": course_code,
        "admission_year": admission_year,
        "seat_type": seat_type,
        "district_type": district_type,
        "category": category,
        "gender": gender,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError("Missing required field(s): " + ", ".join(missing))

    seat_count = parse_count(row_value(row, "seat_count", "Seat Count"))
    totals = {
        field: parse_count(
            row_value(row, field, field.replace("_", " ")),
            field.replace("_", " "),
            optional=True,
        )
        for field in OPTIONAL_TOTAL_COLUMNS
    }

    college = colleges.get(college_code)
    if college is None:
        if not college_name:
            raise ValueError(f"College {college_code} is not in the database and has no college_name")
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
            raise ValueError(f"Course {course_code} is not in the database and has no course_name")
        course, _ = Course.objects.get_or_create(
            course_code=course_code,
            defaults={"course_name": course_name, "college": college},
        )
        courses[course_code] = course
    if course.college_id != college.id:
        raise ValueError(
            f"Course {course_code} belongs to college {course.college.college_code}, "
            f"not {college_code}"
        )

    return SeatMatrix(
        college_code=college_code,
        college_name=college_name or college.college_name,
        course=course,
        course_code=course_code,
        course_name=course_name or course.course_name,
        admission_year=admission_year,
        cap_round=cap_round,
        seat_type=seat_type,
        district_type=district_type,
        category=category,
        gender=gender,
        seat_count=seat_count,
        **totals,
    )


def database_keys():
    return set(
        SeatMatrix.objects.values_list(
            "course__course_code", "admission_year", "cap_round", "seat_type",
            "district_type", "category", "gender",
        )
    )


def main():
    files = input_files()
    regions = region_lookup()
    rows_seen = imported_count = duplicate_count = rejected_count = 0
    rejected_rows = []

    with transaction.atomic():
        colleges = {
            obj.college_code: obj
            for obj in College.objects.all().only("id", "college_code", "college_name", "region", "status")
        }
        courses = {
            obj.course_code: obj
            for obj in Course.objects.select_related("college").only(
                "id", "course_code", "course_name", "college_id", "college__college_code"
            )
        }
        seen_keys = database_keys()
        batch = []

        for csv_path, consolidated in files:
            try:
                display_path = csv_path.relative_to(BASE_DIR)
            except ValueError:
                display_path = csv_path
            print(f"Processing {display_path}")

            with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                headers = {
                    str(header).strip().lower().replace(" ", "_")
                    for header in (reader.fieldnames or [])
                    if header
                }
                if not reader.fieldnames:
                    raise ValueError(f"{csv_path.name} is empty or has no header row")
                if consolidated:
                    missing = sorted(CONSOLIDATED_COLUMNS - headers)
                    if missing:
                        raise ValueError(
                            f"{csv_path.name} is missing required columns: {', '.join(missing)}"
                        )

                for line_number, row in enumerate(reader, start=2):
                    rows_seen += 1
                    try:
                        normalized_gender = normalize_gender(
                            row_value(row, "gender", "Gender")
                        )
                    except ValueError:
                        # Let make_record reject the row and record the reason.
                        normalized_gender = ""
                    key_values = (
                        row_value(row, "course_code", "Course Code"),
                        row_value(row, "admission_year", "Admission Year"),
                        row_value(
                            row, "cap_round", "CAP Round",
                            default="MATRIX" if consolidated else "INITIAL",
                        ) or ("MATRIX" if consolidated else "INITIAL"),
                        row_value(row, "seat_type", "Seat Type"),
                        row_value(row, "district_type", "District Type"),
                        row_value(row, "category", "Category"),
                        normalized_gender,
                    )
                    if all(key_values) and key_values in seen_keys:
                        duplicate_count += 1
                        continue

                    try:
                        record = make_record(row, consolidated, colleges, courses, regions)
                    except (ValueError, TypeError, OverflowError) as exc:
                        rejected_count += 1
                        rejected_rows.append([str(display_path), line_number, str(exc)])
                        continue

                    key = natural_key(
                        record.course_code, record.admission_year, record.cap_round,
                        record.seat_type, record.district_type, record.category, record.gender,
                    )
                    seen_keys.add(key)
                    batch.append(record)
                    if len(batch) >= BATCH_SIZE:
                        SeatMatrix.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                        imported_count += len(batch)
                        batch.clear()

                    if rows_seen % PROGRESS_INTERVAL == 0:
                        print(
                            f"Processed {rows_seen:,} rows; imported {imported_count:,}; "
                            f"duplicates {duplicate_count:,}; invalid {rejected_count:,}."
                        )

        if batch:
            SeatMatrix.objects.bulk_create(batch, batch_size=BATCH_SIZE)
            imported_count += len(batch)

    if rejected_rows:
        with REJECT_FILE.open("w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(["file", "line", "reason"])
            writer.writerows(rejected_rows)

    print("Seat-matrix import complete.")
    print(f"Rows processed: {rows_seen:,}")
    print(f"New rows imported: {imported_count:,}")
    print(f"Duplicate rows skipped: {duplicate_count:,}")
    print(f"Invalid rows skipped: {rejected_count:,}")
    if rejected_rows:
        print(f"Rejected rows saved to: {REJECT_FILE}")
    print(f"Total rows now in SeatMatrix: {SeatMatrix.objects.count():,}")


if __name__ == "__main__":
    main()
