from django.contrib import admin
from .models import EnrollmentYear, Faculty, Student
# Register your models here.


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(EnrollmentYear)
class EnrollmentYearAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'enrollment_batch', 'faculty', 'age', 'email', 'enrollment_date')
    search_fields = ('name', 'roll_number', '=enrollment_batch__year', 'faculty__name', 'email')
    list_filter = ('enrollment_batch', 'faculty', 'age', 'enrollment_date')