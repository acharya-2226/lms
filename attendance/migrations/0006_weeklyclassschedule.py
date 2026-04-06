from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_timeslot_and_attendance_timeslot_fk'),
        ('student', '0004_subject'),
        ('teacher', '0002_teacher_faculties'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeklyClassSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=200)),
                ('day_of_week', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=15)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, default=None, null=True)),
                ('note', models.TextField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('enrollment_batch', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weekly_schedules', to='student.enrollmentyear')),
                ('faculty', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weekly_schedules', to='student.faculty')),
                ('subject', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weekly_schedules', to='student.subject')),
                ('teacher', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weekly_schedules', to='teacher.teacher')),
                ('timeslot', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weekly_schedules', to='attendance.timeslot')),
            ],
            options={
                'ordering': ['faculty__name', 'enrollment_batch__year', 'day_of_week', 'timeslot__display_order', 'timeslot__start_time'],
            },
        ),
        migrations.AddConstraint(
            model_name='weeklyclassschedule',
            constraint=models.UniqueConstraint(condition=models.Q(('enrollment_batch__isnull', False), ('faculty__isnull', False), ('subject__isnull', False), ('timeslot__isnull', False)), fields=('subject', 'faculty', 'enrollment_batch', 'day_of_week', 'timeslot'), name='unique_weekly_schedule_subject_faculty_year_day_slot'),
        ),
    ]
