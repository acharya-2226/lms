from django.urls import path

from .views import (
    TeacherCreateView,
    TeacherDeleteView,
    TeacherDetailView,
    TeacherImportTemplateView,
    TeacherImportView,
    TeacherImportErrorReportView,
    TeacherListView,
    TeacherUpdateView,
    FirstLoginPasswordChangeView,
)

app_name = 'teacher'

urlpatterns = [
    path('', TeacherListView.as_view(), name='teacher-list'),
    path('import/', TeacherImportView.as_view(), name='teacher-import'),
    path('import/template/', TeacherImportTemplateView.as_view(), name='teacher-import-template'),
    path('import/errors/', TeacherImportErrorReportView.as_view(), name='teacher-import-errors'),
    path('change-password/', FirstLoginPasswordChangeView.as_view(), name='first-login-change-password'),
    path('<int:pk>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('create/', TeacherCreateView.as_view(), name='teacher-create'),
    path('<int:pk>/update/', TeacherUpdateView.as_view(), name='teacher-update'),
    path('<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher-delete'),
]
