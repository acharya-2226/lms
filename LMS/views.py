from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse
from django.shortcuts import render


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


class FrontendLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to

        user = self.request.user
        if hasattr(user, 'student_profile'):
            return reverse('student:student-list')
        if hasattr(user, 'teacher_profile'):
            return reverse('teacher:teacher-list')
        return reverse('home')


class FrontendLogoutView(LogoutView):
    next_page = 'login'
