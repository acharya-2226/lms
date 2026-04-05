from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django import forms
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from student.models import Student

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


class AssignmentListView(ListView):
    model = Assignment
    template_name = 'assignment/assignment_list.html'
    context_object_name = 'assignments'


class AssignmentDetailView(DetailView):
    model = Assignment
    template_name = 'assignment/assignment_detail.html'
    context_object_name = 'assignment'
    queryset = Assignment.objects.all()


class AssignmentRosterView(DetailView):
    model = Assignment
    template_name = 'assignment/assignment_roster.html'
    context_object_name = 'assignment'
    queryset = Assignment.objects.select_related('faculty', 'enrollment_batch').all()

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
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


class AssignmentCreateView(CreateView):
    model = Assignment
    template_name = 'assignment/assignment_form.html'
    form_class = AssignmentForm

    def form_valid(self, form):
        self.object = form.save()
        seed_assignment_recipients(self.object)
        messages.success(self.request, 'Assignment created successfully.')
        return redirect('assignment:assignment-roster', pk=self.object.pk)


class AssignmentUpdateView(UpdateView):
    model = Assignment
    template_name = 'assignment/assignment_form.html'
    form_class = AssignmentForm
    success_url = reverse_lazy('assignment:assignment-list')


class AssignmentDeleteView(DeleteView):
    model = Assignment
    template_name = 'assignment/assignment_confirm_delete.html'
    success_url = reverse_lazy('assignment:assignment-list')
