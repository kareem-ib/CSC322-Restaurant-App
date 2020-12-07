from django.contrib import admin
from .models import Customer, Post, Report
from django.contrib.admin.models import LogEntry

LogEntry.objects.all().delete()

# Register your models here.
def accept_report(modeladmin, request, queryset):
    for report in queryset:
        report.accept_report()
        print('Report for', report.complainee.username, "submitted")
accept_report.short_description = 'Accept this report'

def deny_report(modeladmin, request, queryset):
    for report in queryset:
        report.deny_report()
        print('Report for', report.snitch.username, "submitted")
deny_report.short_description = 'Deny this report'

class ReportAdmin(admin.ModelAdmin):
    list_display = ['snitch', 'complainee', 'report_body', 'is_disputed', 'dispute_body']
    ordering = ['-time_reported']
    actions = [accept_report, deny_report]

admin.site.register(Customer)
admin.site.register(Post)
admin.site.register(Report, ReportAdmin)
