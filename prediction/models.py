from django.db import models
from colleges.models import Course


class Cutoff(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    cap_round = models.CharField(max_length=10)
    admission_year = models.CharField(max_length=10)
    seat_category = models.CharField(max_length=255)

    category_code = models.CharField(max_length=50)

    stage = models.CharField(max_length=20)

    cutoff_merit_no = models.IntegerField()

    cutoff_percentile = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=["admission_year", "category_code"], name="cutoff_year_category_idx"),
            models.Index(fields=["course", "admission_year"], name="cutoff_course_year_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "course", "cap_round", "admission_year", "seat_category",
                    "category_code", "stage", "cutoff_merit_no",
                ],
                name="unique_cutoff_record",
            ),
        ]

    def __str__(self):
        return f"{self.course.course_name} - {self.category_code}"


class SeatMatrix(models.Model):

    # Keep the source identifiers alongside the existing course relation so
    # the matrix remains easy to filter and the legacy relation stays intact.
    college_code = models.CharField(max_length=20, blank=True, default="", db_index=True)
    college_name = models.CharField(max_length=255, blank=True, default="")
    course_code = models.CharField(max_length=20, blank=True, default="", db_index=True)
    course_name = models.CharField(max_length=255, blank=True, default="")

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    admission_year = models.CharField(max_length=10)

    cap_round = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=50)

    seat_count = models.IntegerField()
    cap_seats = models.PositiveIntegerField(blank=True, null=True)
    ms_seats = models.PositiveIntegerField(blank=True, null=True)
    minority_seats = models.PositiveIntegerField(blank=True, null=True)
    institute_seats = models.PositiveIntegerField(blank=True, null=True)
    orphan_seats = models.PositiveIntegerField(blank=True, null=True)
    ews_seats = models.PositiveIntegerField(blank=True, null=True)
    pwd_seats = models.PositiveIntegerField(blank=True, null=True)
    def_seats = models.PositiveIntegerField(blank=True, null=True)

    category = models.CharField(max_length=20, db_index=True)

    gender = models.CharField(max_length=10, db_index=True)

    district_type = models.CharField(max_length=20, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "course", "admission_year", "cap_round", "seat_type",
                    "district_type", "category", "gender",
                ],
                name="unique_seat_matrix_record",
            ),
        ]

    def __str__(self):
        return f"{self.course.course_name} - {self.category}"
