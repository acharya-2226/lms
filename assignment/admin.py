from django.contrib import admin

from .models import Assignment, AssignmentRecipient


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'faculty', 'enrollment_batch', 'due_date', 'created_at')
    search_fields = ('title', 'subject__name', 'faculty__name', 'enrollment_batch__year', 'teacher__name')
    list_filter = ('subject', 'teacher', 'faculty', 'enrollment_batch', 'due_date', 'created_at')


@admin.register(AssignmentRecipient)
class AssignmentRecipientAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'is_notified', 'is_seen', 'is_submitted', 'notified_at', 'seen_at', 'submitted_at')
    search_fields = ('assignment__title', 'student__name', 'student__roll_number')
    list_filter = ('is_notified', 'is_seen', 'is_submitted', 'assignment')
