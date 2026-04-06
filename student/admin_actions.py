import csv
import io
import random
import string
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.text import slugify
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.http import HttpResponse
from .models import Student, Faculty, EnrollmentYear


def generate_random_password(length=12):
    """Generate a random password with uppercase, lowercase, digits, and special chars."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def generate_username_from_email(email):
    """Generate unique username from email."""
    base_username = email.split('@')[0]
    base_username = slugify(base_username).replace('-', '_')
    
    # Check if username exists, if so, append a number
    counter = 1
    username = base_username
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username


def generate_csv_template(request):
    """Generate a CSV template for student import."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_import_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Roll Number', 'Enrollment Year', 'Faculty', 'Age', 'Email', 'Address'])
    writer.writerow(['Ex: John Doe', 'EX001', '2024', 'Science', '20', 'john@example.com', 'City, Country'])
    
    return response


def import_students_from_csv(request, file_obj):
    """
    Import students from CSV file, create User accounts with hashed passwords,
    and return a PDF with credentials.
    
    Returns: (created_users_data, updated_students_count, error_messages)
    """
    created_users_data = []
    updated_students = 0
    error_messages = []
    
    try:
        # Read CSV file
        file_obj.seek(0)
        csv_file = io.TextIOWrapper(file_obj, encoding='utf-8')
        csv_reader = csv.DictReader(csv_file)
        
        if not csv_reader.fieldnames:
            raise ValueError("CSV file is empty or has invalid format")
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Extract and validate data
                name = (row.get('Name', '') or '').strip()
                roll_number = (row.get('Roll Number', '') or '').strip() or None
                enrollment_year_str = (row.get('Enrollment Year', '') or '').strip()
                faculty_name = (row.get('Faculty', '') or '').strip() or None
                age_str = (row.get('Age', '') or '').strip()
                email = (row.get('Email', '') or '').strip() or None
                address = (row.get('Address', '') or '').strip() or None
                
                # Validate required fields
                if not name:
                    error_messages.append(f"Row {row_num}: Name is required")
                    continue
                
                if not email:
                    error_messages.append(f"Row {row_num}: Email is required for user creation")
                    continue
                
                # Validate email uniqueness
                if Student.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
                    error_messages.append(f"Row {row_num}: Email {email} already exists")
                    continue
                
                # Process enrollment year
                enrollment_batch = None
                if enrollment_year_str:
                    try:
                        year_value = int(enrollment_year_str)
                        enrollment_batch, _ = EnrollmentYear.objects.get_or_create(year=year_value)
                    except ValueError:
                        error_messages.append(f"Row {row_num}: Invalid enrollment year '{enrollment_year_str}'")
                        continue
                
                # Process faculty
                faculty = None
                if faculty_name:
                    faculty, _ = Faculty.objects.get_or_create_case_insensitive(faculty_name)
                
                # Process age
                age = None
                if age_str:
                    try:
                        age = int(age_str)
                    except ValueError:
                        error_messages.append(f"Row {row_num}: Invalid age '{age_str}'")
                        continue
                
                # Generate credentials
                username = generate_username_from_email(email)
                password = generate_random_password()
                
                # Create or update Student
                student, created = Student.objects.get_or_create(
                    email=email,
                    defaults={
                        'name': name,
                        'roll_number': roll_number,
                        'enrollment_batch': enrollment_batch,
                        'faculty': faculty,
                        'age': age,
                        'address': address,
                        'is_first_login': True,
                    }
                )
                
                if created:
                    # Create User account
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=name.split()[0],
                        last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                    )
                    
                    # Link User to Student
                    student.user = user
                    student.is_first_login = True
                    student.save()
                    
                    created_users_data.append({
                        'name': name,
                        'username': username,
                        'email': email,
                        'password': password,
                        'roll_number': roll_number,
                        'type': 'Student',
                    })
                else:
                    # Update existing student
                    student.name = name
                    if roll_number:
                        student.roll_number = roll_number
                    if enrollment_batch:
                        student.enrollment_batch = enrollment_batch
                    if faculty:
                        student.faculty = faculty
                    if age:
                        student.age = age
                    if address:
                        student.address = address
                    student.save()
                    updated_students += 1
                    error_messages.append(f"Row {row_num}: Student with email {email} already existed, data updated")
            
            except Exception as e:
                error_messages.append(f"Row {row_num}: {str(e)}")
                continue
    
    except Exception as e:
        error_messages.append(f"CSV parsing error: {str(e)}")
    
    return created_users_data, updated_students, error_messages


def generate_credentials_pdf(created_users_data):
    """Generate a PDF file with usernames and passwords."""
    # Create PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        alignment=1,  # center
    )
    
    # Title
    title = Paragraph(f"<b>User Credentials Report</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add generation date
    date_paragraph = Paragraph(
        f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles['Normal']
    )
    elements.append(date_paragraph)
    elements.append(Spacer(1, 0.2*inch))
    
    # Create table data
    table_data = [['Name', 'Username', 'Email', 'Password', 'Type']]
    for user_data in created_users_data:
        table_data.append([
            user_data['name'],
            user_data['username'],
            user_data['email'],
            user_data['password'],
            user_data['type'],
        ])
    
    # Create table
    table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1.8*inch, 1.2*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    
    elements.append(table)
    
    # Add warning note
    elements.append(Spacer(1, 0.3*inch))
    warning = Paragraph(
        "<b>⚠️ Important:</b> Keep this document secure. Share passwords with users through secure channels. "
        "Users should change their passwords on first login.",
        styles['Normal']
    )
    elements.append(warning)
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    return pdf_buffer
