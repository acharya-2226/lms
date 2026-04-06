from io import BytesIO
from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.utils.decorators import method_decorator
from openpyxl import Workbook, load_workbook

from student.models import Faculty
from .models import Teacher
from .forms import FirstLoginPasswordChangeForm
from LMS.views import access_denied_response


class NonStudentAccessRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'student_profile') and not (request.user.is_staff or request.user.is_superuser):
            return access_denied_response(request, 'Student accounts cannot access teacher management pages.')
        return super().dispatch(request, *args, **kwargs)


class TeacherListView(LoginRequiredMixin, NonStudentAccessRequiredMixin, ListView):
    model = Teacher
    template_name = 'teacher/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        return Teacher.objects.prefetch_related('faculties').order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view_mode = self.request.GET.get('view', 'grouped')
        if view_mode not in {'grouped', 'flat'}:
            view_mode = 'grouped'

        context['view_mode'] = view_mode

        grouped_teachers_map = OrderedDict()
        for teacher in context['teachers']:
            faculties = list(teacher.faculties.all())
            if not faculties:
                grouped_teachers_map.setdefault('No Faculty', []).append(teacher)
                continue

            for faculty in faculties:
                grouped_teachers_map.setdefault(faculty.name, []).append(teacher)

        context['grouped_teachers'] = [
            {
                'faculty': faculty,
                'teachers': teachers,
            }
            for faculty, teachers in grouped_teachers_map.items()
        ]
        return context


class TeacherDetailView(LoginRequiredMixin, NonStudentAccessRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teacher/teacher_detail.html'
    context_object_name = 'teacher'
    queryset = Teacher.objects.all()


class TeacherCreateView(LoginRequiredMixin, NonStudentAccessRequiredMixin, CreateView):
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


class TeacherUpdateView(LoginRequiredMixin, NonStudentAccessRequiredMixin, UpdateView):
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


class TeacherDeleteView(LoginRequiredMixin, NonStudentAccessRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'teacher/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher:teacher-list')


class TeacherImportView(LoginRequiredMixin, NonStudentAccessRequiredMixin, View):
    template_name = 'teacher/teacher_import.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        upload = request.FILES.get('xlsx_file')
        if not upload:
            messages.error(request, 'Please select an XLSX file to import.')
            return redirect('teacher:teacher-import')

        if not upload.name.lower().endswith('.xlsx'):
            messages.error(request, 'Only .xlsx files are supported.')
            return redirect('teacher:teacher-import')

        try:
            workbook = load_workbook(upload, data_only=True)
        except Exception:
            messages.error(request, 'Unable to read the file. Please use the provided template.')
            return redirect('teacher:teacher-import')

        worksheet = workbook.active
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for row in worksheet.iter_rows(min_row=2, values_only=True):
            if not row or all(value in (None, '') for value in row):
                continue

            name = str(row[0]).strip() if row[0] else ''
            employee_id = str(row[1]).strip() if row[1] else None
            department = str(row[2]).strip() if row[2] else None
            qualification = str(row[3]).strip() if row[3] else None
            experience_raw = row[4]
            faculties_raw = str(row[5]).strip() if row[5] else ''
            email = str(row[6]).strip() if row[6] else None
            address = str(row[7]).strip() if row[7] else None

            if not name:
                skipped_count += 1
                continue

            experience_years = None
            if experience_raw not in (None, ''):
                try:
                    experience_years = int(experience_raw)
                except (TypeError, ValueError):
                    skipped_count += 1
                    continue

            defaults = {
                'name': name,
                'department': department,
                'qualification': qualification,
                'experience_years': experience_years,
                'email': email,
                'address': address,
            }

            try:
                if employee_id:
                    teacher, created = Teacher.objects.update_or_create(
                        employee_id=employee_id,
                        defaults=defaults,
                    )
                elif email:
                    teacher, created = Teacher.objects.update_or_create(
                        email=email,
                        defaults={**defaults, 'employee_id': None},
                    )
                else:
                    teacher = Teacher.objects.create(
                        **defaults,
                        employee_id=None,
                    )
                    created = True
            except Exception:
                skipped_count += 1
                continue

            faculty_names = [item.strip() for item in faculties_raw.split(',') if item.strip()]
            faculties = [Faculty.objects.get_or_create_case_insensitive(faculty_name)[0] for faculty_name in faculty_names]
            teacher.faculties.set(faculties)

            if created:
                created_count += 1
            else:
                updated_count += 1

        messages.success(
            request,
            f'Import finished. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}.',
        )
        return redirect('teacher:teacher-list')


class TeacherImportTemplateView(LoginRequiredMixin, NonStudentAccessRequiredMixin, View):
    def get(self, request):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Teachers'

        worksheet.append([
            'name',
            'employee_id',
            'department',
            'qualification',
            'experience_years',
            'faculties',
            'email',
            'address',
        ])
        worksheet.append([
            'Sita Karki',
            'EMP-1042',
            'Computer Science',
            'MSc Computer Science',
            6,
            'Computer Science, IT',
            'sita.karki@example.com',
            'Pokhara',
        ])

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="teacher_import_template.xlsx"'
        return response


@method_decorator(login_required, name='dispatch')
class FirstLoginPasswordChangeView(View):
    """View for changing password on first login"""
    template_name = 'teacher/first_login_password_change.html'
    
    def get(self, request):
        """Display password change form"""
        try:
            teacher = request.user.teacher_profile
            if not teacher.is_first_login:
                messages.info(request, 'You have already changed your password.')
                return redirect('teacher:teacher-list')
        except AttributeError:
            # User is not a teacher, redirect to home
            messages.error(request, 'Only teachers can access this page.')
            return redirect('/')
        
        form = FirstLoginPasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process password change"""
        try:
            teacher = request.user.teacher_profile
        except AttributeError:
            messages.error(request, 'Only teachers can access this page.')
            return redirect('/')
        
        form = FirstLoginPasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            form.save()
            
            # Mark first login as False
            teacher.is_first_login = False
            teacher.save()
            
            messages.success(request, 'Your password has been changed successfully. Please login again.')
            return redirect('login')
        
        return render(request, self.template_name, {'form': form})

