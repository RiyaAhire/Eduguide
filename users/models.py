from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    percentage = models.FloatField()
    category = models.CharField(max_length=20)
    branch = models.CharField(max_length=100)
    passing_year = models.IntegerField()
    preferred_location = models.CharField(max_length=100, default="Any")
    college_type = models.CharField(max_length=50, default="Any")
    admission_year = models.CharField(max_length=10, default="2026-27")
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

class CourseInfo(models.Model):
    course_name = models.CharField(max_length=255, unique=True)
    field = models.CharField(max_length=100)

    description = models.TextField()

    major_subjects = models.TextField()
    skills = models.TextField()
    career_opportunities = models.TextField()
    higher_studies = models.TextField()
   

    duration = models.CharField(max_length=50)
    level = models.CharField(max_length=50)
    mode = models.CharField(max_length=50)

    def __str__(self):
        return self.course_name
