from django.urls import path

from .views import (
    AssignmentCreateView,
    AssignmentDeleteView,
    AssignmentDetailView,
    AssignmentListView,
    AssignmentRosterView,
    AssignmentUpdateView,
)

app_name = 'assignment'

urlpatterns = [
    path('', AssignmentListView.as_view(), name='assignment-list'),
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:pk>/roster/', AssignmentRosterView.as_view(), name='assignment-roster'),
    path('create/', AssignmentCreateView.as_view(), name='assignment-create'),
    path('<int:pk>/update/', AssignmentUpdateView.as_view(), name='assignment-update'),
    path('<int:pk>/delete/', AssignmentDeleteView.as_view(), name='assignment-delete'),
]
