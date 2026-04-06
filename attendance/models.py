from django.db import models
from django.db.models import Q

from student.models import EnrollmentYear, Faculty, Subject
from teacher.models import Teacher


class Attendance(models.Model):
    DAY_MONDAY = 'monday'
    DAY_TUESDAY = 'tuesday'
    DAY_WEDNESDAY = 'wednesday'
    DAY_THURSDAY = 'thursday'
    DAY_FRIDAY = 'friday'
    DAY_SATURDAY = 'saturday'
    DAY_SUNDAY = 'sunday'

    DAY_CHOICES = [
        (DAY_MONDAY, 'Monday'),
        (DAY_TUESDAY, 'Tuesday'),
        (DAY_WEDNESDAY, 'Wednesday'),
        (DAY_THURSDAY, 'Thursday'),
        (DAY_FRIDAY, 'Friday'),
        (DAY_SATURDAY, 'Saturday'),
        (DAY_SUNDAY, 'Sunday'),
    ]

    title = models.CharField(max_length=200)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='attendances',
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='attendances',
    )
    enrollment_batch = models.ForeignKey(
        EnrollmentYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='attendances',
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='attendances',
    )
    day_of_week = models.CharField(max_length=15, choices=DAY_CHOICES, blank=True, default='')
    start_time = models.TimeField(null=True, blank=True, default=None)
    end_time = models.TimeField(null=True, blank=True, default=None)
    attendance_date = models.DateField()
    note = models.TextField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.attendance_date:
            self.day_of_week = self.attendance_date.strftime('%A').lower()
        if self.subject and self.attendance_date:
            self.title = f'{self.subject.name} : {self.attendance_date}'
        elif self.attendance_date:
            self.title = f'Attendance : {self.attendance_date}'
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subject', 'faculty', 'enrollment_batch', 'attendance_date'],
                condition=Q(subject__isnull=False, faculty__isnull=False, enrollment_batch__isnull=False),
                name='unique_attendance_subject_faculty_year_date',
            ),
        ]


class AttendanceEntry(models.Model):
    STATUS_UNMARKED = 'unmarked'
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'

    STATUS_CHOICES = [
        (STATUS_UNMARKED, 'Unmarked'),
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
    ]

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name='entries',
    )
    student = models.ForeignKey(
        'student.Student',
        on_delete=models.CASCADE,
        related_name='attendance_entries',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNMARKED)
    marked_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        unique_together = ('attendance', 'student')

    def __str__(self):
        return f'{self.attendance} - {self.student}'
