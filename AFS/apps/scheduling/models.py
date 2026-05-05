"""
Scheduling App Models - Complete PostgreSQL Schema Implementation
"""
from django.db import models
from django.conf import settings


class Department(models.Model):
    """Academic Department"""
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, blank=True, null=True, related_name='headed_departments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class Faculty(models.Model):
    """Faculty Member Profile"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(unique=True, max_length=20)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, related_name='faculty_members')
    specialization = models.TextField(blank=True, null=True)
    max_teaching_load = models.IntegerField(default=24)
    max_sections = models.IntegerField(default=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    phone = models.CharField(max_length=20, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'faculty'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return self.user.get_full_name()


class Program(models.Model):
    """Academic Program (e.g., BSIS, BSCS)"""
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, related_name='programs')
    total_years = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'programs'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Subject(models.Model):
    """Subject/Course Definition"""
    TYPE_CHOICES = [
        ('lecture', 'Lecture'),
        ('lab', 'Lab'),
        ('lecture-lab', 'Lecture-Lab'),
    ]
    
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    units = models.IntegerField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    hours_per_week = models.IntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, related_name='subjects')
    year_level = models.IntegerField(choices=[(i, f'Year {i}') for i in range(1, 5)])
    semester = models.IntegerField(choices=[(1, 'Semester 1'), (2, 'Semester 2')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['year_level', 'semester']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Prerequisite(models.Model):
    """Subject Prerequisites"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite_subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='required_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prerequisites'
        unique_together = ('subject', 'prerequisite_subject')

    def __str__(self):
        return f"{self.prerequisite_subject.code} → {self.subject.code}"


class AcademicYear(models.Model):
    """Academic Year (e.g., 2024-2025)"""
    year_code = models.CharField(unique=True, max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academic_years'
        ordering = ['-year_code']

    def __str__(self):
        return self.year_code


class Semester(models.Model):
    """Semester within Academic Year"""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.IntegerField(choices=[(1, 'First'), (2, 'Second')])
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semesters'
        unique_together = ('academic_year', 'semester_number')
        ordering = ['-academic_year', 'semester_number']

    def __str__(self):
        return f"{self.academic_year.year_code} - Sem {self.semester_number}"


class Section(models.Model):
    """Class Section"""
    code = models.CharField(unique=True, max_length=20)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='sections')
    year_level = models.IntegerField(choices=[(i, f'Year {i}') for i in range(1, 5)])
    section_name = models.CharField(max_length=10)
    student_count = models.IntegerField(default=0)
    max_capacity = models.IntegerField(default=50)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, blank=True, null=True, related_name='sections')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sections'
        ordering = ['code']

    def __str__(self):
        return self.code


class Curriculum(models.Model):
    """Program Curriculum Mapping"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='curriculum')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='curriculum')
    year_level = models.IntegerField(choices=[(i, f'Year {i}') for i in range(1, 5)])
    semester = models.IntegerField(choices=[(1, 'Semester 1'),  (2, 'Semester 2')])
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curriculum'
        unique_together = ('program', 'subject', 'year_level', 'semester')

    def __str__(self):
        return f"{self.program.code}: {self.subject.code}"


class Room(models.Model):
    """Classroom/Room Resource"""
    TYPE_CHOICES = [
        ('classroom', 'Classroom'),
        ('laboratory', 'Laboratory'),
        ('lecture_hall', 'Lecture Hall'),
        ('gym', 'Gym'),
    ]
    
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)
    building = models.CharField(max_length=100, blank=True, null=True)
    floor = models.IntegerField(blank=True, null=True)
    capacity = models.IntegerField(default=30)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True, null=True)
    facilities = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rooms'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class TimeSlot(models.Model):
    """Time Slot for Classes"""
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'time_slots'
        unique_together = ('day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.day_of_week} {self.start_time}-{self.end_time}"


class Schedule(models.Model):
    """Class Schedule Assignment"""
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='schedules')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True, related_name='schedules')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='schedules')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='schedules')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_schedules', db_column='created_by')

    class Meta:
        db_table = 'schedules'
        ordering = ['-semester', 'faculty', 'subject']
        indexes = [
            models.Index(fields=['faculty', 'semester']),
            models.Index(fields=['section', 'semester']),
        ]

    def __str__(self):
        return f"{self.faculty.user.get_full_name()}: {self.subject.code} ({self.section.code})"


class TeachingLoad(models.Model):
    """Calculated Teaching Load per Faculty per Semester"""
    STATUS_CHOICES = [
        ('underload', 'Underload'),
        ('normal', 'Normal'),
        ('overload', 'Overload'),
    ]
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='teaching_loads')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='teaching_loads')
    total_units = models.IntegerField(default=0)
    total_hours = models.IntegerField(default=0)
    total_sections = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teaching_loads'
        unique_together = ('faculty', 'semester')
        ordering = ['faculty', '-semester']

    def __str__(self):
        return f"{self.faculty.user.get_full_name()} - {self.semester}: {self.total_units} units"


class SchedulePattern(models.Model):
    """Schedule Pattern Templates (e.g., MWF, TTH)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    days = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'schedule_patterns'
        ordering = ['name']

    def __str__(self):
        return self.name


class Conflict(models.Model):
    """Scheduling Conflict Records"""
    CONFLICT_TYPE_CHOICES = [
        ('faculty', 'Faculty Conflict'),
        ('room', 'Room Conflict'),
        ('section', 'Section Conflict'),
    ]
    
    STATUS_CHOICES = [
        ('unresolved', 'Unresolved'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ]
    
    conflict_type = models.CharField(max_length=50, choices=CONFLICT_TYPE_CHOICES)
    schedule_id_1 = models.ForeignKey(Schedule, on_delete=models.CASCADE, db_column='schedule_id_1', blank=True, null=True, related_name='conflicts_as_first')
    schedule_id_2 = models.ForeignKey(Schedule, on_delete=models.CASCADE, db_column='schedule_id_2', blank=True, null=True, related_name='conflicts_as_second')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unresolved')
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='resolved_conflicts')

    class Meta:
        db_table = 'conflicts'
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.conflict_type}: {self.status}"


class Notification(models.Model):
    """System Notifications"""
    TYPE_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    """Audit Log for Data Changes"""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    table_name = models.CharField(max_length=50)
    record_id = models.IntegerField(blank=True, null=True)
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['table_name', '-created_at']),
        ]

    def __str__(self):
        return f"{self.action} on {self.table_name}"


class Setting(models.Model):
    """System Settings"""
    DATA_TYPE_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]
    
    key = models.CharField(unique=True, max_length=100)
    value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True,  null=True)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='updated_settings')

    class Meta:
        db_table = 'settings'
        ordering = ['key']

    def __str__(self):
        return f"{self.key} = {self.value}"


class Holiday(models.Model):
    """Academic Calendar Holidays"""
    TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('special', 'Special'),
        ('university', 'University'),
    ]
    
    name = models.CharField(max_length=100)
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'holidays'
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"


class FacultyAvailability(models.Model):
    """Faculty Availability Constraints"""
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'faculty_availability'
        unique_together = ('faculty', 'day_of_week', 'start_time')
        ordering = ['faculty', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.faculty.user.get_full_name()} - {self.day_of_week} {self.start_time}-{self.end_time}"


class ScheduleRequest(models.Model):
    """Faculty Schedule Change Requests"""
    REQUEST_TYPE_CHOICES = [
        ('change_time', 'Change Time'),
        ('change_room', 'Change Room'),
        ('swap', 'Swap'),
        ('cancel', 'Cancel'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='schedule_requests')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    reason = models.TextField()
    requested_changes = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'schedule_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.faculty.user.get_full_name()} - {self.request_type}: {self.status}"
