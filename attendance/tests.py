from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from student.models import Subject


class AttendanceReportGuardrailTests(TestCase):
    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'
        self.admin_user = User.objects.create_user('admin_att', password='Admin123!')
        self.admin_user.is_staff = True
        self.admin_user.save(update_fields=['is_staff'])
        self.subject = Subject.objects.create(name='Physics')

    def test_report_download_rejects_large_date_range(self):
        self.client.login(username='admin_att', password='Admin123!')

        response = self.client.post(
            reverse('attendance:attendance-report-download'),
            {
                'subject': self.subject.id,
                'start_date': date(2025, 1, 1),
                'end_date': date(2025, 4, 15),
                'format': 'xlsx',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('Date range is too large' in str(message) for message in messages))
