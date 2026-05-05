from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Q
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from .models import AcademicYear, Curriculum, Department, Faculty, FacultyAvailability, Program, Room, Schedule, Section, Semester, Subject, TeachingLoad, TimeSlot


DAY_ORDER = {
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6,
    'Sunday': 7,
}


def _get_current_semester():
    semester = Semester.objects.filter(is_current=True).select_related('academic_year').first()
    if semester is not None:
        return semester

    return (
        Semester.objects.select_related('academic_year')
        .order_by('-academic_year__start_date', '-semester_number')
        .first()
    )


def _ordered_timeslots():
    timeslots = list(TimeSlot.objects.filter(is_active=True))
    return sorted(timeslots, key=lambda slot: (DAY_ORDER.get(slot.day_of_week, 99), slot.start_time, slot.end_time))


def _faculty_has_availability_conflict(faculty, time_slot):
    unavailable_slots = FacultyAvailability.objects.filter(
        faculty=faculty,
        day_of_week=time_slot.day_of_week,
        is_available=False,
    )
    for unavailable in unavailable_slots:
        overlaps = not (time_slot.end_time <= unavailable.start_time or time_slot.start_time >= unavailable.end_time)
        if overlaps:
            return True
    return False


def _sync_teaching_loads(semester, faculty_load_map):
    for faculty_id, payload in faculty_load_map.items():
        faculty = Faculty.objects.select_related('user', 'department').get(pk=faculty_id)
        maximum_load = faculty.max_teaching_load or 24
        total_units = payload['units']

        if total_units > maximum_load:
            status = 'overload'
        elif total_units < round(maximum_load * 0.67):
            status = 'underload'
        else:
            status = 'normal'

        TeachingLoad.objects.update_or_create(
            faculty=faculty,
            semester=semester,
            defaults={
                'total_units': total_units,
                'total_hours': total_units,
                'total_sections': payload['sections'],
                'status': status,
            },
        )


def _generate_schedule_assignments(semester, generated_by):
    current_schedules = list(
        Schedule.objects.filter(is_active=True, semester=semester)
        .select_related('subject', 'faculty', 'room', 'time_slot', 'section')
    )

    faculty_pool = list(
        Faculty.objects.filter(user__is_active=True, status='active')
        .select_related('user', 'department')
        .order_by('user__last_name', 'user__first_name', 'user__username')
    )
    time_slots = _ordered_timeslots()
    room_pool = list(Room.objects.filter(is_available=True).order_by('capacity', 'code'))

    faculty_load_map = defaultdict(lambda: {'units': 0, 'sections': set()})
    faculty_slot_taken = set()
    section_slot_taken = set()
    room_slot_taken = set()
    existing_pairs = set()

    for schedule in current_schedules:
        faculty_load_map[schedule.faculty_id]['units'] += schedule.subject.units or 0
        faculty_load_map[schedule.faculty_id]['sections'].add(schedule.section_id)
        faculty_slot_taken.add((schedule.faculty_id, schedule.time_slot_id))
        section_slot_taken.add((schedule.section_id, schedule.time_slot_id))
        if schedule.room_id:
            room_slot_taken.add((schedule.room_id, schedule.time_slot_id))
        existing_pairs.add((schedule.section_id, schedule.subject_id))

    created_schedules = []
    skipped_existing = 0
    skipped_no_subjects = 0
    skipped_no_faculty = 0
    skipped_no_slot = 0

    sections = (
        Section.objects.filter(is_active=True)
        .select_related('program', 'program__department', 'semester')
        .order_by('year_level', 'program__code', 'section_name')
    )

    for section in sections:
        section_semester = section.semester or semester
        if section_semester != semester:
            continue

        curriculum_subjects = list(
            Subject.objects.filter(
                is_active=True,
                curriculum__program=section.program,
                curriculum__year_level=section.year_level,
                curriculum__semester=semester.semester_number,
            )
            .distinct()
            .order_by('code')
        )

        if not curriculum_subjects:
            curriculum_subjects = list(
                Subject.objects.filter(
                    is_active=True,
                    department=section.program.department,
                    year_level=section.year_level,
                    semester=semester.semester_number,
                ).order_by('code')
            )

        if not curriculum_subjects:
            skipped_no_subjects += 1
            continue

        for subject in curriculum_subjects:
            if (section.id, subject.id) in existing_pairs:
                skipped_existing += 1
                continue

            preferred_department_id = subject.department_id or section.program.department_id
            eligible_faculty = [faculty for faculty in faculty_pool if not preferred_department_id or faculty.department_id == preferred_department_id]
            if not eligible_faculty:
                eligible_faculty = faculty_pool[:]

            if not eligible_faculty:
                skipped_no_faculty += 1
                continue

            chosen_faculty = None
            chosen_slot = None
            chosen_room = None

            for time_slot in time_slots:
                if (section.id, time_slot.id) in section_slot_taken:
                    continue

                available_faculty = [
                    faculty for faculty in eligible_faculty
                    if (faculty.id, time_slot.id) not in faculty_slot_taken
                    and not _faculty_has_availability_conflict(faculty, time_slot)
                    and len(faculty_load_map[faculty.id]['sections']) < (faculty.max_sections or 6)
                ]

                if not available_faculty:
                    continue

                within_limit = [
                    faculty for faculty in available_faculty
                    if faculty_load_map[faculty.id]['units'] + (subject.units or 0) <= (faculty.max_teaching_load or 24)
                ]
                faculty_candidates = within_limit or available_faculty

                faculty_candidates.sort(
                    key=lambda faculty: (
                        0 if preferred_department_id and faculty.department_id == preferred_department_id else 1,
                        faculty_load_map[faculty.id]['units'],
                        len(faculty_load_map[faculty.id]['sections']),
                        faculty.user.last_name.lower(),
                        faculty.user.first_name.lower(),
                    )
                )

                faculty = faculty_candidates[0]

                room = None
                for candidate_room in room_pool:
                    if candidate_room.capacity < (section.student_count or 0):
                        continue
                    if (candidate_room.id, time_slot.id) in room_slot_taken:
                        continue
                    room = candidate_room
                    break

                if room is None and room_pool:
                    for candidate_room in room_pool:
                        if (candidate_room.id, time_slot.id) not in room_slot_taken:
                            room = candidate_room
                            break

                chosen_faculty = faculty
                chosen_slot = time_slot
                chosen_room = room
                break

            if chosen_faculty is None or chosen_slot is None:
                skipped_no_slot += 1
                continue

            schedule = Schedule.objects.create(
                faculty=chosen_faculty,
                subject=subject,
                section=section,
                room=chosen_room,
                time_slot=chosen_slot,
                semester=semester,
                is_active=True,
                created_by=generated_by,
            )
            created_schedules.append(schedule)

            faculty_load_map[chosen_faculty.id]['units'] += subject.units or 0
            faculty_load_map[chosen_faculty.id]['sections'].add(section.id)
            faculty_slot_taken.add((chosen_faculty.id, chosen_slot.id))
            section_slot_taken.add((section.id, chosen_slot.id))
            if chosen_room is not None:
                room_slot_taken.add((chosen_room.id, chosen_slot.id))
            existing_pairs.add((section.id, subject.id))

    _sync_teaching_loads(semester, faculty_load_map)

    return {
        'created_schedules': created_schedules,
        'created_count': len(created_schedules),
        'skipped_existing': skipped_existing,
        'skipped_no_subjects': skipped_no_subjects,
        'skipped_no_faculty': skipped_no_faculty,
        'skipped_no_slot': skipped_no_slot,
    }


class FacultyListView(LoginRequiredMixin, View):
    """Display faculty management page."""
    login_url = 'login'
    template_name = 'scheduling/faculty_list.html'
    def get(self, request):
        query = request.GET.get('q', '').strip()
        faculty_queryset = Faculty.objects.select_related('user', 'department').order_by('user__last_name', 'user__first_name', 'user__username')

        if query:
            faculty_queryset = faculty_queryset.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__username__icontains=query)
                | Q(user__email__icontains=query)
                | Q(department__name__icontains=query)
            )

        schedules = (
            Schedule.objects.filter(is_active=True, faculty__in=faculty_queryset)
            .select_related('subject', 'faculty__user')
            .order_by('faculty__user__last_name', 'faculty__user__first_name', 'subject__code')
        )

        schedule_map = defaultdict(list)
        for schedule in schedules:
            schedule_map[schedule.faculty_id].append(schedule)

        faculty_rows = []
        total_faculty = 0
        at_max_load = 0
        underutilized = 0
        on_leave = 0

        for faculty in faculty_queryset:
            faculty_schedules = schedule_map.get(faculty.id, [])
            subject_codes = []
            seen_codes = set()
            current_load = 0

            for schedule in faculty_schedules:
                code = schedule.subject.code
                if code in seen_codes:
                    continue
                seen_codes.add(code)
                subject_codes.append(code)
                current_load += schedule.subject.units or 0

            maximum_load = faculty.max_teaching_load or 24

            if faculty.status == 'on_leave' or not faculty.user.is_active:
                status_label = 'On Leave'
                status_class = 'neutral'
                on_leave += 1
            elif current_load >= maximum_load:
                status_label = 'At Maximum Load'
                status_class = 'danger'
                at_max_load += 1
            elif current_load > 0:
                status_label = 'Active'
                status_class = 'success'
                underutilized += 1
            else:
                status_label = 'Active'
                status_class = 'success'
                underutilized += 1

            total_faculty += 1
            load_percentage = min(int((current_load / maximum_load) * 100), 100) if maximum_load else 0
            load_state = 'max' if current_load >= maximum_load else 'green' if current_load >= 12 else 'blue'

            faculty_rows.append({
                'faculty': faculty,
                'display_name': faculty.user.get_full_name() or faculty.user.username,
                'department': faculty.department.name if faculty.department else 'Unassigned',
                'subject_tags': subject_codes[:2],
                'extra_subject_count': max(len(subject_codes) - 2, 0),
                'maximum_load': maximum_load,
                'current_load': current_load,
                'load_percentage': load_percentage,
                'load_state': load_state,
                'status_label': status_label,
                'status_class': status_class,
            })

        context = {
            'query': query,
            'faculty_rows': faculty_rows,
            'summary': {
                'total_faculty': total_faculty,
                'at_max_load': at_max_load,
                'underutilized': underutilized,
                'on_leave': on_leave,
            },
        }
        return render(request, self.template_name, context)


class SubjectListView(LoginRequiredMixin, View):
    """Display subject management page with database-backed filters."""
    login_url = 'login'
    template_name = 'scheduling/subject_list.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()
        year = request.GET.get('year', 'all').strip()
        department = request.GET.get('department', 'all').strip()
        subject_type = request.GET.get('type', 'all').strip()

        base_queryset = Subject.objects.filter(is_active=True).select_related('department').order_by('year_level', 'semester', 'code')
        subjects = base_queryset

        if query:
            subjects = subjects.filter(
                Q(code__icontains=query)
                | Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(department__name__icontains=query)
            )

        if year in {'1', '2', '3', '4'}:
            subjects = subjects.filter(year_level=int(year))

        departments = Department.objects.filter(is_active=True).order_by('name')
        if department.isdigit():
            subjects = subjects.filter(department_id=int(department))

        if subject_type in {'lecture', 'lab', 'lecture-lab'}:
            subjects = subjects.filter(type=subject_type)

        year_distribution = {
            item['year_level']: item['total']
            for item in base_queryset.values('year_level').annotate(total=Count('id'))
        }

        year_tabs = [
            {'value': 'all', 'label': 'All Years', 'count': base_queryset.count()},
            {'value': '1', 'label': '1st Year', 'count': year_distribution.get(1, 0)},
            {'value': '2', 'label': '2nd Year', 'count': year_distribution.get(2, 0)},
            {'value': '3', 'label': '3rd Year', 'count': year_distribution.get(3, 0)},
            {'value': '4', 'label': '4th Year', 'count': year_distribution.get(4, 0)},
        ]

        context = {
            'subjects': subjects,
            'query': query,
            'year': year,
            'department': department,
            'subject_type': subject_type,
            'year_tabs': year_tabs,
            'departments': departments,
            'summary': {
                'total_subjects': base_queryset.count(),
                'lecture_courses': base_queryset.filter(type='lecture').count(),
                'lab_courses': base_queryset.filter(type__in=['lab', 'lecture-lab']).count(),
            },
        }
        return render(request, self.template_name, context)


class SectionListView(LoginRequiredMixin, View):
    """Display section management page with grouped year sections."""
    login_url = 'login'
    template_name = 'scheduling/section_list.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()
        year = request.GET.get('year', 'all').strip()
        program = request.GET.get('program', 'all').strip()

        base_queryset = (
            Section.objects.filter(is_active=True)
            .select_related('program', 'semester', 'semester__academic_year')
            .annotate(active_schedule_count=Count('schedules', filter=Q(schedules__is_active=True), distinct=True))
            .order_by('year_level', 'program__code', 'section_name')
        )

        sections = base_queryset

        if query:
            sections = sections.filter(
                Q(code__icontains=query)
                | Q(section_name__icontains=query)
                | Q(program__code__icontains=query)
                | Q(program__name__icontains=query)
            )

        if year in {'1', '2', '3', '4'}:
            sections = sections.filter(year_level=int(year))

        if program.isdigit():
            sections = sections.filter(program_id=int(program))

        programs = Program.objects.filter(is_active=True).order_by('name')

        year_labels = {
            1: '1st Year',
            2: '2nd Year',
            3: '3rd Year',
            4: '4th Year',
        }

        year_groups = []
        for year_level in [1, 2, 3, 4]:
            year_sections = [section for section in sections if section.year_level == year_level]
            year_groups.append({
                'value': str(year_level),
                'label': year_labels[year_level],
                'count': len(year_sections),
                'sections': year_sections,
            })

        total_students = sum(section.student_count or 0 for section in base_queryset)
        section_count = base_queryset.count()
        average_class_size = round(total_students / section_count) if section_count else 0

        context = {
            'query': query,
            'year': year,
            'program': program,
            'programs': programs,
            'year_groups': year_groups,
            'visible_sections_count': sections.count(),
            'summary': {
                'total_sections': section_count,
                'total_students': total_students,
                'average_class_size': average_class_size,
                'programs': programs.count(),
            },
        }
        return render(request, self.template_name, context)


class TeachingLoadView(LoginRequiredMixin, View):
    """Display faculty teaching load management page."""
    login_url = 'login'
    template_name = 'scheduling/teaching_load.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()
        status_filter = request.GET.get('status', 'all').strip()

        current_semester = (
            Semester.objects.filter(is_current=True)
            .select_related('academic_year')
            .first()
        )

        schedule_queryset = (
            Schedule.objects.filter(is_active=True)
            .select_related('subject', 'faculty__user', 'faculty__department', 'semester', 'semester__academic_year')
        )
        if current_semester is not None:
            schedule_queryset = schedule_queryset.filter(semester=current_semester)

        faculty_queryset = Faculty.objects.select_related('user', 'department').filter(user__is_active=True).order_by('user__last_name', 'user__first_name', 'user__username')

        if query:
            faculty_queryset = faculty_queryset.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__username__icontains=query)
                | Q(user__email__icontains=query)
                | Q(department__name__icontains=query)
            )

        schedule_map = defaultdict(list)
        for schedule in schedule_queryset:
            schedule_map[schedule.faculty_id].append(schedule)

        faculty_rows = []
        overloaded = 0
        balanced = 0
        underutilized = 0
        unassigned = 0

        for faculty in faculty_queryset:
            faculty_schedules = schedule_map.get(faculty.id, [])
            subject_codes = []
            seen_codes = set()
            current_load = 0

            for schedule in faculty_schedules:
                subject_code = schedule.subject.code
                if subject_code in seen_codes:
                    continue
                seen_codes.add(subject_code)
                subject_codes.append(subject_code)
                current_load += schedule.subject.units or 0

            maximum_load = faculty.max_teaching_load or 24

            if current_load <= 0:
                status_key = 'unassigned'
                status_label = 'Unassigned'
                status_class = 'neutral'
                unassigned += 1
            elif current_load > maximum_load:
                status_key = 'overloaded'
                status_label = 'Overloaded'
                status_class = 'danger'
                overloaded += 1
            elif current_load >= max(1, round(maximum_load * 0.67)):
                status_key = 'balanced'
                status_label = 'Balanced'
                status_class = 'success'
                balanced += 1
            else:
                status_key = 'underutilized'
                status_label = 'Underutilized'
                status_class = 'warning'
                underutilized += 1

            if status_filter != 'all' and status_filter != status_key:
                continue

            load_percentage = min(int((current_load / maximum_load) * 100), 100) if maximum_load else 0
            load_state = 'max' if status_key == 'overloaded' else 'green' if status_key == 'balanced' else 'orange' if status_key == 'underutilized' else 'neutral'

            faculty_rows.append({
                'faculty': faculty,
                'display_name': faculty.user.get_full_name() or faculty.user.username,
                'employee_id': faculty.employee_id,
                'department': faculty.department.name if faculty.department else 'Unassigned',
                'subject_tags': subject_codes[:2],
                'extra_subject_count': max(len(subject_codes) - 2, 0),
                'maximum_load': maximum_load,
                'current_load': current_load,
                'load_percentage': load_percentage,
                'load_state': load_state,
                'status_key': status_key,
                'status_label': status_label,
                'status_class': status_class,
            })

        context = {
            'query': query,
            'status_filter': status_filter,
            'current_semester': current_semester,
            'faculty_rows': faculty_rows,
            'summary': {
                'overloaded': overloaded,
                'balanced': balanced,
                'underutilized': underutilized,
                'unassigned': unassigned,
            },
            'visible_faculty_count': len(faculty_rows),
        }
        return render(request, self.template_name, context)


class ScheduleGeneratorView(LoginRequiredMixin, View):
    """Display and run the automatic schedule generator."""
    login_url = 'login'
    template_name = 'scheduling/schedule_generator.html'

    def _build_context(self, request, semester, result=None):
        faculty_count = Faculty.objects.filter(user__is_active=True, status='active').count()
        subject_count = Subject.objects.filter(is_active=True).count()
        available_slots = TimeSlot.objects.filter(is_active=True).count()
        current_schedule_count = Schedule.objects.filter(is_active=True, semester=semester).count() if semester else 0

        current_year = semester.academic_year.year_code if semester else 'N/A'
        current_sem = semester.semester_number if semester else 'N/A'

        context = {
            'semester': semester,
            'current_year': current_year,
            'current_semester_number': current_sem,
            'faculty_count': faculty_count,
            'subject_count': subject_count,
            'available_slots': available_slots,
            'current_schedule_count': current_schedule_count,
            'recent_schedules': Schedule.objects.filter(is_active=True, semester=semester).select_related(
                'subject', 'faculty__user', 'section', 'room', 'time_slot', 'semester__academic_year'
            ).order_by('-created_at')[:12] if semester else [],
            'result': result,
        }
        return context

    def get(self, request):
        semester = _get_current_semester()
        return render(request, self.template_name, self._build_context(request, semester))

    def post(self, request):
        semester = _get_current_semester()
        if semester is None:
            messages.error(request, 'No current semester is available. Set a current semester first.')
            return render(request, self.template_name, self._build_context(request, semester))

        with transaction.atomic():
            result = _generate_schedule_assignments(semester, request.user)

        if result['created_count'] > 0:
            messages.success(request, f"Generated {result['created_count']} schedule assignments successfully.")
        else:
            messages.warning(request, 'No new schedule assignments were created.')

        if result['skipped_existing']:
            messages.info(request, f"Skipped {result['skipped_existing']} already scheduled subject-section pairs.")
        if result['skipped_no_subjects']:
            messages.info(request, f"Skipped {result['skipped_no_subjects']} sections with no curriculum subjects.")
        if result['skipped_no_faculty']:
            messages.info(request, f"Skipped {result['skipped_no_faculty']} assignments without an eligible faculty match.")
        if result['skipped_no_slot']:
            messages.info(request, f"Skipped {result['skipped_no_slot']} assignments with no available time slot.")

        return render(request, self.template_name, self._build_context(request, semester, result=result))


class ScheduleListView(LoginRequiredMixin, View):
    """Display faculty weekly schedule timetable."""
    login_url = 'login'

    def get(self, request):
        semester = _get_current_semester()
        selected_faculty_id = request.GET.get('faculty')

        faculty_queryset = Faculty.objects.filter(user__is_active=True, status='active').select_related('user', 'department').order_by(
            'user__last_name', 'user__first_name', 'user__username'
        )

        selected_faculty = None
        if selected_faculty_id and selected_faculty_id.isdigit():
            selected_faculty = faculty_queryset.filter(pk=int(selected_faculty_id)).first()

        if selected_faculty is None:
            selected_faculty = faculty_queryset.first()

        schedules = Schedule.objects.filter(is_active=True)
        if semester is not None:
            schedules = schedules.filter(semester=semester)
        if selected_faculty is not None:
            schedules = schedules.filter(faculty=selected_faculty)

        schedules = schedules.select_related(
            'subject',
            'faculty__user',
            'room',
            'time_slot',
            'section',
            'semester',
            'semester__academic_year',
        )

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        slot_ranges = sorted(
            {
                (item.time_slot.start_time, item.time_slot.end_time)
                for item in schedules
            },
            key=lambda value: (value[0], value[1]),
        )

        if not slot_ranges:
            slot_ranges = sorted(
                {
                    (slot.start_time, slot.end_time)
                    for slot in TimeSlot.objects.filter(is_active=True, day_of_week__in=days)
                },
                key=lambda value: (value[0], value[1]),
            )

        schedule_map = defaultdict(list)
        for schedule in schedules:
            key = (schedule.time_slot.day_of_week, schedule.time_slot.start_time, schedule.time_slot.end_time)
            schedule_map[key].append(schedule)

        color_cycle = ['green', 'orange', 'blue', 'purple']
        subject_color = {}
        for index, code in enumerate(sorted({item.subject.code for item in schedules})):
            subject_color[code] = color_cycle[index % len(color_cycle)]

        timetable_rows = []
        for start_time, end_time in slot_ranges:
            day_cells = []
            for day in days:
                items = schedule_map.get((day, start_time, end_time), [])
                for item in items:
                    item.card_color = subject_color.get(item.subject.code, 'green')
                day_cells.append({'day': day, 'items': items})

            timetable_rows.append({
                'start_time': start_time,
                'end_time': end_time,
                'day_cells': day_cells,
            })

        current_load_sections = 0
        total_classes = schedules.count()
        if selected_faculty is not None:
            current_load_sections = schedules.values('section_id').distinct().count()

        context = {
            'schedules': schedules,
            'faculties': faculty_queryset,
            'selected_faculty': selected_faculty,
            'semester': semester,
            'days': days,
            'timetable_rows': timetable_rows,
            'current_load_sections': current_load_sections,
            'maximum_sections': selected_faculty.max_sections if selected_faculty else 0,
            'total_classes': total_classes,
            'generated_at': timezone.localdate(),
        }
        return render(request, 'scheduling/schedule_list.html', context)


class SectionScheduleView(LoginRequiredMixin, View):
    """Display section weekly schedule timetable."""
    login_url = 'login'
    template_name = 'scheduling/section_schedule.html'

    def get(self, request):
        current_semester = _get_current_semester()
        sections = (
            Section.objects.filter(is_active=True)
            .select_related('program', 'program__department', 'semester', 'semester__academic_year')
            .order_by('program__code', 'year_level', 'section_name')
        )

        selected_section_id = request.GET.get('section')
        selected_section = None
        if selected_section_id and selected_section_id.isdigit():
            selected_section = sections.filter(pk=int(selected_section_id)).first()

        if selected_section is None:
            if current_semester is not None:
                selected_section = sections.filter(semester=current_semester).first()
            if selected_section is None:
                selected_section = sections.first()

        effective_semester = None
        if selected_section is not None:
            effective_semester = selected_section.semester or current_semester
        else:
            effective_semester = current_semester

        schedules = Schedule.objects.filter(is_active=True)
        if effective_semester is not None:
            schedules = schedules.filter(semester=effective_semester)
        if selected_section is not None:
            schedules = schedules.filter(section=selected_section)

        schedules = schedules.select_related(
            'subject',
            'faculty__user',
            'room',
            'time_slot',
            'section',
            'semester',
            'semester__academic_year',
        )

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        slot_ranges = sorted(
            {
                (item.time_slot.start_time, item.time_slot.end_time)
                for item in schedules
            },
            key=lambda value: (value[0], value[1]),
        )

        if not slot_ranges:
            slot_ranges = sorted(
                {
                    (slot.start_time, slot.end_time)
                    for slot in TimeSlot.objects.filter(is_active=True, day_of_week__in=days)
                },
                key=lambda value: (value[0], value[1]),
            )

        schedule_map = defaultdict(list)
        for schedule in schedules:
            key = (schedule.time_slot.day_of_week, schedule.time_slot.start_time, schedule.time_slot.end_time)
            schedule_map[key].append(schedule)

        color_cycle = ['green', 'orange', 'blue', 'purple']
        subject_color = {}
        for index, code in enumerate(sorted({item.subject.code for item in schedules})):
            subject_color[code] = color_cycle[index % len(color_cycle)]

        timetable_rows = []
        for start_time, end_time in slot_ranges:
            day_cells = []
            for day in days:
                items = schedule_map.get((day, start_time, end_time), [])
                for item in items:
                    item.card_color = subject_color.get(item.subject.code, 'green')
                day_cells.append({'day': day, 'items': items})

            timetable_rows.append({
                'start_time': start_time,
                'end_time': end_time,
                'day_cells': day_cells,
            })

        section_schedule_count = schedules.count()
        total_subjects = schedules.values('subject_id').distinct().count()

        context = {
            'sections': sections,
            'selected_section': selected_section,
            'current_semester': effective_semester,
            'days': days,
            'timetable_rows': timetable_rows,
            'section_schedule_count': section_schedule_count,
            'total_subjects': total_subjects,
            'generated_at': timezone.localdate(),
        }
        return render(request, self.template_name, context)


class ScheduleDetailView(LoginRequiredMixin, View):
    """Display schedule details."""
    login_url = 'login'

    def get(self, request, pk):
        schedule = Schedule.objects.select_related(
            'subject',
            'subject__department',
            'faculty__user',
            'room',
            'time_slot',
            'section',
            'semester',
        ).get(pk=pk)
        context = {
            'schedule': schedule,
        }
        return render(request, 'scheduling/schedule_detail.html', context)
