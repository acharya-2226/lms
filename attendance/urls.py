from django.urls import path

from .views import (
    AttendanceCreateView,
    AttendanceDeleteView,
    AttendanceDetailView,
    AttendanceListView,
    AttendanceRosterView,
    AttendanceUpdateView,
)

app_name = 'attendance'

urlpatterns = [
    path('', AttendanceListView.as_view(), name='attendance-list'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('<int:pk>/roster/', AttendanceRosterView.as_view(), name='attendance-roster'),
    path('create/', AttendanceCreateView.as_view(), name='attendance-create'),
    path('<int:pk>/update/', AttendanceUpdateView.as_view(), name='attendance-update'),
    path('<int:pk>/delete/', AttendanceDeleteView.as_view(), name='attendance-delete'),
]
