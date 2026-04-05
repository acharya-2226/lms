from django.db import models

from student.models import Faculty


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.CharField(
        max_length=20, unique=True, null=True, blank=True, default=None
    )
    department = models.CharField(max_length=150, null=True, blank=True, default=None)
    qualification = models.CharField(max_length=150, null=True, blank=True, default=None)
    experience_years = models.IntegerField(null=True, blank=True, default=None)
    faculties = models.ManyToManyField(
        Faculty,
        blank=True,
        related_name='teachers',
    )
    email = models.EmailField(unique=True, null=True, blank=True, default=None)
    dp = models.ImageField(upload_to='teacher_dp/', null=True, blank=True, default=None)
    address = models.TextField(null=True, blank=True, default=None)
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
