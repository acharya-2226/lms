from django.shortcuts import redirect
from django.urls import reverse


class FirstLoginRedirectMiddleware:
    """
    Middleware to redirect users to password change page on first login.
    Excludes certain paths from the redirect.
    """
    
    AUTH_EXEMPT_PATH_PREFIXES = [
        '/login/',
        '/logout/',
        '/admin/login/',
        '/admin/logout/',
        '/admin/jsi18n/',
        '/static/',
        '/media/',
    ]

    FIRST_LOGIN_EXEMPT_PATH_PREFIXES = [
        '/admin/',
        '/students/change-password/',
        '/teachers/change-password/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path

        # Global authentication requirement for all non-exempt routes.
        if not request.user.is_authenticated:
            auth_exempt = any(path.startswith(prefix) for prefix in self.AUTH_EXEMPT_PATH_PREFIXES)
            if not auth_exempt:
                return redirect(f"{reverse('login')}?next={path}")
            return self.get_response(request)

        first_login_exempt = any(path.startswith(prefix) for prefix in self.FIRST_LOGIN_EXEMPT_PATH_PREFIXES)
        if not first_login_exempt:
            student = getattr(request.user, 'student_profile', None)
            if student and student.is_first_login:
                return redirect('student:first-login-change-password')

            teacher = getattr(request.user, 'teacher_profile', None)
            if teacher and teacher.is_first_login:
                return redirect('teacher:first-login-change-password')

        response = self.get_response(request)
        return response

