from django.db import models


class College(models.Model):
    college_code = models.CharField(max_length=20, unique=True)
    college_name = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=255)

    def __str__(self):
        return self.college_name


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=255)

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    def __str__(self):
        return self.course_name