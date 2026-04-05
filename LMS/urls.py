from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('student/', RedirectView.as_view(pattern_name='student:student-list', permanent=False)),
    path('teacher/', RedirectView.as_view(pattern_name='teacher:teacher-list', permanent=False)),
    path('students/', include('student.urls')),
    path('teachers/', include('teacher.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
