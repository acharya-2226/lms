from django.contrib.auth.models import AnonymousUser


def get_student_profile(user):
    if not user or isinstance(user, AnonymousUser):
        return None
    return getattr(user, 'student_profile', None)


def get_teacher_profile(user):
    if not user or isinstance(user, AnonymousUser):
        return None
    return getattr(user, 'teacher_profile', None)


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def get_logged_in_name(user):
    if not user or not user.is_authenticated:
        return ''

    student = get_student_profile(user)
    if student and student.name:
        return student.name.split()[0]

    teacher = get_teacher_profile(user)
    if teacher and teacher.name:
        return teacher.name.split()[0]

    if user.first_name:
        return user.first_name.split()[0]

    return user.username


def can_manage_academic_records(user):
    return bool(get_teacher_profile(user) or is_admin_user(user))
