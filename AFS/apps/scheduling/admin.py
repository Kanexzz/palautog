from django.contrib import admin
from .models import (
    Department, Faculty, Program, Subject, Prerequisite,
    AcademicYear, Semester, Section, Curriculum, Room, TimeSlot,
    Schedule, TeachingLoad, SchedulePattern, Conflict, Notification,
    AuditLog, Setting, Holiday, FacultyAvailability, ScheduleRequest
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'head', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'status')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name')
    list_filter = ('status', 'department', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active', 'department')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'units', 'type', 'year_level', 'semester')
    search_fields = ('code', 'name')
    list_filter = ('type', 'year_level', 'semester', 'department')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('subject', 'prerequisite_subject')
    search_fields = ('subject__code', 'prerequisite_subject__code')
    readonly_fields = ('created_at',)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year_code', 'start_date', 'end_date', 'is_current')
    search_fields = ('year_code',)
    list_filter = ('is_current',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'semester_number', 'start_date', 'end_date', 'is_current')
    search_fields = ('academic_year__year_code',)
    list_filter = ('semester_number', 'is_current')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('code', 'program', 'year_level', 'program', 'student_count', 'max_capacity')
    search_fields = ('code', 'program__code')
    list_filter = ('year_level', 'program', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('program', 'subject', 'year_level', 'semester', 'is_required')
    search_fields = ('program__code', 'subject__code')
    list_filter = ('year_level', 'semester', 'is_required')
    readonly_fields = ('created_at',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'building', 'capacity', 'type', 'is_available')
    search_fields = ('code', 'name', 'building')
    list_filter = ('building', 'type', 'is_available')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    readonly_fields = ('created_at',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('subject', 'faculty', 'section', 'room', 'time_slot', 'semester')
    search_fields = ('subject__code', 'faculty__user__username', 'section__code')
    list_filter = ('semester', 'subject__department', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TeachingLoad)
class TeachingLoadAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'semester', 'total_units', 'total_sections', 'status')
    search_fields = ('faculty__user__username',)
    list_filter = ('status', 'semester')
    readonly_fields = ('calculated_at',)


@admin.register(SchedulePattern)
class SchedulePatternAdmin(admin.ModelAdmin):
    list_display = ('name', 'days')
    search_fields = ('name', 'days')
    readonly_fields = ('created_at',)


@admin.register(Conflict)
class ConflictAdmin(admin.ModelAdmin):
    list_display = ('conflict_type', 'status', 'detected_at')
    search_fields = ('description',)
    list_filter = ('conflict_type', 'status', 'detected_at')
    readonly_fields = ('detected_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    list_filter = ('type', 'is_read', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'table_name', 'user', 'created_at')
    search_fields = ('table_name', 'user__username')
    list_filter = ('action', 'table_name', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'data_type')
    search_fields = ('key',)
    list_filter = ('data_type',)
    readonly_fields = ('updated_at',)


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'type')
    search_fields = ('name',)
    list_filter = ('type', 'date')
    readonly_fields = ('created_at',)


@admin.register(FacultyAvailability)
class FacultyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'day_of_week', 'start_time', 'end_time', 'is_available')
    search_fields = ('faculty__user__username',)
    list_filter = ('day_of_week', 'is_available')
    readonly_fields = ('created_at',)


@admin.register(ScheduleRequest)
class ScheduleRequestAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'request_type', 'status', 'created_at')
    search_fields = ('faculty__user__username',)
    list_filter = ('request_type', 'status', 'created_at')
    readonly_fields = ('created_at', 'reviewed_at')
