from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html, mark_safe
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import EnrollmentYear, Faculty, Student, Subject
from .admin_actions import (
    import_students_from_csv, 
    generate_credentials_pdf, 
    generate_csv_template
)


class CSVImportForm:
    """Simple form handler for CSV import"""
    pass


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(EnrollmentYear)
class EnrollmentYearAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'enrollment_batch', 'faculty', 'age', 'email', 'enrollment_date', 'user_column')
    search_fields = ('name', 'roll_number', '=enrollment_batch__year', 'faculty__name', 'email')
    list_filter = ('enrollment_batch', 'faculty', 'age', 'enrollment_date', 'is_first_login')
    change_list_template = 'admin/student/change_list.html'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'age', 'email', 'address', 'dp')
        }),
        ('Academic Information', {
            'fields': ('roll_number', 'enrollment_batch', 'faculty')
        }),
        ('Account Information', {
            'fields': ('user', 'is_first_login'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('enrollment_date',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('enrollment_date',)
    
    def user_column(self, obj):
        """Display user linked to student"""
        if obj.user:
            return format_html('<span style="color: green;">✓ {}</span>', obj.user.username)
        return mark_safe('<span style="color: red;">✗ No User</span>')
    user_column.short_description = 'User'
    
    def get_urls(self):
        """Add custom URLs for CSV import and download"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv),
                name='student_import_csv',
            ),
            path(
                'download-csv-template/',
                self.admin_site.admin_view(self.download_csv_template),
                name='student_download_csv_template',
            ),
        ]
        return custom_urls + urls
    
    def import_csv(self, request):
        """Handle CSV import request"""
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please select a CSV file to import.')
                return render(request, 'admin/student_import.html', {'admin_site': self.admin_site})
            
            if not csv_file.name.lower().endswith('.csv'):
                messages.error(request, 'Only .csv files are supported.')
                return render(request, 'admin/student_import.html', {'admin_site': self.admin_site})
            
            # Import students from CSV
            created_users_data, updated_students_count, error_messages = import_students_from_csv(request, csv_file)
            
            # Display messages
            if error_messages:
                for error in error_messages:
                    messages.warning(request, error)
            
            if created_users_data:
                messages.success(
                    request,
                    f'Successfully created {len(created_users_data)} student account(s) '
                    f'and updated {updated_students_count} record(s).'
                )
                
                # Generate and download PDF with credentials
                pdf_buffer = generate_credentials_pdf(created_users_data)
                response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="student_credentials.pdf"'
                return response
            elif updated_students_count > 0:
                messages.success(request, f'Successfully updated {updated_students_count} student record(s).')
            else:
                messages.warning(request, 'No students were imported or updated.')
            
            return redirect('admin:student_student_changelist')
        
        # GET request - show import form
        return render(
            request,
            'admin/student_import.html',
            {
                'admin_site': self.admin_site,
                'title': 'Import Students from CSV',
                'has_change_permission': self.has_change_permission(request),
            }
        )
    
    def download_csv_template(self, request):
        """Download CSV template for student import"""
        return generate_csv_template(request)
    
    def changelist_view(self, request, extra_context=None):
        """Add import/download buttons to changelist"""
        extra_context = extra_context or {}
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        try:
            extra_context['import_csv_url'] = reverse(f'admin:{app_label}_{model_name}_import_csv')
            extra_context['download_template_url'] = reverse(f'admin:{app_label}_{model_name}_download_csv_template')
        except:
            # Fallback if reverse doesn't work
            base = request.path.rsplit('/', 1)[0] + '/'
            extra_context['import_csv_url'] = base + 'import-csv/'
            extra_context['download_template_url'] = base + 'download-csv-template/'
        return super().changelist_view(request, extra_context=extra_context)
