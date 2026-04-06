from django.urls import path
from .views import (
    StudentListView,
    StudentDetailView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
    StudentImportView,
    StudentImportTemplateView,
    SubjectListView,
    SubjectImportView,
    SubjectImportTemplateView,
    FirstLoginPasswordChangeView,
)

app_name = 'student'

urlpatterns = [
    path('', StudentListView.as_view(), name='student-list'),
    path('import/', StudentImportView.as_view(), name='student-import'),
    path('import/template/', StudentImportTemplateView.as_view(), name='student-import-template'),
    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('subjects/import/', SubjectImportView.as_view(), name='subject-import'),
    path('subjects/import/template/', SubjectImportTemplateView.as_view(), name='subject-import-template'),
    path('change-password/', FirstLoginPasswordChangeView.as_view(), name='first-login-change-password'),
    path('<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('create/', StudentCreateView.as_view(), name='student-create'),
    path('<int:pk>/update/', StudentUpdateView.as_view(), name='student-update'),
    path('<int:pk>/delete/', StudentDeleteView.as_view(), name='student-delete'),
]