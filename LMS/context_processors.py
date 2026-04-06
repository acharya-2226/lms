def role_flags(request):
    user = request.user
    is_authenticated = bool(user and user.is_authenticated)
    is_student = is_authenticated and hasattr(user, 'student_profile')
    is_teacher = is_authenticated and hasattr(user, 'teacher_profile')
    is_admin_like = is_authenticated and (user.is_staff or user.is_superuser)

    display_name = ''
    if is_authenticated:
        profile_name = ''
        if is_student:
            profile_name = (user.student_profile.name or '').strip()
        elif is_teacher:
            profile_name = (user.teacher_profile.name or '').strip()
        if profile_name:
            display_name = profile_name.split()[0]
        elif (user.first_name or '').strip():
            display_name = user.first_name.strip().split()[0]
        else:
            display_name = user.username

    return {
        'is_student_user': is_student,
        'is_teacher_user': is_teacher,
        'is_admin_like_user': is_admin_like,
        'can_manage_academic_records': is_teacher or is_admin_like,
        'current_user_display_name': display_name,
    }
