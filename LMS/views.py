from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse

from LMS.roles import get_student_profile, get_teacher_profile, is_admin_user


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


def home_view(request):
    return render(request, 'home.html')


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
