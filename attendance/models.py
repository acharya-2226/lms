from django.db import models
from django.db.models import Q

from student.models import EnrollmentYear, Faculty, Subject
from teacher.models import Teacher


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


class TimeSlot(models.Model):
    label = models.CharField(max_length=100, blank=True, default='')
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'start_time', 'id']
        constraints = [
            models.UniqueConstraint(fields=['start_time', 'end_time'], name='unique_timeslot_time_range'),
        ]

    def __str__(self):
        if self.label:
            return f'{self.label} ({self.start_time.strftime("%H:%M")} - {self.end_time.strftime("%H:%M")})'
        return f'{self.start_time.strftime("%H:%M")} - {self.end_time.strftime("%H:%M")}'

    @property
    def display_label(self):
        time_range = f'{self.start_time.strftime("%I:%M %p").lstrip("0")} - {self.end_time.strftime("%I:%M %p").lstrip("0")}'
        return f'{self.label} ({time_range})' if self.label else time_range


class WeeklyClassSchedule(models.Model):
    title = models.CharField(max_length=200, blank=True, default='')
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='weekly_schedules',
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='weekly_schedules',
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='weekly_schedules',
    )
    enrollment_batch = models.ForeignKey(
        EnrollmentYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='weekly_schedules',
    )
    day_of_week = models.CharField(max_length=15, choices=DAY_CHOICES)
    timeslot = models.ForeignKey(
        TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='weekly_schedules',
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, default=None)
    note = models.TextField(null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['faculty__name', 'enrollment_batch__year', 'day_of_week', 'timeslot__display_order', 'timeslot__start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['subject', 'faculty', 'enrollment_batch', 'day_of_week', 'timeslot'],
                condition=Q(
                    subject__isnull=False,
                    faculty__isnull=False,
                    enrollment_batch__isnull=False,
                    timeslot__isnull=False,
                ),
                name='unique_weekly_schedule_subject_faculty_year_day_slot',
            ),
        ]

    def __str__(self):
        parts = [
            self.subject.name if self.subject else 'Class',
            self.faculty.name if self.faculty else 'No Faculty',
            str(self.enrollment_batch.year) if self.enrollment_batch else 'No Year',
            self.get_day_of_week_display(),
            self.timeslot.display_label if self.timeslot else 'No Timeslot',
        ]
        return ' | '.join(parts)

    def save(self, *args, **kwargs):
        if self.subject:
            self.title = f'{self.subject.name} weekly schedule'
        elif not self.title:
            self.title = 'Weekly class schedule'
        super().save(*args, **kwargs)


class Attendance(models.Model):
    DAY_CHOICES = DAY_CHOICES

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
    timeslot = models.ForeignKey(
        TimeSlot,
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
        if self.timeslot:
            self.start_time = self.timeslot.start_time
            self.end_time = self.timeslot.end_time
        if self.subject and self.attendance_date:
            self.title = f'{self.subject.name} : {self.attendance_date}'
        elif self.attendance_date:
            self.title = f'Attendance : {self.attendance_date}'
        super().save(*args, **kwargs)

    @property
    def slot_display(self):
        if self.timeslot:
            return self.timeslot.display_label
        if self.start_time and self.end_time:
            return f'{self.start_time.strftime("%I:%M %p").lstrip("0")} - {self.end_time.strftime("%I:%M %p").lstrip("0")}'
        return '-'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subject', 'faculty', 'enrollment_batch', 'attendance_date', 'timeslot'],
                condition=Q(
                    subject__isnull=False,
                    faculty__isnull=False,
                    enrollment_batch__isnull=False,
                    timeslot__isnull=False,
                ),
                name='unique_attendance_subject_faculty_year_date_slot',
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
