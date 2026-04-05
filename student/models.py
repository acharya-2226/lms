from django.db import models


# Create your models here.
class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class EnrollmentYear(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return str(self.year)


class Student(models.Model):

    name = models.CharField(max_length=100)
    roll_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True, default=None
    )
    enrollment_batch = models.ForeignKey(
        EnrollmentYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='students',
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='students',
    )
    age = models.IntegerField(null=True, blank=True, default=None)
    email = models.EmailField(unique=True, null=True, blank=True, default=None)
    dp = models.ImageField(upload_to='student_dp/', null=True, blank=True, default=None)
    address = models.TextField(null=True, blank=True, default=None)
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    