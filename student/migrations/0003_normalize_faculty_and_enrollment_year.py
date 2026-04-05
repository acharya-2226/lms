from django.db import migrations, models


def forward_normalize_student_categories(apps, schema_editor):
    Student = apps.get_model('student', 'Student')
    Faculty = apps.get_model('student', 'Faculty')
    EnrollmentYear = apps.get_model('student', 'EnrollmentYear')

    for student in Student.objects.all():
        faculty_obj = None
        year_obj = None

        faculty_value = (student.faculty or '').strip() if isinstance(student.faculty, str) else ''
        year_value = (student.enrollment_batch or '').strip() if isinstance(student.enrollment_batch, str) else ''

        if faculty_value:
            # Case-insensitive lookup
            faculty_obj = Faculty.objects.filter(name__iexact=faculty_value).first()
            if not faculty_obj:
                faculty_obj = Faculty.objects.create(name=faculty_value.strip())

        if year_value:
            try:
                year_int = int(year_value)
            except (TypeError, ValueError):
                year_int = None

            if year_int is not None:
                year_obj, _ = EnrollmentYear.objects.get_or_create(year=year_int)

        student.faculty_fk = faculty_obj
        student.enrollment_batch_fk = year_obj
        student.save(update_fields=['faculty_fk', 'enrollment_batch_fk'])


def backward_noop(apps, schema_editor):
    # No backward data transform needed for this baseline migration.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_student_enrollment_batch_student_faculty_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EnrollmentYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='enrollment_batch_fk',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=models.SET_NULL, related_name='students', to='student.enrollmentyear'),
        ),
        migrations.AddField(
            model_name='student',
            name='faculty_fk',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=models.SET_NULL, related_name='students', to='student.faculty'),
        ),
        migrations.RunPython(forward_normalize_student_categories, backward_noop),
        migrations.RemoveField(
            model_name='student',
            name='enrollment_batch',
        ),
        migrations.RemoveField(
            model_name='student',
            name='faculty',
        ),
        migrations.RenameField(
            model_name='student',
            old_name='enrollment_batch_fk',
            new_name='enrollment_batch',
        ),
        migrations.RenameField(
            model_name='student',
            old_name='faculty_fk',
            new_name='faculty',
        ),
    ]
