from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html, mark_safe
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Teacher
from .admin_actions import (
    import_teachers_from_csv,
    generate_credentials_pdf,
    generate_csv_template
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'employee_id',
        'department',
        'faculty_list',
        'qualification',
        'experience_years',
        'email',
        'joining_date',
        'user_column',
    )
    search_fields = ('name', 'employee_id', 'department', 'qualification', 'email', 'faculties__name')
    list_filter = ('department', 'qualification', 'faculties', 'joining_date', 'is_first_login')
    filter_horizontal = ('faculties',)
    change_list_template = 'admin/teacher/change_list.html'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'dp', 'address')
        }),
        ('Employment Information', {
            'fields': ('employee_id', 'department', 'qualification', 'experience_years', 'faculties')
        }),
        ('Account Information', {
            'fields': ('user', 'is_first_login'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('joining_date',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('joining_date',)

    @admin.display(description='Faculties')
    def faculty_list(self, obj):
        return ', '.join(obj.faculties.values_list('name', flat=True)) or '-'
    
    def user_column(self, obj):
        """Display user linked to teacher"""
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
                name='teacher_import_csv',
            ),
            path(
                'download-csv-template/',
                self.admin_site.admin_view(self.download_csv_template),
                name='teacher_download_csv_template',
            ),
        ]
        return custom_urls + urls
    
    def import_csv(self, request):
        """Handle CSV import request"""
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            
            if not csv_file:
                messages.error(request, 'Please select a CSV file to import.')
                return render(request, 'admin/teacher_import.html', {'admin_site': self.admin_site})
            
            if not csv_file.name.lower().endswith('.csv'):
                messages.error(request, 'Only .csv files are supported.')
                return render(request, 'admin/teacher_import.html', {'admin_site': self.admin_site})
            
            # Import teachers from CSV
            created_users_data, updated_teachers_count, error_messages = import_teachers_from_csv(request, csv_file)
            
            # Display messages
            if error_messages:
                for error in error_messages:
                    messages.warning(request, error)
            
            if created_users_data:
                messages.success(
                    request,
                    f'Successfully created {len(created_users_data)} teacher account(s) '
                    f'and updated {updated_teachers_count} record(s).'
                )
                
                # Generate and download PDF with credentials
                pdf_buffer = generate_credentials_pdf(created_users_data)
                response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="teacher_credentials.pdf"'
                return response
            elif updated_teachers_count > 0:
                messages.success(request, f'Successfully updated {updated_teachers_count} teacher record(s).')
            else:
                messages.warning(request, 'No teachers were imported or updated.')
            
            return redirect('admin:teacher_teacher_changelist')
        
        # GET request - show import form
        return render(
            request,
            'admin/teacher_import.html',
            {
                'admin_site': self.admin_site,
                'title': 'Import Teachers from CSV',
                'has_change_permission': self.has_change_permission(request),
            }
        )
    
    def download_csv_template(self, request):
        """Download CSV template for teacher import"""
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

