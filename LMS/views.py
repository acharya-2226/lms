import logging

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from LMS.roles import get_student_profile, get_teacher_profile, is_admin_user


logger = logging.getLogger('LMS')


def get_default_authenticated_redirect(user):
    if get_student_profile(user):
        if getattr(user.student_profile, 'is_first_login', False):
            return reverse('student:first-login-change-password')
        return reverse('assignment:assignment-list')
    if get_teacher_profile(user):
        if getattr(user.teacher_profile, 'is_first_login', False):
            return reverse('teacher:first-login-change-password')
        return reverse('assignment:assignment-list')
    if is_admin_user(user):
        return reverse('student:student-list')
    return reverse('home')


def access_denied_response(request, message='You do not have permission to access this module.', status=403):
    logger.warning(
        'Permission denied for path=%s user=%s reason=%s',
        request.path,
        request.user.username if request.user.is_authenticated else 'anonymous',
        message,
    )
    return render(
        request,
        'errors/access_denied.html',
        {
            'error_message': message,
        },
        status=status,
    )


def permission_denied_handler(request, exception=None):
    message = 'You do not have permission to access this module.'
    if exception:
        message = str(exception)
    return access_denied_response(request, message=message, status=403)


def bad_request_handler(request, exception=None):
    return render(
        request,
        'errors/400.html',
        {
            'error_message': 'The request could not be processed. Please verify your input and try again.',
        },
        status=400,
    )


def page_not_found_handler(request, exception=None):
    return render(
        request,
        'errors/404.html',
        {
            'error_message': 'The page you are looking for does not exist or has been moved.',
        },
        status=404,
    )


def server_error_handler(request):
    return render(
        request,
        'errors/500.html',
        {
            'error_message': 'Something went wrong on our side. Please try again in a few minutes.',
        },
        status=500,
    )


def home_view(request):
    user = request.user
    dashboard = {
        'role': 'anonymous',
        'quick_actions': [],
        'pending_summary': 'Sign in to view your dashboard.',
        'recent_activity': 'Recent activity appears here after login.',
    }

    if user.is_authenticated:
        if is_admin_user(user):
            dashboard = {
                'role': 'admin',
                'quick_actions': [
                    {'label': 'Manage Students', 'url': reverse('student:student-list')},
                    {'label': 'Manage Teachers', 'url': reverse('teacher:teacher-list')},
                    {'label': 'Import Data', 'url': reverse('student:student-import')},
                    {'label': 'Attendance Reports', 'url': reverse('attendance:attendance-report')},
                ],
                'pending_summary': 'Review imports, assignment rosters, and attendance exceptions.',
                'recent_activity': 'Admin activity feed placeholder. Integrate audit logs in v1.2.',
            }
        elif get_teacher_profile(user):
            dashboard = {
                'role': 'teacher',
                'quick_actions': [
                    {'label': 'Students', 'url': reverse('student:student-list')},
                    {'label': 'Assignments', 'url': reverse('assignment:assignment-list')},
                    {'label': 'Attendance', 'url': reverse('attendance:attendance-list')},
                    {'label': 'Timetable', 'url': reverse('attendance:attendance-timetable')},
                ],
                'pending_summary': 'Track pending submissions and attendance marks for your classes.',
                'recent_activity': 'Teacher activity feed placeholder. Connect classroom events next.',
            }
        elif get_student_profile(user):
            dashboard = {
                'role': 'student',
                'quick_actions': [
                    {'label': 'Assignments', 'url': reverse('assignment:assignment-list')},
                    {'label': 'Attendance', 'url': reverse('attendance:attendance-list')},
                    {'label': 'Timetable', 'url': reverse('attendance:attendance-timetable')},
                ],
                'pending_summary': 'Check pending assignments and attendance updates for your batch.',
                'recent_activity': 'Student activity feed placeholder. Submission timeline coming soon.',
            }

    return render(request, 'home.html', {'dashboard': dashboard})


def health_check_view(request):
    if request.headers.get('accept', '').lower().startswith('application/json'):
        return JsonResponse({'status': 'ok'})
    return HttpResponse('ok', content_type='text/plain')


class FrontendLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid credentials.')
        return super().form_invalid(form)

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to

        default_redirect = get_default_authenticated_redirect(self.request.user)
        if default_redirect == reverse('home'):
            messages.error(self.request, 'This account is not configured for LMS access.')
        return default_redirect


class FrontendLogoutView(LogoutView):
    next_page = 'login'
