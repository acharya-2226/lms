from datetime import date

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from assignment.models import Assignment, AssignmentRecipient
from student.models import EnrollmentYear, Faculty, Student, Subject


class AssignmentUploadSafetyTests(TestCase):
    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'
        self.user = User.objects.create_user('student1', password='Student123!')
        self.faculty = Faculty.objects.create(name='Science')
        self.year = EnrollmentYear.objects.create(year=2026)
        self.subject = Subject.objects.create(name='Biology', faculty=self.faculty)
        self.student = Student.objects.create(
            user=self.user,
            name='Student One',
            faculty=self.faculty,
            enrollment_batch=self.year,
            is_first_login=False,
        )
        self.assignment = Assignment.objects.create(
            title='Lab Report',
            subject=self.subject,
            faculty=self.faculty,
            enrollment_batch=self.year,
            due_date=date(2026, 1, 15),
        )
        self.recipient = AssignmentRecipient.objects.create(
            assignment=self.assignment,
            student=self.student,
        )

    def test_submission_rejects_unsupported_type(self):
        self.client.login(username='student1', password='Student123!')

        bad_file = SimpleUploadedFile(
            'payload.exe',
            b'not-allowed',
            content_type='application/x-msdownload',
        )
        response = self.client.post(
            reverse('assignment:assignment-submit', kwargs={'pk': self.assignment.pk}),
            {'submission_file': bad_file},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.recipient.refresh_from_db()
        self.assertFalse(self.recipient.is_submitted)
        messages = list(response.context['messages'])
        self.assertTrue(any('Unsupported file type' in str(message) for message in messages))
