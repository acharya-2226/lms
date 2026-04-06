from django.db import migrations


def populate_day_of_week(apps, schema_editor):
    Attendance = apps.get_model('attendance', 'Attendance')
    for attendance in Attendance.objects.all():
        if attendance.attendance_date:
            attendance.day_of_week = attendance.attendance_date.strftime('%A').lower()
            attendance.save(update_fields=['day_of_week'])


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_attendance_timeslot_fields'),
    ]

    operations = [
        migrations.RunPython(populate_day_of_week, migrations.RunPython.noop),
    ]
