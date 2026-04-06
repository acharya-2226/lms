from LMS.roles import (
    can_manage_academic_records,
    get_logged_in_name,
    get_student_profile,
    get_teacher_profile,
    is_admin_user,
)


def role_flags(request):
    user = request.user
    student_profile = get_student_profile(user)
    teacher_profile = get_teacher_profile(user)
    admin_user = is_admin_user(user)

    return {
        'has_student_profile': bool(student_profile),
        'has_teacher_profile': bool(teacher_profile),
        'is_admin': admin_user,
        'logged_in_name': get_logged_in_name(user),
        'current_student': student_profile,
        'current_teacher': teacher_profile,
        'can_manage_academic_records': can_manage_academic_records(user),
        'is_student_user': bool(student_profile),
        'is_teacher_user': bool(teacher_profile),
        'is_admin_like_user': admin_user,
        'current_user_display_name': get_logged_in_name(user),
    }
