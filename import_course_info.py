import os
import csv
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from users.models import CourseInfo

files = [
    "data/diploma_courses_AGS.csv",
    "data/diploma_courses_AGS_batch2.csv"
]

for file_path in files:

    print(f"Processing: {file_path}")

    with open(file_path, mode="r", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for row in reader:

            CourseInfo.objects.update_or_create(

                course_name=row["course_name"],

                defaults={
                    "field": row["field"],
                    "description": row["description"],
                    "major_subjects": row["major_subjects"],
                    "skills": row["skills"],
                    "career_opportunities": row["career_opportunities"],
                    "higher_studies": row["higher_studies"],
                    "duration": row["duration"],
                    "level": row["level"],
                    "mode": row["mode"],
                }
            )

print("Import Completed Successfully")