from django.contrib import admin

from .models import Attendance, AttendanceEntry, TimeSlot, WeeklyClassSchedule


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('label', 'start_time', 'end_time', 'is_break', 'display_order')
    list_filter = ('is_break',)
    ordering = ('display_order', 'start_time', 'id')


@admin.register(WeeklyClassSchedule)
class WeeklyClassScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'subject',
        'teacher',
        'faculty',
        'enrollment_batch',
        'day_of_week',
        'timeslot',
        'start_date',
        'end_date',
        'is_active',
    )
    list_filter = ('is_active', 'day_of_week', 'faculty', 'enrollment_batch', 'timeslot')
    search_fields = ('subject__name', 'teacher__name', 'faculty__name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'faculty', 'enrollment_batch', 'timeslot', 'attendance_date', 'created_at')
    search_fields = ('title', 'subject__name', 'teacher__name', 'faculty__name', 'enrollment_batch__year')
    list_filter = ('subject', 'teacher', 'faculty', 'enrollment_batch', 'timeslot', 'attendance_date', 'created_at')


@admin.register(AttendanceEntry)
class AttendanceEntryAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'student', 'status', 'marked_at')
    search_fields = ('attendance__title', 'student__name', 'student__roll_number')
    list_filter = ('status', 'attendance')
