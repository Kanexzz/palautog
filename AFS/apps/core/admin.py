from django.contrib import admin
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'university_name', 'logo_text', 'updated_at')
    fieldsets = (
        ('System Information', {
            'fields': ('site_name', 'university_name', 'logo_text')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
