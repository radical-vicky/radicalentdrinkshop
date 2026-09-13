from django.contrib import admin
from django.utils.html import format_html

from .models import JobApplication, JobListing


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ('full_name', 'email', 'phone_number', 'message', 'resume_link', 'submitted_at')
    fields = ('full_name', 'email', 'phone_number', 'resume_link', 'reviewed', 'submitted_at')


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'location', 'employment_type', 'is_active', 'posted_at')
    list_filter = ('department', 'employment_type', 'is_active')
    search_fields = ('title', 'department', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [JobApplicationInline]

    fieldsets = (
        ('Basic info', {
            'fields': ('title', 'slug', 'department', 'location', 'employment_type')
        }),
        ('Content', {
            'fields': ('description', 'requirements')
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
            'description': "Optional banner image shown at the top of the job listing.",
        }),
        ('Visibility', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if not obj.image:
            return '—'
        return format_html(
            '<img src="{}" style="max-height: 160px; border-radius: 6px;" />',
            obj.image.url,
        )

    image_preview.short_description = 'Preview'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job', 'email', 'phone_number', 'reviewed', 'submitted_at')
    list_filter = ('reviewed', 'job')
    search_fields = ('full_name', 'email', 'phone_number')