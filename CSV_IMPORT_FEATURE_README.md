# CSV Import & First-Login Password Change Feature

## Overview
This document describes the new CSV import functionality and first-login password change system implemented for the LMS.

## Features Implemented

### 1. **CSV Import for Students and Teachers**
- Import students/teachers from CSV files via Django admin panel
- Automatic User account creation with hashed passwords
- Download CSV template for proper format
- PDF report generation with credentials

### 2. **Automatic User Account Creation**
- Each imported student/teacher gets a unique User account
- Username generated from email (e.g., john.doe@example.com → john_doe)
- Random 12-character password with uppercase, lowercase, digits, and special characters
- User linked to Student/Teacher profile via OneToOne relationship

### 3. **PDF Credentials Report**
- Generated immediately after import
- Contains: Name, Username, Email, Password, Type (Student/Teacher)
- Security warning on report about sharing passwords

### 4. **First-Login Password Change**
- New field `is_first_login` on Student and Teacher models
- Middleware redirects users to password change page on first login
- Users must change password before accessing other pages
- Password requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit

## File Structure

### New Files Created
```
student/
  ├── admin_actions.py          # CSV import functions and PDF generation
  ├── forms.py                  # FirstLoginPasswordChangeForm
  ├── middleware.py             # FirstLoginRedirectMiddleware
  ├── migrations/
  │   └── 0004_student_user_is_first_login.py

teacher/
  ├── admin_actions.py          # CSV import functions and PDF generation
  ├── forms.py                  # FirstLoginPasswordChangeForm
  └── migrations/
      └── 0003_teacher_user_is_first_login.py

LMS/templates/
  ├── admin/
  │   ├── student_import.html   # Student CSV import form
  │   └── teacher_import.html   # Teacher CSV import form
  ├── student/
  │   └── first_login_password_change.html
  └── teacher/
      └── first_login_password_change.html
```

### Modified Files
```
student/
  ├── models.py                 # Added User OneToOne field, is_first_login
  ├── admin.py                  # Added import actions to StudentAdmin
  ├── views.py                  # Added FirstLoginPasswordChangeView
  └── urls.py                   # Added first-login-change-password URL

teacher/
  ├── models.py                 # Added User OneToOne field, is_first_login
  ├── admin.py                  # Added import actions to TeacherAdmin
  ├── views.py                  # Added FirstLoginPasswordChangeView
  └── urls.py                   # Added first-login-change-password URL

LMS/
  ├── settings.py               # Added middleware and LOGIN_URL settings
```

## How to Use

### For Admins: Importing Students

1. **Access Admin Panel**
   - Go to `/admin/`
   - Login with admin credentials

2. **Navigate to Students**
   - Click on "Students" in the left sidebar

3. **Download CSV Template**
   - Click the "📥 Download CSV Template" button
   - Fill in the template with student data

4. **Import Students**
   - Click the "Import Students from CSV" button in the student list
   - Select the filled CSV file
   - Click "Import Students"
   - A PDF with credentials will be automatically downloaded

5. **CSV Format**
   ```
   Name,Roll Number,Enrollment Year,Faculty,Age,Email,Address
   John Doe,STU001,2024,Science,20,john@example.com,City
   Jane Smith,STU002,2024,Engineering,21,jane@example.com,City
   ```

### For Admins: Importing Teachers

Same process as students, but:
- Navigate to "Teachers" in left sidebar
- Use the teacher import button
- CSV format:
  ```
  Name,Employee ID,Department,Qualification,Experience Years,Faculties,Email,Address
  John Doe,EMP001,Science,MSc Physics,5,Science;IT,john@example.com,City
  ```

### For Students/Teachers: First Login

1. **Receive Credentials**
   - Admin provides username and password from PDF report

2. **First Login**
   - Go to `/admin/login/`
   - Enter username and password
   - System redirects to password change page

3. **Change Password**
   - Enter current password (provided temporary password)
   - Enter new password (8+ chars, uppercase, lowercase, digit)
   - Confirm new password
   - Click "Update Password"
   - Redirected to login page

4. **Subsequent Logins**
   - Login with new password
   - No redirect to password change page

## Database Schema Changes

### Student Model
```python
user = OneToOneField(User, null=True, blank=True, related_name='student_profile')
is_first_login = BooleanField(default=True)
```

### Teacher Model
```python
user = OneToOneField(User, null=True, blank=True, related_name='teacher_profile')
is_first_login = BooleanField(default=True)
```

## Security Features

1. **Password Security**
   - Passwords hashed using Django's password hashing
   - No plaintext passwords stored
   - Strong password requirements enforced

2. **First-Login Enforcement**
   - Middleware redirects users to change password
   - Excluded paths prevent redirect loops
   - User cannot access other pages until password changed

3. **PDF Security Warning**
   - Strong warning on credentials PDF about secure transmission
   - Recommendation to share through secure channels

## Middleware Configuration

The middleware is registered in `settings.py`:
```python
MIDDLEWARE = [
    ...
    'student.middleware.FirstLoginRedirectMiddleware',
]
```

**Excluded Paths:**
- `/admin` - Admin pages
- `/students/change-password/` - Student password change
- `/teachers/change-password/` - Teacher password change
- `/logout` - Logout
- `/api/` - API endpoints
- `/static/` - Static files
- `/media/` - Media files

## Error Handling

### CSV Import Errors
- Invalid CSV format
- Missing required fields (Name, Email)
- Duplicate emails
- Invalid enrollment year/experience years
- Row-by-row error reporting

### Password Change Errors
- Incorrect old password
- Password too short
- Missing uppercase/lowercase/digit
- Passwords don't match
- Specific validation feedback

## Migration Steps

1. **Backup Database**
   ```bash
   cp db.sqlite3 db.sqlite3.backup
   ```

2. **Apply Migrations**
   ```bash
   python manage.py migrate student
   python manage.py migrate teacher
   ```

3. **Restart Server**
   ```bash
   python manage.py runserver
   ```

## Testing the Feature

### Test CSV Import
1. Create test CSV file with student/teacher data
2. Use admin import functionality
3. Verify PDF is generated with correct credentials
4. Check database for User records linked to Student/Teacher

### Test First-Login Redirect
1. Import a test student
2. Login with provided credentials
3. Verify redirect to password change page
4. Change password and verify it works
5. Logout and login with new password
6. Verify no redirect this time

## Troubleshooting

### "Only .csv files are supported"
- Ensure file extension is `.csv`
- Not `.xlsx` or other formats

### "CSV file is empty or has invalid format"
- Verify CSV has header row
- Check column names match template exactly

### Middleware not redirecting
- Ensure middleware is added to `MIDDLEWARE` list in settings
- Check excluded paths configuration
- Verify user has is_first_login=True

### Password change form not displaying
- Check templates directory exists
- Verify template path correct
- Check DEBUG=True if not seeing error

## Dependencies

Required packages (already in project):
- Django 6.0.3
- reportlab (for PDF generation)
- openpyxl (for Excel templates)

## Future Enhancements

- Bulk email credentials instead of PDF download
- Password expiration policies
- Login attempt tracking
- Two-factor authentication
- Import from Excel files (.xlsx)
- Export user lists with hashed passwords
