from django.urls import path

from .views import (
    AttendanceCreateView,
    AttendanceDeleteView,
    AttendanceDetailView,
    AttendanceListView,
    AttendanceReportDownloadView,
    AttendanceReportView,
    AttendanceRosterView,
    AttendanceTimetableView,
    AttendanceUpdateView,
    WeeklyScheduleCreateView,
    WeeklyScheduleDeleteView,
    WeeklyScheduleListView,
    WeeklyScheduleUpdateView,
)

app_name = 'attendance'

urlpatterns = [
    path('', AttendanceListView.as_view(), name='attendance-list'),
    path('weekly-schedules/', WeeklyScheduleListView.as_view(), name='weekly-schedule-list'),
    path('weekly-schedules/create/', WeeklyScheduleCreateView.as_view(), name='weekly-schedule-create'),
    path('weekly-schedules/<int:pk>/update/', WeeklyScheduleUpdateView.as_view(), name='weekly-schedule-update'),
    path('weekly-schedules/<int:pk>/delete/', WeeklyScheduleDeleteView.as_view(), name='weekly-schedule-delete'),
    path('report/', AttendanceReportView.as_view(), name='attendance-report'),
    path('report/download/', AttendanceReportDownloadView.as_view(), name='attendance-report-download'),
    path('timetable/', AttendanceTimetableView.as_view(), name='attendance-timetable'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('<int:pk>/roster/', AttendanceRosterView.as_view(), name='attendance-roster'),
    path('create/', AttendanceCreateView.as_view(), name='attendance-create'),
    path('<int:pk>/update/', AttendanceUpdateView.as_view(), name='attendance-update'),
    path('<int:pk>/delete/', AttendanceDeleteView.as_view(), name='attendance-delete'),
]
