from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_attendance_unique_attendance_subject_faculty_year_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='day_of_week',
            field=models.CharField(blank=True, choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], default='', max_length=15),
        ),
        migrations.AddField(
            model_name='attendance',
            name='start_time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='end_time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
    ]
