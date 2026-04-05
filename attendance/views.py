from io import BytesIO
from datetime import timedelta

from django.contrib import messages
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from student.models import Student, Subject

from .models import Attendance, AttendanceEntry


def seed_attendance_entries(attendance):
    if not attendance.faculty or not attendance.enrollment_batch:
        return

    students = Student.objects.filter(
        faculty=attendance.faculty,
        enrollment_batch=attendance.enrollment_batch,
    )
    for student in students:
        AttendanceEntry.objects.get_or_create(
            attendance=attendance,
            student=student,
        )


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['subject', 'teacher', 'faculty', 'enrollment_batch', 'attendance_date', 'note']
        widgets = {
            'attendance_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        faculty = cleaned_data.get('faculty')
        enrollment_batch = cleaned_data.get('enrollment_batch')
        attendance_date = cleaned_data.get('attendance_date')

        if subject and faculty and enrollment_batch and attendance_date:
            duplicate_exists = Attendance.objects.filter(
                subject=subject,
                faculty=faculty,
                enrollment_batch=enrollment_batch,
                attendance_date=attendance_date,
            )
            if self.instance.pk:
                duplicate_exists = duplicate_exists.exclude(pk=self.instance.pk)

            if duplicate_exists.exists():
                raise forms.ValidationError(
                    'An attendance record for this subject, faculty, enrollment year, and date already exists.'
                )

        return cleaned_data


class AttendanceReportForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.order_by('name'))
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class AttendanceListView(ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'


class AttendanceDetailView(DetailView):
    model = Attendance
    template_name = 'attendance/attendance_detail.html'
    context_object_name = 'attendance'
    queryset = Attendance.objects.all()


class AttendanceRosterView(DetailView):
    model = Attendance
    template_name = 'attendance/attendance_roster.html'
    context_object_name = 'attendance'
    queryset = Attendance.objects.select_related('subject', 'teacher', 'faculty', 'enrollment_batch').all()

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.ensure_entries_exist()
        if request.method == 'POST':
            return self.handle_post(request)
        return super().dispatch(request, *args, **kwargs)

    def ensure_entries_exist(self):
        seed_attendance_entries(self.object)

    def handle_post(self, request):
        updated_count = 0
        for entry in self.object.entries.all():
            status = request.POST.get(f'status_{entry.pk}')
            if status not in {'present', 'absent', 'unmarked'}:
                continue

            new_marked_at = timezone.now() if status != 'unmarked' else None
            if entry.status != status or entry.marked_at != new_marked_at:
                entry.status = status
                entry.marked_at = new_marked_at
                entry.save(update_fields=['status', 'marked_at'])
                updated_count += 1

        if updated_count:
            messages.success(
                self.request,
                f"Attendance saved for {updated_count} student{'s' if updated_count != 1 else ''}.",
            )
        else:
            messages.info(self.request, 'No attendance changes to save.')
        return redirect('attendance:attendance-roster', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entries'] = self.object.entries.select_related('student').order_by('student__name')
        context['matching_students'] = Student.objects.filter(
            faculty=self.object.faculty,
            enrollment_batch=self.object.enrollment_batch,
        ).order_by('name') if self.object.faculty and self.object.enrollment_batch else Student.objects.none()
        return context


class AttendanceCreateView(CreateView):
    model = Attendance
    template_name = 'attendance/attendance_form.html'
    form_class = AttendanceForm

    def form_valid(self, form):
        self.object = form.save()
        seed_attendance_entries(self.object)
        messages.success(self.request, 'Attendance created successfully.')
        return redirect('attendance:attendance-roster', pk=self.object.pk)


class AttendanceUpdateView(UpdateView):
    model = Attendance
    template_name = 'attendance/attendance_form.html'
    form_class = AttendanceForm
    success_url = reverse_lazy('attendance:attendance-list')


class AttendanceDeleteView(DeleteView):
    model = Attendance
    template_name = 'attendance/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:attendance-list')


class AttendanceReportView(View):
    template_name = 'attendance/attendance_report.html'

    def get(self, request):
        form = AttendanceReportForm(request.GET or None)
        return render(request, self.template_name, {'form': form})


class AttendanceReportDownloadView(View):
    def post(self, request):
        form = AttendanceReportForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Please choose a valid subject and date range.')
            return redirect('attendance:attendance-report')

        subject = form.cleaned_data['subject']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        report_format = request.POST.get('format', 'xlsx')

        if start_date > end_date:
            messages.error(request, 'Start date cannot be after end date.')
            return redirect('attendance:attendance-report')

        report_dates = self._build_date_list(start_date, end_date)
        report_rows = self._build_matrix(subject, start_date, end_date, report_dates)
        title_text = f'{subject.name} Attendance Report {start_date} - {end_date}'
        filename_base = f'attendance_report_{subject.name}_{start_date}_to_{end_date}'.replace(' ', '_')

        if report_format == 'pdf':
            return self._build_pdf_response(filename_base, title_text, report_dates, report_rows)
        return self._build_xlsx_response(filename_base, title_text, report_dates, report_rows)

    def _build_date_list(self, start_date, end_date):
        report_dates = []
        current_date = start_date
        while current_date <= end_date:
            report_dates.append(current_date)
            current_date += timedelta(days=1)
        return report_dates

    def _build_matrix(self, subject, start_date, end_date, report_dates):
        attendances = Attendance.objects.select_related(
            'subject', 'teacher', 'faculty', 'enrollment_batch'
        ).prefetch_related('entries__student').filter(
            subject=subject,
            attendance_date__range=(start_date, end_date),
        ).order_by('attendance_date', 'id')

        attendance_lookup = {}
        status_lookup = {}
        students_by_id = {}

        for attendance in attendances:
            attendance_lookup[(attendance.attendance_date, attendance.faculty_id, attendance.enrollment_batch_id)] = attendance
            for entry in attendance.entries.all():
                students_by_id[entry.student_id] = entry.student
                status_lookup[(attendance.attendance_date, attendance.faculty_id, attendance.enrollment_batch_id, entry.student_id)] = entry.status

        students = sorted(
            students_by_id.values(),
            key=lambda student: (
                student.roll_number or '',
                student.name or '',
            ),
        )

        rows = []
        total_days = len(report_dates)
        for student in students:
            statuses = []
            present_count = 0
            for report_date in report_dates:
                attendance = attendance_lookup.get((report_date, student.faculty_id, student.enrollment_batch_id))
                status = '-'
                if attendance:
                    status = status_lookup.get((attendance.attendance_date, attendance.faculty_id, attendance.enrollment_batch_id, student.id), '-')

                if status == AttendanceEntry.STATUS_PRESENT:
                    statuses.append('P')
                    present_count += 1
                elif status == AttendanceEntry.STATUS_ABSENT:
                    statuses.append('A')
                else:
                    statuses.append('-')

            percentage_ratio = (present_count / total_days) if total_days else 0
            rows.append({
                'roll_no': student.roll_number or '-',
                'name': student.name,
                'statuses': statuses,
                'present_count': present_count,
                'percentage_ratio': percentage_ratio,
                'percentage_display': f'{percentage_ratio * 100:.2f}%',
                'highlight': percentage_ratio < 0.5,
            })

        return rows

    def _build_xlsx_response(self, filename_base, title_text, report_dates, rows):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Attendance Report'

        total_columns = 3 + len(report_dates)

        worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_columns)
        title_cell = worksheet.cell(row=1, column=1, value=title_text)
        title_cell.font = Font(bold=True, size=14)
        title_cell.fill = PatternFill('solid', fgColor='EAF2FF')

        date_range_cell = worksheet.cell(
            row=2,
            column=1,
            value=f'Date Range: {report_dates[0]} to {report_dates[-1]}' if report_dates else 'Date Range: -',
        )
        date_range_cell.font = Font(italic=True)

        worksheet.append([])
        headers = ['Roll No', 'Name'] + [report_date.strftime('%d-%b') for report_date in report_dates] + ['Percentage']
        worksheet.append(headers)

        for cell in worksheet[4]:
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='155EEF')

        low_fill = PatternFill('solid', fgColor='FDE2E1')

        for row_index, row in enumerate(rows, start=5):
            row_values = [row['roll_no'], row['name'], *row['statuses'], row['percentage_ratio']]
            worksheet.append(row_values)

            if row['highlight']:
                for column_index in range(1, total_columns + 1):
                    worksheet.cell(row=row_index, column=column_index).fill = low_fill

            percentage_cell = worksheet.cell(row=row_index, column=total_columns)
            percentage_cell.number_format = '0.00%'
            percentage_cell.alignment = percentage_cell.alignment.copy(horizontal='center')

        worksheet.freeze_panes = 'C5'
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 50
        for index in range(3, total_columns):
            worksheet.column_dimensions[get_column_letter(index)].width = 10
        worksheet.column_dimensions[get_column_letter(total_columns)].width = 12

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
        return response

    def _build_pdf_response(self, filename_base, title_text, report_dates, rows):
        output = BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )
        styles = getSampleStyleSheet()

        story = [
            Paragraph(title_text, styles['Title']),
            Spacer(1, 12),
            Paragraph(
                f'Date Range: {report_dates[0]} to {report_dates[-1]}' if report_dates else 'Date Range: -',
                styles['Normal'],
            ),
            Spacer(1, 12),
        ]

        headers = ['Roll No', 'Name'] + [report_date.strftime('%d-%b') for report_date in report_dates] + ['Percentage']
        table_data = [headers]
        if rows:
            for row in rows:
                table_data.append([
                    row['roll_no'],
                    row['name'],
                    *row['statuses'],
                    row['percentage_display'],
                ])
        else:
            table_data.append(['No matching attendance records found.'] + [''] * (len(headers) - 1))

        page_width = landscape(A4)[0] - document.leftMargin - document.rightMargin
        fixed_widths = [90, 220, 58]
        remaining_width = max(page_width - sum(fixed_widths), 0)
        date_width = (remaining_width / len(report_dates)) if report_dates else 0
        column_widths = [fixed_widths[0], fixed_widths[1]] + [date_width for _ in report_dates] + [fixed_widths[2]]

        table = Table(table_data, repeatRows=1, colWidths=column_widths)
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#155eef')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ])

        for row_index, row in enumerate(rows, start=1):
            if row['highlight']:
                table_style.add('BACKGROUND', (0, row_index), (-1, row_index), colors.HexColor('#FDE2E1'))
                table_style.add('TEXTCOLOR', (0, row_index), (-1, row_index), colors.HexColor('#7A1E1E'))

        table.setStyle(table_style)
        story.append(table)

        document.build(story)
        output.seek(0)

        response = HttpResponse(output.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename_base}.pdf"'
        return response
