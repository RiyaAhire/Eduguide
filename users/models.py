from django.db import models

from django.db import models

class Student(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    percentage = models.FloatField()
    category = models.CharField(max_length=20)
    branch = models.CharField(max_length=100)
    passing_year = models.IntegerField()

    def __str__(self):
        return self.full_name