import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduguide.settings")
django.setup()

from colleges.models import College, CollegeWebsite


csv_file = "College_Websitesss.csv"

with open(csv_file, mode="r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        institute_code = row["Institute Code"].strip()
        website = row["Website"].strip()

        if not website:
            continue

        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        try:
            college = College.objects.get(
                college_code=institute_code
            )

            CollegeWebsite.objects.update_or_create(
                college=college,
                defaults={"website": website}
            )

        except College.DoesNotExist:
            print(
                f"College code {institute_code} not found: "
                f"{row['Institute Name']}"
            )

print("College website import completed.")