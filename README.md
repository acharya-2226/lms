# LMS

Learning and Education Management System built with Django.

## Overview

This project manages academic records for students, teachers, assignments, and attendance. It includes role-based access control, frontend login, first-login password change, CSV-based bulk import, PDF credential export, assignment submission, attendance timetables, and compact table-based record views.

## Core Access Model

| Role | What they can do |
| --- | --- |
| Student | View their own assignments, submissions, attendance, timetable, and profile data that is permitted for their account. |
| Teacher | View assigned classes, attendance, timetables, assignment rosters, and manage academic records for their scope. |
| Admin / Staff | Full access to CRUD screens, imports, reports, and management views. |

## Feature Catalog

| Module | Feature | Procedure |
| --- | --- | --- |
| Authentication | Frontend login page | Open `/login/`, enter username and password, then the app redirects to the appropriate portal. |
| Authentication | Logout | Use the Logout button in the header/footer to end the session and return to login. |
| Authentication | First-login password change | Temporary users are redirected to the change-password page on first login, must enter old password, new password, and confirmation, then log in again. |
| Authentication | Access denied screen | When a user opens a blocked module, the app shows a custom Access Denied screen with portal links instead of a raw error. |
| Global UI | Logged-in identity | The header shows `Logged in as {name}` using the first word of the linked student or teacher name. |
| Global UI | Portal navigation | The base layout keeps portal links visible so users can choose Students, Teachers, Assignments, or Attendance when permitted. |
| UI | Compact tables | Record tables use wrapped, denser cells so long names and text stay readable in a compact layout. |
| Student module | Student CRUD | Admin/teacher-level users can create, update, view, and delete student profiles through standard Django views. |
| Student module | Grouped and flat list views | The student list can be viewed grouped by faculty and enrollment year, with a collapsible show/hide control per group. |
| Student module | Student detail page | Opens a single student profile with profile data and related information. |
| Student module | Student import template download | Download the XLSX template before importing students. |
| Student module | Student XLSX import | Upload the prepared spreadsheet to bulk-create or update students. |
| Student module | Student portal login account creation | Imported students get linked Django user accounts, hashed passwords, and first-login enforcement. |
| Student module | First-login password reset | The student must change the temporary password before continuing to protected pages. |
| Teacher module | Teacher CRUD | Admin/teacher-level users can create, update, view, and delete teacher profiles. |
| Teacher module | Grouped and flat list views | Teacher records can be grouped by faculty, with collapsible sections. |
| Teacher module | Teacher detail page | Opens a single teacher profile with contact and academic information. |
| Teacher module | Teacher import template download | Download the XLSX template before importing teachers. |
| Teacher module | Teacher XLSX import | Upload the prepared spreadsheet to bulk-create or update teachers. |
| Teacher module | Teacher portal login account creation | Imported teachers get linked Django user accounts, hashed passwords, and first-login enforcement. |
| Teacher module | First-login password reset | The teacher must change the temporary password before continuing to protected pages. |
| Assignment module | Assignment CRUD | Teachers and admins can create, update, view, and delete assignments for a faculty and enrollment year. |
| Assignment module | Assignment list | Students see only assignments assigned to them; teachers see assigned classes; admins see all. |
| Assignment module | Assignment detail | Shows assignment description, subject, teacher, faculty, year, file attachment, and due date. |
| Assignment module | Assignment roster | Teachers/admins can open the roster to see all recipients and notification/submission status. |
| Assignment module | Assignment submission | Students open an assignment, upload a submission file, and resubmit if needed. |
| Assignment module | Submission status tracking | The list and detail pages show whether the current student submission is pending, submitted, or resubmitted. |
| Attendance module | Attendance CRUD | Teachers and admins can create, update, view, and delete attendance sessions. |
| Attendance module | Attendance list | Students see their own attendance sessions; teachers see their assigned scope; admins see all. |
| Attendance module | Attendance detail | Shows note, date, timeslot, and record metadata. |
| Attendance module | Attendance roster | Teachers/admins can mark students present, absent, or unmarked. |
| Attendance module | Attendance report | Users can generate an attendance report for an allowed subject and date range. |
| Attendance module | Attendance report download | Reports can be downloaded as XLSX or PDF. |
| Attendance module | Attendance timetable | A timetable view groups sessions by weekday and displays timeslots for assigned classes. |
| Attendance module | Attendance timeslots | Each attendance session stores start time, end time, and weekday for timetable-style display. |
| Reporting | PDF credentials report | Bulk imports generate a PDF listing usernames and temporary passwords. |
| Reporting | CSV/XLSX templates | Admins can download a template before importing student or teacher data. |
| Role enforcement | Student restrictions | Student accounts cannot access student/teacher management pages, edit buttons, or admin-only record controls. |
| Role enforcement | Teacher restrictions | Teachers can manage only their allowed academic scope and assigned records. |
| Role enforcement | Login required | Protected views require authentication, and unauthenticated users are redirected to the frontend login page. |

## Processing Flow

### 1. Frontend Login

1. Open `/login/`.
2. Enter your LMS username and password.
3. If this is your first login, the app redirects you to the password change page.
4. After changing the password, log in again using the new password.
5. The session then loads the portal that matches your role.

### 2. Student Import Workflow

1. Go to the Students section in the admin panel.
2. Download the import template.
3. Fill the spreadsheet with student data.
4. Upload the XLSX file.
5. The system validates rows, creates or updates students, creates linked user accounts, and generates hashed passwords.
6. A PDF credential report is downloaded for the admin.
7. Students log in with temporary credentials and are forced to change their password on first use.

### 3. Teacher Import Workflow

1. Go to the Teachers section in the admin panel.
2. Download the teacher import template.
3. Fill the spreadsheet with teacher data and faculty names.
4. Upload the XLSX file.
5. The system validates rows, creates or updates teachers, creates linked user accounts, and generates hashed passwords.
6. A PDF credential report is downloaded for the admin.
7. Teachers log in with temporary credentials and are forced to change their password on first use.

### 4. Assignment Workflow

1. A teacher or admin creates an assignment for a subject, faculty, and enrollment year.
2. The app seeds assignment recipients from matching students.
3. Students see only their assigned assignments.
4. A student opens the assignment detail page and uploads a submission file.
5. The submission status updates to submitted.
6. The student can resubmit if needed.
7. Teachers can open the roster to review notification and submission progress.

### 5. Attendance Workflow

1. A teacher or admin creates an attendance session for a subject, faculty, year, date, and timeslot.
2. The app seeds attendance entries for matching students.
3. The teacher opens the roster and marks each student present, absent, or unmarked.
4. Students can only see attendance records that include them.
5. The timetable view groups attendance sessions by weekday and time.
6. Reports can be exported in PDF or XLSX format.

## Data Model Highlights

| Model | Key fields |
| --- | --- |
| Student | User link, name, roll number, enrollment year, faculty, age, email, address, first-login flag. |
| Teacher | User link, name, employee ID, department, qualification, experience, faculties, email, address, first-login flag. |
| Assignment | Title, description, subject, faculty, enrollment year, teacher, attachment, due date. |
| AssignmentRecipient | Notification status, seen status, submission status, submission file. |
| Attendance | Subject, faculty, enrollment year, teacher, attendance date, weekday, start time, end time, note. |
| AttendanceEntry | Student, attendance, status, marked timestamp. |

## URLs and Main Screens

| Screen | Path |
| --- | --- |
| Frontend login | `/login/` |
| Frontend logout | `/logout/` |
| Home | `/` |
| Students portal | `/students/` |
| Teachers portal | `/teachers/` |
| Assignments portal | `/assignments/` |
| Attendance portal | `/attendances/` |
| Attendance timetable | `/attendances/timetable/` |
| Attendance report | `/attendances/report/` |
| Student import template | admin student import screen |
| Teacher import template | admin teacher import screen |

## Notes

- Imported credentials are stored securely using Django password hashing.
- Blocked users are shown a custom Access Denied page with navigation options.
- The timetable and compact table views are designed to make dense academic data easier to scan.
- Student and teacher list views still remain visible as portals, but restricted actions are filtered by role.

## Windows App Launcher (Non-Technical Use)

This project now includes a desktop launcher that can start LMS like an app.

### What was added

- `lms_launcher.py`: GUI launcher that starts Django, runs migrations, and opens LMS in a browser.
- `build_lms_launcher.bat`: one-click build script to generate the `.exe`.
- `dist/LMS-Launcher.exe`: built desktop executable (created by PyInstaller).
- `install_app.bat`: one-time installer for environment, dependencies, and migrations.
- `launch_app.bat`: fast launcher that only runs the app.
- `requirements_runtime.txt`: runtime package list used by installer.
- `lms_desktop_app.py`: desktop window app that embeds LMS (no external browser needed).
- `build_lms_desktop_app.bat`: build script for desktop app EXE.

### Segment 1: Install App (run once)

1. Double-click `install_app.bat`.
2. It creates `env` if needed.
3. It installs required dependencies from `requirements_runtime.txt`.
4. It runs database migrations.

### Segment 2: Launch App (daily use)

1. Double-click `launch_app.bat`.
2. It starts the server and opens LMS in a desktop app window (embedded webview).
3. No dependency installation or migration checks run during launch.

### Build Desktop EXE (optional)

1. Run `build_lms_desktop_app.bat`.
2. It reads version from `APP_VERSION.txt`.
3. It produces:
	- `dist/LMS-Desktop-v<version>.exe` (versioned release)
	- `dist/LMS-Desktop-latest.exe` (stable latest alias)

### App Version Naming Convention

- Version file: `APP_VERSION.txt`
- Format: `major.minor.patch` (example: `2.0.0`)
- Release artifact: `LMS-Desktop-v<major.minor.patch>.exe`
- Convenience alias for users: `LMS-Desktop-latest.exe`

### How end users can run LMS

1. First run `install_app.bat` once.
2. For normal usage, run `launch_app.bat` or `LMS-Launcher.exe`.
3. The app opens at `http://127.0.0.1:8000/`.

### Rebuild the EXE (for developers)

1. Double-click `build_lms_launcher.bat`.
2. It installs/updates PyInstaller and rebuilds `dist/LMS-Launcher.exe`.

### Important packaging note

- This EXE is a launcher for this project, not a fully standalone packaged backend.
- It expects the LMS source folder and virtual environment to exist locally.
