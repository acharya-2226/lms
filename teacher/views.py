from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Teacher


class TeacherListView(ListView):
    model = Teacher
    template_name = 'teacher/teacher_list.html'
    context_object_name = 'teachers'


class TeacherDetailView(DetailView):
    model = Teacher
    template_name = 'teacher/teacher_detail.html'
    context_object_name = 'teacher'
    queryset = Teacher.objects.all()


class TeacherCreateView(CreateView):
    model = Teacher
    template_name = 'teacher/teacher_form.html'
    fields = [
        'name',
        'employee_id',
        'department',
        'qualification',
        'experience_years',
        'faculties',
        'email',
        'dp',
        'address',
    ]
    success_url = reverse_lazy('teacher:teacher-create')


class TeacherUpdateView(UpdateView):
    model = Teacher
    template_name = 'teacher/teacher_form.html'
    fields = [
        'name',
        'employee_id',
        'department',
        'qualification',
        'experience_years',
        'faculties',
        'email',
        'dp',
        'address',
    ]
    success_url = reverse_lazy('teacher:teacher-list')


class TeacherDeleteView(DeleteView):
    model = Teacher
    template_name = 'teacher/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher:teacher-list')
