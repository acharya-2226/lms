from django.urls import path

from .views import (
    AttendanceCreateView,
    AttendanceDeleteView,
    AttendanceDetailView,
    AttendanceListView,
    AttendanceReportDownloadView,
    AttendanceReportView,
    AttendanceRosterView,
    AttendanceUpdateView,
)

app_name = 'attendance'

urlpatterns = [
    path('', AttendanceListView.as_view(), name='attendance-list'),
    path('report/', AttendanceReportView.as_view(), name='attendance-report'),
    path('report/download/', AttendanceReportDownloadView.as_view(), name='attendance-report-download'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('<int:pk>/roster/', AttendanceRosterView.as_view(), name='attendance-roster'),
    path('create/', AttendanceCreateView.as_view(), name='attendance-create'),
    path('<int:pk>/update/', AttendanceUpdateView.as_view(), name='attendance-update'),
    path('<int:pk>/delete/', AttendanceDeleteView.as_view(), name='attendance-delete'),
]
