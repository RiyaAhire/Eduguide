from django.db import models
from django.contrib.auth.models import User
from colleges.models import College

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


class FavoriteCollege(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_colleges")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="saved_by_users")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-saved_at"]
        constraints = [models.UniqueConstraint(fields=["user", "college"], name="unique_user_favorite_college")]

    def __str__(self):
        return f"{self.user.username} — {self.college.college_name}"


class ChecklistTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admission_checklist")
    key = models.CharField(max_length=50)
    title = models.CharField(max_length=180)
    description = models.CharField(max_length=400)
    completed = models.BooleanField(default=False)
    position = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        constraints = [models.UniqueConstraint(fields=["user", "key"], name="unique_user_checklist_task")]

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class PersonalReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_reminders")
    title = models.CharField(max_length=160)
    note = models.CharField(max_length=500, blank=True)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["completed", "due_date", "id"]

    def __str__(self):
        return f"{self.title} — {self.due_date}"


class AdmissionNotice(models.Model):
    title = models.CharField(max_length=220)
    summary = models.TextField()
    academic_year = models.CharField(max_length=10, blank=True)
    published_on = models.DateField()
    source_url = models.URLField(max_length=500)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_on", "-id"]

    def __str__(self):
        return self.title
