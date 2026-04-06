from datetime import time

from django.db import migrations, models
import django.db.models.deletion


DEFAULT_SLOTS = [
    {'label': 'Period 1', 'start_time': time(7, 10), 'end_time': time(8, 45), 'is_break': False, 'display_order': 1},
    {'label': 'Period 2', 'start_time': time(8, 45), 'end_time': time(10, 15), 'is_break': False, 'display_order': 2},
    {'label': 'Break', 'start_time': time(10, 15), 'end_time': time(11, 0), 'is_break': True, 'display_order': 3},
    {'label': 'Period 3', 'start_time': time(11, 0), 'end_time': time(12, 30), 'is_break': False, 'display_order': 4},
    {'label': 'Period 4', 'start_time': time(12, 30), 'end_time': time(14, 0), 'is_break': False, 'display_order': 5},
]


def create_default_timeslots_and_map_existing_attendance(apps, schema_editor):
    TimeSlot = apps.get_model('attendance', 'TimeSlot')
    Attendance = apps.get_model('attendance', 'Attendance')

    slot_index = {}
    for slot_data in DEFAULT_SLOTS:
        slot, _ = TimeSlot.objects.get_or_create(
            start_time=slot_data['start_time'],
            end_time=slot_data['end_time'],
            defaults={
                'label': slot_data['label'],
                'is_break': slot_data['is_break'],
                'display_order': slot_data['display_order'],
            },
        )
        if not slot.label:
            slot.label = slot_data['label']
            slot.is_break = slot_data['is_break']
            slot.display_order = slot_data['display_order']
            slot.save(update_fields=['label', 'is_break', 'display_order'])
        slot_index[(slot.start_time, slot.end_time)] = slot.id

    for attendance in Attendance.objects.exclude(start_time__isnull=True).exclude(end_time__isnull=True):
        slot_id = slot_index.get((attendance.start_time, attendance.end_time))
        if slot_id:
            attendance.timeslot_id = slot_id
            attendance.save(update_fields=['timeslot'])


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_populate_day_of_week'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='', max_length=100)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_break', models.BooleanField(default=False)),
                ('display_order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['display_order', 'start_time', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='timeslot',
            constraint=models.UniqueConstraint(fields=('start_time', 'end_time'), name='unique_timeslot_time_range'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='timeslot',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendances', to='attendance.timeslot'),
        ),
        migrations.RunPython(create_default_timeslots_and_map_existing_attendance, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='attendance',
            name='unique_attendance_subject_faculty_year_date',
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.UniqueConstraint(condition=models.Q(('enrollment_batch__isnull', False), ('faculty__isnull', False), ('subject__isnull', False), ('timeslot__isnull', False)), fields=('subject', 'faculty', 'enrollment_batch', 'attendance_date', 'timeslot'), name='unique_attendance_subject_faculty_year_date_slot'),
        ),
    ]
