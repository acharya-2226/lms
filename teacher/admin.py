from django.contrib import admin

from .models import Teacher


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
    )
    search_fields = ('name', 'employee_id', 'department', 'qualification', 'email', 'faculties__name')
    list_filter = ('department', 'qualification', 'faculties', 'joining_date')
    filter_horizontal = ('faculties',)

    @admin.display(description='Faculties')
    def faculty_list(self, obj):
        return ', '.join(obj.faculties.values_list('name', flat=True)) or '-'
