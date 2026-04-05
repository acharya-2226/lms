from django.db import models

from student.models import EnrollmentYear, Faculty
from student.models import Subject
from teacher.models import Teacher


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True, default=None)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='assignments',
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='assignments',
    )
    enrollment_batch = models.ForeignKey(
        EnrollmentYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='assignments',
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='assignments',
    )
    attachment = models.FileField(upload_to='assignment_files/', null=True, blank=True, default=None)
    due_date = models.DateField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AssignmentRecipient(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='recipients',
    )
    student = models.ForeignKey(
        'student.Student',
        on_delete=models.CASCADE,
        related_name='assignment_recipients',
    )
    is_notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True, default=None)
    is_seen = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True, default=None)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True, default=None)
    submission_file = models.FileField(
        upload_to='assignment_submissions/',
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f'{self.assignment} - {self.student}'
