from django.db import models


class FacultyManager(models.Manager):
    def get_or_create_case_insensitive(self, name):
        """Get or create Faculty by case-insensitive name match."""
        cleaned = (name or '').strip()
        if not cleaned:
            raise ValueError('Faculty name cannot be empty.')

        existing = self.filter(name__iexact=cleaned).first()
        if existing:
            return existing, False
        return self.create(name=cleaned), True


# Create your models here.
class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)
    objects = FacultyManager()

    def __str__(self):
        return self.name


class EnrollmentYear(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return str(self.year)


class Subject(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True, null=True, blank=True, default=None)

    def __str__(self):
        return self.name


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
    