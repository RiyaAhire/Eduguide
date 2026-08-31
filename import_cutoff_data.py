import os
import django
import pandas as pd
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from colleges.models import College, Course
from prediction.models import Cutoff

BASE_PATH = Path("data")

for csv_file in BASE_PATH.rglob("*.csv"):

    if "cutoff" not in str(csv_file).lower():
        continue

    print(f"Processing: {csv_file}")

    admission_year = csv_file.parts[1]

    file_name = csv_file.name.lower()

    if "cap 1" in file_name:
        cap_round = "CAP1"
    elif "cap 2" in file_name:
        cap_round = "CAP2"
    elif "cap 3" in file_name:
        cap_round = "CAP3"
    elif "cap 4" in file_name:
        cap_round = "CAP4"
    else:
        continue

    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():

        college_code = str(row["College Code"]).strip()

        college, _ = College.objects.get_or_create(
            college_code=college_code,
            defaults={
                "college_name": str(row["College Name"]).strip(),
                "status": str(row["Status"]).strip(),
            }
        )

        course_code = str(row["Course Code"]).strip()

        course, _ = Course.objects.get_or_create(
            course_code=course_code,
            defaults={
                "course_name": str(row["Course Name"]).strip(),
                "college": college,
            }
        )

        percentile = str(row["Cutoff Percentile"]).replace("%", "").strip()

        if percentile == "" or percentile.lower() == "nan":
            continue

        percentile = float(percentile)

        if percentile > 1:
            percentile = percentile / 100

        Cutoff.objects.create(
            course=course,
            cap_round=cap_round,
            admission_year=admission_year,
            seat_category=str(row["Seat Category"]).strip(),
            category_code=str(row["Category Code"]).strip(),
            stage=str(row["Stage"]).strip(),
            cutoff_merit_no=int(row["Cutoff Merit No."]),
            cutoff_percentile=percentile,
        )

print("Cutoff Import Completed")