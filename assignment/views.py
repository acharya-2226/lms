from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django import forms
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from student.models import Student
from LMS.views import access_denied_response

from .models import Assignment, AssignmentRecipient


def seed_assignment_recipients(assignment):
    if not assignment.faculty or not assignment.enrollment_batch:
        return

    students = Student.objects.filter(
        faculty=assignment.faculty,
        enrollment_batch=assignment.enrollment_batch,
    )
    for student in students:
        AssignmentRecipient.objects.get_or_create(
            assignment=assignment,
            student=student,
        )


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'teacher', 'faculty', 'enrollment_batch', 'attachment', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class RoleFilteredAssignmentQuerysetMixin:
    def get_base_queryset(self):
        return Assignment.objects.select_related(
            'subject', 'teacher', 'faculty', 'enrollment_batch'
        ).prefetch_related('recipients__student')

    def get_role_filtered_queryset(self):
        queryset = self.get_base_queryset()
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return queryset

        student_profile = getattr(user, 'student_profile', None)
        if student_profile:
            return queryset.filter(recipients__student=student_profile).distinct()

        teacher_profile = getattr(user, 'teacher_profile', None)
        if teacher_profile:
            return queryset.filter(
                Q(teacher=teacher_profile) | Q(faculty__in=teacher_profile.faculties.all())
            ).distinct()

        return queryset.none()


class TeacherOrAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser or user.is_staff or hasattr(user, 'teacher_profile')
        )

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return access_denied_response(self.request, 'You do not have permission to modify assignments.')
        return super().handle_no_permission()


class AssignmentListView(LoginRequiredMixin, RoleFilteredAssignmentQuerysetMixin, ListView):
    model = Assignment
    template_name = 'assignment/assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return self.get_role_filtered_queryset().order_by('-created_at', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = getattr(self.request.user, 'student_profile', None)
        if student_profile:
            recipient_lookup = {
                recipient.assignment_id: recipient
                for recipient in AssignmentRecipient.objects.filter(
                    student=student_profile,
                    assignment__in=context['assignments'],
                )
            }
            for assignment in context['assignments']:
                assignment.current_recipient = recipient_lookup.get(assignment.id)
        return context


class AssignmentDetailView(LoginRequiredMixin, RoleFilteredAssignmentQuerysetMixin, DetailView):
    model = Assignment
    template_name = 'assignment/assignment_detail.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        return self.get_role_filtered_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = getattr(self.request.user, 'student_profile', None)
        recipient = None
        if student_profile:
            recipient = AssignmentRecipient.objects.filter(
                assignment=self.object,
                student=student_profile,
            ).first()
            if recipient and not recipient.is_seen:
                recipient.is_seen = True
                recipient.seen_at = timezone.now()
                recipient.save(update_fields=['is_seen', 'seen_at'])
        context['student_recipient'] = recipient
        return context


class AssignmentRosterView(LoginRequiredMixin, RoleFilteredAssignmentQuerysetMixin, DetailView):
    model = Assignment
    template_name = 'assignment/assignment_roster.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        queryset = self.get_role_filtered_queryset().select_related('faculty', 'enrollment_batch')
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return queryset

        teacher_profile = getattr(user, 'teacher_profile', None)
        if teacher_profile:
            return queryset.filter(
                Q(teacher=teacher_profile) | Q(faculty__in=teacher_profile.faculties.all())
            ).distinct()

        return queryset.none()

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not (request.user.is_superuser or request.user.is_staff or hasattr(request.user, 'teacher_profile')):
            return access_denied_response(request, 'Only teachers and admins can view assignment rosters.')
        self.ensure_recipients_exist()
        if request.method == 'POST':
            return self.handle_post(request)
        return super().dispatch(request, *args, **kwargs)

    def ensure_recipients_exist(self):
        seed_assignment_recipients(self.object)

    def handle_post(self, request):
        recipient_id = request.POST.get('recipient_id')
        if recipient_id:
            recipient = get_object_or_404(AssignmentRecipient, pk=recipient_id, assignment=self.object)
            if not recipient.is_notified:
                recipient.is_notified = True
                recipient.notified_at = timezone.now()
                recipient.save(update_fields=['is_notified', 'notified_at'])
        return redirect('assignment:assignment-roster', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipients'] = self.object.recipients.select_related('student').order_by('student__name')
        context['matching_students'] = Student.objects.filter(
            faculty=self.object.faculty,
            enrollment_batch=self.object.enrollment_batch,
        ).order_by('name') if self.object.faculty and self.object.enrollment_batch else Student.objects.none()
        return context


class AssignmentCreateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, CreateView):
    model = Assignment
    template_name = 'assignment/assignment_form.html'
    form_class = AssignmentForm

    def form_valid(self, form):
        self.object = form.save()
        seed_assignment_recipients(self.object)
        messages.success(self.request, 'Assignment created successfully.')
        return redirect('assignment:assignment-roster', pk=self.object.pk)


class AssignmentUpdateView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, RoleFilteredAssignmentQuerysetMixin, UpdateView):
    model = Assignment
    template_name = 'assignment/assignment_form.html'
    form_class = AssignmentForm
    success_url = reverse_lazy('assignment:assignment-list')

    def get_queryset(self):
        queryset = self.get_role_filtered_queryset()
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return queryset
        teacher_profile = getattr(user, 'teacher_profile', None)
        if teacher_profile:
            return queryset.filter(
                Q(teacher=teacher_profile) | Q(faculty__in=teacher_profile.faculties.all())
            ).distinct()
        return queryset.none()


class AssignmentDeleteView(LoginRequiredMixin, TeacherOrAdminRequiredMixin, RoleFilteredAssignmentQuerysetMixin, DeleteView):
    model = Assignment
    template_name = 'assignment/assignment_confirm_delete.html'
    success_url = reverse_lazy('assignment:assignment-list')

    def get_queryset(self):
        queryset = self.get_role_filtered_queryset()
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return queryset
        teacher_profile = getattr(user, 'teacher_profile', None)
        if teacher_profile:
            return queryset.filter(
                Q(teacher=teacher_profile) | Q(faculty__in=teacher_profile.faculties.all())
            ).distinct()
        return queryset.none()


class AssignmentSubmissionView(LoginRequiredMixin, RoleFilteredAssignmentQuerysetMixin, View):
    def post(self, request, pk):
        student_profile = getattr(request.user, 'student_profile', None)
        if not student_profile:
            return access_denied_response(request, 'Only students can submit assignment files.')

        assignment = get_object_or_404(self.get_role_filtered_queryset(), pk=pk)
        recipient, _ = AssignmentRecipient.objects.get_or_create(
            assignment=assignment,
            student=student_profile,
        )

        submission_file = request.FILES.get('submission_file')
        if not submission_file:
            messages.error(request, 'Please choose a file before submitting.')
            return redirect('assignment:assignment-detail', pk=assignment.pk)

        recipient.submission_file = submission_file
        recipient.is_submitted = True
        recipient.submitted_at = timezone.now()
        if not recipient.is_seen:
            recipient.is_seen = True
            recipient.seen_at = timezone.now()
        recipient.save(update_fields=['submission_file', 'is_submitted', 'submitted_at', 'is_seen', 'seen_at'])

        messages.success(request, 'Assignment submitted successfully.')
        return redirect('assignment:assignment-detail', pk=assignment.pk)
