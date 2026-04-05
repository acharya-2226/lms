from django.shortcuts import render
# Creating views for the Student model using Django's generic class-based views
# StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView,StudentDeleteView
# Create your views here.

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Student
from django.urls import reverse_lazy

class StudentListView(ListView):
    model = Student
    template_name = 'student/student_list.html'
    context_object_name = 'students'

class StudentDetailView(DetailView):
    model = Student
    template_name = 'student/student_detail.html'
    context_object_name = 'student'
    queryset = Student.objects.all()

class StudentCreateView(CreateView):
    model = Student
    template_name = 'student/student_form.html'
    fields = ['name', 'roll_number', 'enrollment_batch', 'faculty', 'age', 'email', 'dp', 'address']
    success_url = reverse_lazy('student:student-create')

class StudentUpdateView(UpdateView):
    model = Student
    template_name = 'student/student_form.html'
    fields = ['name', 'roll_number', 'enrollment_batch', 'faculty', 'age', 'email', 'dp', 'address']
    success_url = reverse_lazy('student:student-list')

class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'student/student_confirm_delete.html'
    success_url = reverse_lazy('student:student-list')

