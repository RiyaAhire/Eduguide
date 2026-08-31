import os
import django
import pandas as pd
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from colleges.models import College, Course
from prediction.models import SeatMatrix

BASE_PATH = Path("data")

for csv_file in BASE_PATH.rglob("*.csv"):

    if "seatmatrix" not in str(csv_file).lower() and "seat_matrix" not in str(csv_file).lower():
        continue

    print(f"\nProcessing: {csv_file}")

    admission_year = csv_file.parts[1]

    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():

        college_code = str(row["College Code"]).strip()

        course_code = str(row["Course Code"]).strip()

        # scientific notation fix
        try:
            course_code = str(int(float(course_code)))
        except:
            pass

        college, _ = College.objects.get_or_create(
            college_code=college_code,
            defaults={
                "college_name": f"College {college_code}",
                "status": "Active"
            }
        )

        course, _ = Course.objects.get_or_create(
            course_code=course_code,
            defaults={
                "course_name": f"Course {course_code}",
                "college": college
            }
        )

        SeatMatrix.objects.create(
            course=course,
            admission_year=str(row["Admission Year"]).strip(),
            cap_round="INITIAL",
            seat_type=str(row["Seat Type"]).strip(),
            district_type=str(row["District Type"]).strip(),
            category=str(row["Category"]).strip(),
            gender=str(row["Gender"]).strip(),
            seat_count=int(row["Seat Count"])
        )

print("\nSeat Matrix Import Completed")