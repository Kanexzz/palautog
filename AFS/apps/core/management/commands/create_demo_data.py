"""
Management command to create initial demo data
"""
from itertools import cycle

from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model
from apps.scheduling.models import (
    AcademicYear,
    Department,
    Faculty,
    Program,
    Room,
    Schedule,
    Section,
    Semester,
    Subject,
    TimeSlot,
)

User = get_user_model()


def ensure_auth_schema():
    """Bring the legacy users table up to Django's auth schema."""
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(128) NOT NULL DEFAULT ''")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP NULL")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_staff BOOLEAN NOT NULL DEFAULT FALSE")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN NOT NULL DEFAULT FALSE")

        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = 'users'
              AND column_name = 'password_hash'
            """
        )
        if cursor.fetchone():
            cursor.execute("ALTER TABLE users ALTER COLUMN password_hash SET DEFAULT ''")

        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = 'users'
              AND column_name = 'password_hash'
            """
        )
        if cursor.fetchone():
            cursor.execute(
                "UPDATE users SET password = password_hash WHERE COALESCE(password, '') = '' AND COALESCE(password_hash, '') <> ''"
            )


class Command(BaseCommand):
    help = 'Create initial demo data for the Faculty Scheduling System'

    def handle(self, *args, **options):
        ensure_auth_schema()

        # Create departments
        dept_cs = Department.objects.get_or_create(
            code='CS',
            defaults={'name': 'Computer Science'}
        )[0]

        dept_is = Department.objects.get_or_create(
            code='IS',
            defaults={'name': 'Information Systems'}
        )[0]

        self.stdout.write(self.style.SUCCESS('Created departments'))

        academic_year = AcademicYear.objects.get_or_create(
            year_code='2025-2026',
            defaults={
                'start_date': '2025-08-01',
                'end_date': '2026-05-31',
                'is_current': True,
            },
        )[0]

        semester = Semester.objects.get_or_create(
            academic_year=academic_year,
            semester_number=1,
            defaults={
                'start_date': '2025-08-01',
                'end_date': '2025-12-31',
                'is_current': True,
            },
        )[0]

        program = Program.objects.get_or_create(
            code='BSIS',
            defaults={
                'name': 'Bachelor of Science in Information Systems',
                'description': 'BS Information Systems Program',
                'department': dept_is,
                'total_years': 4,
                'is_active': True,
            },
        )[0]

        section_a = Section.objects.get_or_create(
            code='BSIS-1A',
            defaults={
                'program': program,
                'year_level': 1,
                'section_name': 'A',
                'student_count': 35,
                'max_capacity': 40,
                'semester': semester,
                'is_active': True,
            },
        )[0]

        self.stdout.write(self.style.SUCCESS('Created academic year, semester, program, and section'))

        # Create rooms
        rooms = []
        for i in range(1, 6):
            room, _ = Room.objects.get_or_create(
                code=f'IT{i}01',
                defaults={
                    'building': 'IT Building',
                    'floor': 1,
                    'capacity': 40 if i % 2 == 0 else 35
                }
            )
            rooms.append(room)

        self.stdout.write(self.style.SUCCESS('Created classrooms'))

        # Create time slots
        time_slots = []
        slot_data = [
            ('Monday', '08:00', '09:30'),
            ('Monday', '10:00', '11:30'),
            ('Tuesday', '08:00', '09:30'),
            ('Tuesday', '10:00', '11:30'),
            ('Wednesday', '08:00', '09:30'),
            ('Wednesday', '10:00', '11:30'),
            ('Thursday', '08:00', '09:30'),
            ('Thursday', '10:00', '11:30'),
            ('Friday', '08:00', '09:30'),
            ('Friday', '10:00', '11:30'),
        ]

        for day, start, end in slot_data:
            time_slot, _ = TimeSlot.objects.get_or_create(
                day_of_week=day,
                start_time=start,
                end_time=end
            )
            time_slots.append(time_slot)

        self.stdout.write(self.style.SUCCESS('Created time slots'))

        # Create subjects
        subject_specs = [
            ('CS101', 'Introduction to Programming', 'Lecture', dept_cs, 3, 'lecture', 1, 1),
            ('CS102', 'Data Structures', 'Lecture', dept_cs, 3, 'lecture', 1, 2),
            ('CS103', 'Software Engineering', 'Lecture', dept_cs, 3, 'lecture', 2, 1),
            ('IS101', 'Introduction to Information Systems', 'Lecture', dept_is, 3, 'lecture', 1, 1),
            ('IS201', 'Database Management', 'Lecture', dept_is, 3, 'lecture', 2, 1),
            ('IS202', 'Systems Analysis and Design', 'Lecture', dept_is, 3, 'lecture', 2, 2),
        ]
        subjects = []
        for code, title, description, dept, units, subject_type, year_level, semester_number in subject_specs:
            subject, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': title,
                    'description': description,
                    'units': units,
                    'type': subject_type,
                    'department': dept,
                    'year_level': year_level,
                    'semester': semester_number,
                    'is_active': True,
                }
            )
            subjects.append(subject)

        self.stdout.write(self.style.SUCCESS('Created subjects'))

        # Create or update demo admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@chmsu.edu.ph',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        else:
            admin_user.email = 'admin@chmsu.edu.ph'
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'User'
            admin_user.role = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
        admin_user.set_password('admin123')
        admin_user.save()

        # Create demo faculty users
        demo_faculty = [
            ('jsmith', 'John', 'Smith', 'john@chmsu.edu.ph'),
            ('mdoe', 'Mary', 'Doe', 'mary@chmsu.edu.ph'),
            ('rjones', 'Robert', 'Jones', 'robert@chmsu.edu.ph'),
            ('amartin', 'Ana', 'Martin', 'ana@chmsu.edu.ph'),
            ('bgarcia', 'Ben', 'Garcia', 'ben@chmsu.edu.ph'),
            ('cfernandez', 'Cara', 'Fernandez', 'cara@chmsu.edu.ph'),
            ('dlopez', 'Daniel', 'Lopez', 'daniel@chmsu.edu.ph'),
            ('ecruz', 'Ellen', 'Cruz', 'ellen@chmsu.edu.ph'),
            ('freyes', 'Francis', 'Reyes', 'francis@chmsu.edu.ph'),
            ('gtorres', 'Grace', 'Torres', 'grace@chmsu.edu.ph'),
        ]

        faculty_users = []
        for username, first_name, last_name, email in demo_faculty:
            faculty_user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'faculty',
                    'is_active': True,
                }
            )
            faculty_user.email = email
            faculty_user.first_name = first_name
            faculty_user.last_name = last_name
            faculty_user.role = 'faculty'
            faculty_user.is_active = True
            faculty_user.set_password('faculty123')
            faculty_user.save()
            faculty_users.append(faculty_user)

        self.stdout.write(self.style.SUCCESS('Created demo faculty users'))

        faculty_profiles = []
        for index, faculty_user in enumerate(faculty_users, start=1):
            faculty_profile, _ = Faculty.objects.get_or_create(
                user=faculty_user,
                defaults={
                    'employee_id': f'EMP-{index:03d}',
                    'department': dept_is,
                    'specialization': 'Information Systems',
                    'max_teaching_load': 24,
                    'max_sections': 6,
                    'status': 'active',
                },
            )
            faculty_profiles.append(faculty_profile)

        self.stdout.write(self.style.SUCCESS('Created faculty profiles'))

        # Create sample schedules so faculty loads render meaningfully
        schedule_specs = [
            (faculty_profiles[0], [subjects[0], subjects[3]]),
            (faculty_profiles[1], [subjects[1]]),
            (faculty_profiles[2], [subjects[4], subjects[5]]),
            (faculty_profiles[3], [subjects[2]]),
            (faculty_profiles[4], [subjects[0], subjects[1]]),
            (faculty_profiles[5], [subjects[3]]),
            (faculty_profiles[6], [subjects[4]]),
            (faculty_profiles[7], [subjects[5], subjects[0]]),
            (faculty_profiles[8], [subjects[1]]),
            (faculty_profiles[9], [subjects[2], subjects[3]]),
        ]

        sections = cycle([section_a])
        room_cycle = cycle(rooms)
        slot_cycle = cycle(time_slots)

        for faculty_profile, assigned_subjects in schedule_specs:
            for subject in assigned_subjects:
                Schedule.objects.update_or_create(
                    faculty=faculty_profile,
                    subject=subject,
                    section=next(sections),
                    semester=semester,
                    defaults={
                        'room': next(room_cycle),
                        'time_slot': next(slot_cycle),
                        'created_by': admin_user,
                        'is_active': True,
                    }
                )

        self.stdout.write(self.style.SUCCESS('Created sample schedules'))
        self.stdout.write(self.style.SUCCESS('✓ Demo data created successfully!'))
