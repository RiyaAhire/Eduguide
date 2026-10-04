from django.contrib import admin
from .models import AdmissionNotice, ChecklistTask, FavoriteCollege, PersonalReminder


@admin.register(AdmissionNotice)
class AdmissionNoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "academic_year", "published_on", "is_published")
    list_filter = ("academic_year", "is_published")
    search_fields = ("title", "summary")
    ordering = ("-published_on",)


@admin.register(FavoriteCollege)
class FavoriteCollegeAdmin(admin.ModelAdmin):
    list_display = ("user", "college", "saved_at")
    search_fields = ("user__username", "college__college_name", "college__college_code")


@admin.register(ChecklistTask)
class ChecklistTaskAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "completed", "updated_at")
    list_filter = ("completed",)
    search_fields = ("user__username", "title")


@admin.register(PersonalReminder)
class PersonalReminderAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "due_date", "completed")
    list_filter = ("completed", "due_date")
    search_fields = ("user__username", "title")
