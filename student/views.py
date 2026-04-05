from io import BytesIO
from collections import OrderedDict

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from openpyxl import Workbook, load_workbook

from .models import EnrollmentYear, Faculty, Student

class StudentListView(ListView):
    model = Student
    template_name = 'student/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.objects.select_related('faculty', 'enrollment_batch').order_by(
            'faculty__name',
            'enrollment_batch__year',
            'name',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view_mode = self.request.GET.get('view', 'grouped')
        if view_mode not in {'grouped', 'flat'}:
            view_mode = 'grouped'

        context['view_mode'] = view_mode

        grouped_students_map = OrderedDict()
        for student in context['students']:
            faculty_name = student.faculty.name if student.faculty else 'No Faculty'
            enrollment_year = (
                str(student.enrollment_batch.year) if student.enrollment_batch else 'No Enrollment Year'
            )
            group_key = (faculty_name, enrollment_year)
            grouped_students_map.setdefault(group_key, []).append(student)

        context['grouped_students'] = [
            {
                'faculty': faculty,
                'enrollment_year': enrollment_year,
                'students': students,
            }
            for (faculty, enrollment_year), students in grouped_students_map.items()
        ]
        return context

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


class StudentImportView(View):
    template_name = 'student/student_import.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        upload = request.FILES.get('xlsx_file')
        if not upload:
            messages.error(request, 'Please select an XLSX file to import.')
            return redirect('student:student-import')

        if not upload.name.lower().endswith('.xlsx'):
            messages.error(request, 'Only .xlsx files are supported.')
            return redirect('student:student-import')

        try:
            workbook = load_workbook(upload, data_only=True)
        except Exception:
            messages.error(request, 'Unable to read the file. Please use the provided template.')
            return redirect('student:student-import')

        worksheet = workbook.active
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for row in worksheet.iter_rows(min_row=2, values_only=True):
            if not row or all(value in (None, '') for value in row):
                continue

            name = str(row[0]).strip() if row[0] else ''
            roll_number = str(row[1]).strip() if row[1] else None
            enrollment_year_raw = row[2]
            faculty_name = str(row[3]).strip() if row[3] else None
            age_raw = row[4]
            email = str(row[5]).strip() if row[5] else None
            address = str(row[6]).strip() if row[6] else None

            if not name:
                skipped_count += 1
                continue

            enrollment_batch = None
            if enrollment_year_raw not in (None, ''):
                try:
                    year_value = int(enrollment_year_raw)
                except (TypeError, ValueError):
                    skipped_count += 1
                    continue
                enrollment_batch, _ = EnrollmentYear.objects.get_or_create(year=year_value)

            faculty = None
            if faculty_name:
                faculty, _ = Faculty.objects.get_or_create_case_insensitive(faculty_name)

            age = None
            if age_raw not in (None, ''):
                try:
                    age = int(age_raw)
                except (TypeError, ValueError):
                    skipped_count += 1
                    continue

            defaults = {
                'name': name,
                'enrollment_batch': enrollment_batch,
                'faculty': faculty,
                'age': age,
                'email': email,
                'address': address,
            }

            try:
                if roll_number:
                    student, created = Student.objects.update_or_create(
                        roll_number=roll_number,
                        defaults=defaults,
                    )
                elif email:
                    student, created = Student.objects.update_or_create(
                        email=email,
                        defaults={**defaults, 'roll_number': None},
                    )
                else:
                    student = Student.objects.create(
                        **defaults,
                        roll_number=None,
                    )
                    created = True
            except Exception:
                skipped_count += 1
                continue

            if created:
                created_count += 1
            else:
                updated_count += 1

        messages.success(
            request,
            f'Import finished. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}.',
        )
        return redirect('student:student-list')


class StudentImportTemplateView(View):
    def get(self, request):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Students'

        worksheet.append([
            'name',
            'roll_number',
            'enrollment_year',
            'faculty',
            'age',
            'email',
            'address',
        ])
        worksheet.append([
            'Aarav Sharma',
            'CS-2026-001',
            2026,
            'Computer Science',
            20,
            'aarav@example.com',
            'Kathmandu',
        ])

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="student_import_template.xlsx"'
        return response

