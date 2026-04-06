from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from .views import FrontendLoginView, FrontendLogoutView

handler403 = 'LMS.views.permission_denied_handler'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', FrontendLoginView.as_view(), name='login'),
    path('logout/', FrontendLogoutView.as_view(), name='logout'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('student/', RedirectView.as_view(pattern_name='student:student-list', permanent=False)),
    path('teacher/', RedirectView.as_view(pattern_name='teacher:teacher-list', permanent=False)),
    path('assignment/', RedirectView.as_view(pattern_name='assignment:assignment-list', permanent=False)),
    path('attendance/', RedirectView.as_view(pattern_name='attendance:attendance-list', permanent=False)),
    path('students/', include('student.urls')),
    path('teachers/', include('teacher.urls')),
    path('assignments/', include('assignment.urls')),
    path('attendances/', include('attendance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
