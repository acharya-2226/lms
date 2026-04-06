# Session Focus Guide

This file is the default handoff for future coding sessions.
Follow it unless the user gives a direct override.

## Current Priority (Web App First)

Focus on core LMS web functionality only:
- Student, Teacher, Assignment, Attendance flows in browser.
- Role-based access and visibility fixes.
- Report generation and download correctness.
- Data/model/view/template consistency.
- Basic QA and bug fixing in existing modules.

## Explicitly Out of Scope For Now

Do NOT work on desktop app packaging or launcher UX in normal sessions.
Do NOT refactor build/distribution unless the user explicitly asks.

## Do Not Touch (Without Explicit User Request)

- `lms_desktop_app.py`
- `lms_launcher.py`
- `build_lms_desktop_app.bat`
- `build_lms_launcher.bat`
- `install_app.bat`
- `launch_app.bat`
- `APP_VERSION.txt`
- `dist/` (all generated executables)
- `build/` and generated `.spec` files

## Safe Focus Areas

- `student/`
- `teacher/`
- `assignment/`
- `attendance/`
- `LMS/templates/`
- `LMS/views.py`, `LMS/urls.py`, `LMS/context_processors.py`

## Working Rules

- Prefer minimal, targeted fixes.
- Keep URL names and role checks consistent.
- Avoid editing unrelated files in the same commit.
- If a change may affect auth/permissions, validate with `manage.py check`.
- If touching reports/downloads, test both PDF and XLSX paths.

## Exception Rule

If the user explicitly asks for desktop app/exe/packaging work, this guide is temporarily overridden for that task.
