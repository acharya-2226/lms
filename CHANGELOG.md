# Changelog

## v1.1.0 - 2026-04-06

### Security and Environment
- Replaced hardcoded security settings with environment-driven configuration.
- Added production-secure defaults for SSL redirect, secure cookies, and HSTS.
- Added structured logging with request correlation IDs.
- Added `/health/` endpoint.

### UX and Navigation
- Implemented role-aware top navigation with module visibility by user role.
- Reworked home page into role-based dashboard cards.
- Improved access-denied and custom error pages for 400/404/500.

### Import and Upload Safety
- Added upload validation for extension, MIME type, and max file size.
- Added filename sanitization for assignment submission uploads.
- Applied upload safety checks to student, teacher, and subject XLSX import views.

### Scalability and Performance
- Added list view filtering and pagination for students, teachers, subjects, assignments, and attendance.
- Added attendance report date-range guardrails.
- Added database indexes for frequent role/filter/report query paths.

### Testing and CI
- Added baseline automated tests for auth redirects, first-login flows, pagination, report guardrails, and upload safety.
- Added GitHub Actions CI workflow with lint, migration drift checks, Django checks, and tests.

### Documentation
- Added `.env.example` and dependency pinning in `requirements.txt`.
- Updated README with environment setup, role matrix, import matching strategy, troubleshooting, and backup/restore runbook.
