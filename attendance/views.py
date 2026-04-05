from django.contrib import messages
from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from student.models import Student

from .models import Attendance, AttendanceEntry


def seed_attendance_entries(attendance):
    if not attendance.faculty or not attendance.enrollment_batch:
        return

    students = Student.objects.filter(
        faculty=attendance.faculty,
        enrollment_batch=attendance.enrollment_batch,
    )
    for student in students:
        AttendanceEntry.objects.get_or_create(
            attendance=attendance,
            student=student,
        )


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['subject', 'teacher', 'faculty', 'enrollment_batch', 'attendance_date', 'note']
        widgets = {
            'attendance_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AttendanceListView(ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'


class AttendanceDetailView(DetailView):
    model = Attendance
    template_name = 'attendance/attendance_detail.html'
    context_object_name = 'attendance'
    queryset = Attendance.objects.all()


class AttendanceRosterView(DetailView):
    model = Attendance
    template_name = 'attendance/attendance_roster.html'
    context_object_name = 'attendance'
    queryset = Attendance.objects.select_related('subject', 'teacher', 'faculty', 'enrollment_batch').all()

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.ensure_entries_exist()
        if request.method == 'POST':
            return self.handle_post(request)
        return super().dispatch(request, *args, **kwargs)

    def ensure_entries_exist(self):
        seed_attendance_entries(self.object)

    def handle_post(self, request):
        entry_id = request.POST.get('entry_id')
        status = request.POST.get('status')
        if entry_id and status in {'present', 'absent', 'unmarked'}:
            entry = get_object_or_404(AttendanceEntry, pk=entry_id, attendance=self.object)
            entry.status = status
            entry.marked_at = timezone.now() if status != 'unmarked' else None
            entry.save(update_fields=['status', 'marked_at'])
        return redirect('attendance:attendance-roster', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entries'] = self.object.entries.select_related('student').order_by('student__name')
        context['matching_students'] = Student.objects.filter(
            faculty=self.object.faculty,
            enrollment_batch=self.object.enrollment_batch,
        ).order_by('name') if self.object.faculty and self.object.enrollment_batch else Student.objects.none()
        return context


class AttendanceCreateView(CreateView):
    model = Attendance
    template_name = 'attendance/attendance_form.html'
    form_class = AttendanceForm

    def form_valid(self, form):
        self.object = form.save()
        seed_attendance_entries(self.object)
        messages.success(self.request, 'Attendance created successfully.')
        return redirect('attendance:attendance-roster', pk=self.object.pk)


class AttendanceUpdateView(UpdateView):
    model = Attendance
    template_name = 'attendance/attendance_form.html'
    form_class = AttendanceForm
    success_url = reverse_lazy('attendance:attendance-list')


class AttendanceDeleteView(DeleteView):
    model = Attendance
    template_name = 'attendance/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:attendance-list')
