from django.db.models import Sum, Count
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from django.utils import timezone
from .models import SystemSettings
from apps.scheduling.models import Faculty, Subject, Section, Schedule, TeachingLoad, Semester, AcademicYear


class IndexView(View):
    """Landing page / Login page."""

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'core/dashboard.html')

        context = {
            'site_name': 'Faculty Scheduling System',
            'university_name': 'Carlos Hilado Memorial State University',
            'logo_text': 'CHMSU',
            'description': 'Faculty Scheduling System - Constraint-Based Optimization',
            'tagline': 'For University Departments - Optimize faculty scheduling using constraint-based algorithms for efficient resource allocation and conflict-free timetabling.',
        }
        return render(request, 'authentication/login.html', context)


class DashboardView(LoginRequiredMixin, View):
    """Dashboard page for authenticated users."""
    login_url = 'login'

    def get(self, request):
        total_faculty = Faculty.objects.filter(status='active').count()
        total_subjects = Subject.objects.filter(is_active=True).count()
        total_sections = Section.objects.filter(is_active=True).count()
        scheduled_classes = Schedule.objects.filter(is_active=True).count()

        assigned_subject_ids = Schedule.objects.filter(is_active=True).values_list('subject_id', flat=True).distinct()
        unassigned_subjects = Subject.objects.filter(is_active=True).exclude(id__in=assigned_subject_ids).count()

        context = {
            'user': request.user,
            'stats': {
                'total_faculty': total_faculty,
                'total_subjects': total_subjects,
                'total_sections': total_sections,
                'scheduled_classes': scheduled_classes,
                'unassigned_subjects': unassigned_subjects,
            },
        }
        return render(request, 'core/dashboard.html', context)


class ReportsView(LoginRequiredMixin, View):
    """Reports and analytics page."""
    login_url = 'login'

    def get(self, request):
        current_semester = Semester.objects.filter(is_current=True).select_related('academic_year').first()
        if current_semester is None:
            current_semester = Semester.objects.select_related('academic_year').order_by('-academic_year__start_date', '-semester_number').first()

        active_faculty = Faculty.objects.filter(status='active').select_related('user', 'department').order_by('user__last_name', 'user__first_name', 'user__username')
        active_subjects = Subject.objects.filter(is_active=True)
        active_sections = Section.objects.filter(is_active=True)
        active_schedules = Schedule.objects.filter(is_active=True)

        if current_semester is not None:
            active_schedules = active_schedules.filter(semester=current_semester)

        assigned_subject_ids = active_schedules.values_list('subject_id', flat=True).distinct()
        unassigned_subjects = active_subjects.exclude(id__in=assigned_subject_ids).count()

        teaching_loads = TeachingLoad.objects.none()
        if current_semester is not None:
            teaching_loads = TeachingLoad.objects.filter(semester=current_semester).select_related('faculty__user')

        load_map = {load.faculty_id: load for load in teaching_loads}
        report_faculty_rows = []
        for faculty in active_faculty:
            load = load_map.get(faculty.id)
            current_load = load.total_units if load else active_schedules.filter(faculty=faculty).aggregate(total=Sum('subject__units')).get('total') or 0
            max_load = faculty.max_teaching_load or 24
            load_percentage = min(int(round((current_load / max_load) * 100)) if max_load else 0, 100)
            report_faculty_rows.append({
                'faculty': faculty,
                'label': ''.join(part[0] for part in faculty.user.get_full_name().split() if part)[:3] or faculty.user.username[:3].upper(),
                'current_load': current_load,
                'max_load': max_load,
                'load_percentage': load_percentage,
            })

        report_faculty_rows.sort(key=lambda row: row['current_load'], reverse=True)
        report_faculty_rows = report_faculty_rows[:10]

        total_programs = Section.objects.filter(is_active=True).values('program_id').distinct().count()
        total_faculty = active_faculty.count()
        total_subjects = active_subjects.count()
        total_sections = active_sections.count()
        scheduled_classes = active_schedules.count()

        scheduled_subject_count = active_schedules.values('subject_id').distinct().count()
        subject_distribution = 0
        if total_subjects:
            subject_distribution = round((scheduled_subject_count / total_subjects) * 100)

        load_distribution = []
        for row in report_faculty_rows:
            load_distribution.append({
                'label': row['label'],
                'current_height': max(12, round((row['current_load'] / max(row['max_load'], 1)) * 100)),
                'max_height': 100,
                'current_load': row['current_load'],
                'max_load': row['max_load'],
            })

        context = {
            'current_semester': current_semester,
            'summary_cards': [
                {
                    'title': 'Faculty Report',
                    'description': 'Teaching loads and assignments',
                    'icon': '👥',
                    'active': True,
                },
                {
                    'title': 'Subject Distribution',
                    'description': 'Subject allocation across faculty',
                    'icon': '▤',
                    'value': f'{subject_distribution}%',
                },
                {
                    'title': 'Program Overview',
                    'description': 'BSIS program statistics',
                    'icon': '↗',
                    'value': str(total_programs),
                },
                {
                    'title': 'Load Distribution',
                    'description': 'Faculty workload analysis',
                    'icon': '🗓',
                    'value': f'{scheduled_classes} classes',
                },
            ],
            'faculty_chart_rows': load_distribution,
            'faculty_rows': report_faculty_rows,
            'report_stats': {
                'total_faculty': total_faculty,
                'total_subjects': total_subjects,
                'total_sections': total_sections,
                'scheduled_classes': scheduled_classes,
                'unassigned_subjects': unassigned_subjects,
            },
        }
        return render(request, 'core/reports.html', context)


class SettingsView(LoginRequiredMixin, View):
    """Settings page for user preferences and system configuration."""
    login_url = 'login'

    def get(self, request):
        current_semester = Semester.objects.filter(is_current=True).select_related('academic_year').first()
        if current_semester is None:
            current_semester = Semester.objects.select_related('academic_year').order_by('-academic_year__start_date', '-semester_number').first()
        
        academic_years = AcademicYear.objects.order_by('-year_code')
        semesters = Semester.objects.all().order_by('-academic_year__start_date', '-semester_number')
        
        user = request.user
        profile = {
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'role': 'Administrator' if user.is_superuser else 'User'
        }
        
        context = {
            'user': user,
            'profile': profile,
            'current_semester': current_semester,
            'academic_years': academic_years,
            'semesters': semesters,
        }
        return render(request, 'core/settings.html', context)


class SettingsView(LoginRequiredMixin, View):
    """Settings and configuration page."""
    login_url = 'login'

    def get(self, request):
        user = request.user
        current_semester = Semester.objects.filter(is_current=True).select_related('academic_year').first()
        if current_semester is None:
            current_semester = Semester.objects.select_related('academic_year').order_by('-academic_year__start_date', '-semester_number').first()

        academic_years = AcademicYear.objects.order_by('-year_code')
        semesters = Semester.objects.select_related('academic_year').order_by('-academic_year__start_date', '-semester_number')

        context = {
            'user': user,
            'current_semester': current_semester,
            'academic_years': academic_years,
            'semesters': semesters,
            'profile': {
                'full_name': user.get_full_name() or user.username,
                'email': user.email,
                'role': 'Administrator' if user.is_superuser else 'User',
            },
        }
        return render(request, 'core/settings.html', context)
