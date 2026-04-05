from django.contrib import admin

from .models import Attendance, AttendanceEntry


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'faculty', 'enrollment_batch', 'attendance_date', 'created_at')
    search_fields = ('title', 'subject__name', 'teacher__name', 'faculty__name', 'enrollment_batch__year')
    list_filter = ('subject', 'teacher', 'faculty', 'enrollment_batch', 'attendance_date', 'created_at')


@admin.register(AttendanceEntry)
class AttendanceEntryAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'student', 'status', 'marked_at')
    search_fields = ('attendance__title', 'student__name', 'student__roll_number')
    list_filter = ('status', 'attendance')
