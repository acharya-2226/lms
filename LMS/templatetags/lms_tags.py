from django import template
from django.utils.html import format_html

from LMS.roles import can_manage_academic_records, get_logged_in_name, get_student_profile, get_teacher_profile, is_admin_user

register = template.Library()


@register.simple_tag(takes_context=True)
def role_nav(context):
    request = context['request']
    user = request.user
    if not user.is_authenticated:
        return format_html(
            '<a class="nav-link" href="{}">Login</a>',
            '/login/',
        )

    links = [
        ('Home', '/'),
        ('Assignments', '/assignments/'),
        ('Attendance', '/attendances/'),
    ]

    if is_admin_user(user):
        links.insert(1, ('Students', '/students/'))
        links.insert(2, ('Teachers', '/teachers/'))
    else:
        student = get_student_profile(user)
        teacher = get_teacher_profile(user)
        if teacher:
            links.insert(1, ('Students', '/students/'))
        if student:
            links = [('Home', '/'), ('Assignments', '/assignments/'), ('Attendance', '/attendances/')]

    return format_html(
        ''.join('<a class="nav-link" href="{}">{}</a>'.format(url, label) for label, url in links)
    )


@register.simple_tag
def status_badge(status):
    value = status.lower() if isinstance(status, str) else status
    mapping = {
        'present': ('success', 'Present'),
        'absent': ('danger', 'Absent'),
        'unmarked': ('secondary', 'Unmarked'),
        'pending': ('warning', 'Pending'),
        'submitted': ('success', 'Submitted'),
        'resubmitted': ('info', 'Resubmitted'),
        True: ('warning', 'Temporary Password'),
        False: ('success', 'Active'),
    }
    badge, label = mapping.get(value, ('secondary', str(status).title() if status is not None else '-'))
    return format_html('<span class="badge text-bg-{}">{}</span>', badge, label)


@register.simple_tag(takes_context=True)
def can_edit(context, obj):
    request = context['request']
    user = request.user
    if is_admin_user(user):
        return True
    teacher = get_teacher_profile(user)
    if teacher and hasattr(obj, 'teacher_id'):
        return getattr(obj, 'teacher_id', None) == teacher.id
    return False
