from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from teacher.models import Teacher


class TeacherFirstLoginFlowTests(TestCase):
    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'

    def test_teacher_first_login_is_redirected_to_password_change(self):
        user = User.objects.create_user('teacher1', password='Temp123!')
        Teacher.objects.create(user=user, name='Teacher One', is_first_login=True)

        self.client.login(username='teacher1', password='Temp123!')
        response = self.client.get(reverse('assignment:assignment-list'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('teacher:first-login-change-password'))

    def test_teacher_without_first_login_can_open_teacher_list(self):
        user = User.objects.create_user('teacher2', password='Temp123!')
        Teacher.objects.create(user=user, name='Teacher Two', is_first_login=False)

        self.client.login(username='teacher2', password='Temp123!')
        response = self.client.get(reverse('teacher:teacher-list'))
        self.assertEqual(response.status_code, 200)
