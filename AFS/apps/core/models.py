from django.db import models


class SystemSettings(models.Model):
    """System configuration and settings."""
    site_name = models.CharField(max_length=255, default='Faculty Scheduling System')
    university_name = models.CharField(max_length=255, default='Carlos Hilado Memorial State University')
    logo_text = models.CharField(max_length=10, default='CHMSU')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.site_name
