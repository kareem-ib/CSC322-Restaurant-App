from django.contrib import admin
from .models import Customer, Post, Report, Dish, Chef, DeliveryPerson, Complaints, Compliments, Orders, TabooWords
from django.contrib.admin.models import LogEntry

# Register your models here.

# Allows the admin to accept a report.
def accept_report(modeladmin, request, queryset):
    for report in queryset:
        report.accept_report()
        print('Report for', report.complainee.username, "submitted")
accept_report.short_description = 'Accept the report(s)'

# Allows the admin to deny a report.
def deny_report(modeladmin, request, queryset):
    for report in queryset:
        report.deny_report()
        print('Report for', report.snitch.username, "submitted")
deny_report.short_description = 'Deny the report(s)'

# Allows the admin to accept a compliment.
def accept_compliment(modeladmin, request, queryset):
    for compliment in queryset:
        compliment.accept_compliment()
        print('Compliment for', compliment.sender.username, 'accepted')
accept_compliment.short_description = 'Accept the compliment(s)'

# Allows the admin to deny a compliment.
def deny_compliment(modeladmin, request, queryset):
    for compliment in queryset:
        compliment.deny_compliment()
        print('Compliment for', compliment.sender.username, 'denied')
deny_compliment.short_description = 'Deny the compliment(s)'

# Allows the admin to accept a complaint.
def accept_complaint(modeladmin, request, queryset):
    for complaint in queryset:
        complaint.accept_complaint()
        print('Complaint for', complaint.sender.username, 'accepted')
accept_complaint.short_description = 'Accept the complaint(s)'

# Allows the admin to deny a complaint.
def deny_complaint(modeladmin, request, queryset):
    for complaint in queryset:
        complaint.deny_complaint()
        if not complaint.sender:
            complaint.delete()
        print('Compliment for', complaint.sender.username, 'denied')
deny_complaint.short_description = 'Deny the complaint(s)'

"""
The following classes modify the respective displays on the admin page for the respective models.
"""

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

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'balance', 'is_VIP', 'quit_request']
    ordering = ['-quit_request']

# Sets the header of the admin page
admin.site.site_header = 'Los Tres Locos'

# Registers the models to be viewed on the admin page.
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Post)
admin.site.register(Report, ReportAdmin)
admin.site.register(Dish)
admin.site.register(Chef)
admin.site.register(DeliveryPerson)
admin.site.register(Compliments, ComplimentAdmin)
admin.site.register(Complaints, ComplaintAdmin)
admin.site.register(Orders)
admin.site.register(TabooWords)
