from django.contrib import admin
from .models import Customer, Post, Report, Dish, Chef, DeliveryPerson, Complaints, Compliments, Orders, TabooWords
from django.contrib.admin.models import LogEntry

# Register your models here.
def accept_report(modeladmin, request, queryset):
    for report in queryset:
        report.accept_report()
        print('Report for', report.complainee.username, "submitted")
accept_report.short_description = 'Accept the report(s)'

def deny_report(modeladmin, request, queryset):
    for report in queryset:
        report.deny_report()
        print('Report for', report.snitch.username, "submitted")
deny_report.short_description = 'Deny the report(s)'

def accept_compliment(modeladmin, request, queryset):
    for compliment in queryset:
        compliment.accept_compliment()
        print('Compliment for', compliment.sender.username, 'accepted')
accept_compliment.short_description = 'Accept the compliment(s)'

def deny_compliment(modeladmin, request, queryset):
    for compliment in queryset:
        compliment.deny_compliment()
        print('Compliment for', compliment.sender.username, 'denied')
deny_compliment.short_description = 'Deny the compliment(s)'

def accept_complaint(modeladmin, request, queryset):
    for complaint in queryset:
        complaint.accept_complaint()
        print('Complaint for', complaint.sender.username, 'accepted')
accept_complaint.short_description = 'Accept the complaint(s)'

def deny_complaint(modeladmin, request, queryset):
    for complaint in queryset:
        complaint.deny_complaint()
        if not complaint.sender:
            complaint.delete()
        print('Compliment for', complaint.sender.username, 'denied')
deny_complaint.short_description = 'Deny the complaint(s)'

class ReportAdmin(admin.ModelAdmin):
    list_display = ['snitch', 'complainee', 'report_body', 'is_disputed', 'dispute_body']
    ordering = ['-time_reported']
    actions = [accept_report, deny_report]

class ComplimentAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'body']
    actions = [accept_compliment, deny_compliment]

    def get_queryset(self, request):
        return super(ComplimentAdmin, self).get_queryset(request)

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'complaint_body', 'dispute_body', 'is_disputed']
    actions = [accept_complaint, deny_complaint]

    def get_queryset(self, request):
        return super(ComplaintAdmin, self).get_queryset(request)

"""@admin.Register(Chef)
class DesignatedChef(admin.UserAdmin):"""


admin.site.site_header = 'Los Tres Locos'
admin.site.register(Customer)
admin.site.register(Post)
admin.site.register(Report, ReportAdmin)
admin.site.register(Dish)
admin.site.register(Chef)
admin.site.register(DeliveryPerson)
admin.site.register(Compliments, ComplimentAdmin)
admin.site.register(Complaints, ComplaintAdmin)
admin.site.register(Orders)
admin.site.register(TabooWords)
