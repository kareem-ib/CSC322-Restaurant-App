from django.contrib import admin
from .models import Customer, Post, Report, Dish, Chef
from django.contrib.admin.models import LogEntry

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

"""@admin.Register(Chef)
class DesignatedChef(admin.UserAdmin):"""


admin.site.site_header = 'Los Tres Locos'
admin.site.register(Customer)
admin.site.register(Post)
admin.site.register(Report, ReportAdmin)
admin.site.register(Dish)
admin.site.register(Chef)
