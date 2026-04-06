from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from openpyxl import Workbook

from student.models import EnrollmentYear, Faculty, Student


class StudentRouteBehaviorTests(TestCase):
	def setUp(self):
		self.client.defaults['HTTP_HOST'] = 'localhost'

	def test_anonymous_redirect_preserves_next_path(self):
		response = self.client.get(reverse('student:student-list'))
		self.assertEqual(response.status_code, 302)
		self.assertIn('/login/?next=/students/', response['Location'])

	def test_health_endpoint_returns_ok(self):
		response = self.client.get(reverse('health-check'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode('utf-8'), 'ok')


class StudentListPaginationTests(TestCase):
	def setUp(self):
		self.client.defaults['HTTP_HOST'] = 'localhost'
		self.admin_user = User.objects.create_user('admin', password='Admin123!')
		self.admin_user.is_staff = True
		self.admin_user.save(update_fields=['is_staff'])
		self.faculty = Faculty.objects.create(name='Engineering')
		self.year = EnrollmentYear.objects.create(year=2026)

	def test_student_list_is_paginated(self):
		for index in range(30):
			Student.objects.create(
				name=f'Student {index}',
				roll_number=f'R-{index}',
				faculty=self.faculty,
				enrollment_batch=self.year,
			)

		self.client.login(username='admin', password='Admin123!')
		response = self.client.get(reverse('student:student-list'))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['is_paginated'])
		self.assertEqual(len(response.context['page_obj'].object_list), 25)


class StudentImportPreviewCommitTests(TestCase):
	def setUp(self):
		self.client.defaults['HTTP_HOST'] = 'localhost'
		self.admin_user = User.objects.create_user('admin_import', password='Admin123!')
		self.admin_user.is_staff = True
		self.admin_user.save(update_fields=['is_staff'])

	def _build_workbook_upload(self):
		workbook = Workbook()
		worksheet = workbook.active
		worksheet.append(['name', 'roll_number', 'enrollment_year', 'faculty', 'age', 'email', 'address'])
		worksheet.append(['Import User', 'IMP-01', 2026, 'Engineering', 21, 'import@example.com', 'City'])

		from io import BytesIO

		output = BytesIO()
		workbook.save(output)
		output.seek(0)
		return SimpleUploadedFile(
			'students.xlsx',
			output.getvalue(),
			content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		)

	def test_preview_then_commit_import(self):
		self.client.login(username='admin_import', password='Admin123!')

		preview_response = self.client.post(
			reverse('student:student-import'),
			{'action': 'preview', 'xlsx_file': self._build_workbook_upload()},
			follow=True,
		)

		self.assertEqual(preview_response.status_code, 200)
		self.assertContains(preview_response, 'Preview Summary')
		self.assertEqual(Student.objects.count(), 0)

		commit_response = self.client.post(
			reverse('student:student-import'),
			{'action': 'commit'},
			follow=True,
		)

		self.assertEqual(commit_response.status_code, 200)
		self.assertEqual(Student.objects.count(), 1)
