from django.db import models
from django.contrib.auth.models import User

from student.models import Faculty


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='teacher_profile',
    )
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
    is_first_login = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='teacher_name_idx'),
            models.Index(fields=['department'], name='teacher_dept_idx'),
        ]
