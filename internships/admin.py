from django.contrib import admin

from .models import Application, Company, Interview, Internship


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "location", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("name", "owner__email")
    actions = ["approve_companies"]

    @admin.action(description="Approve selected companies")
    def approve_companies(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "mode", "status", "deadline")
    list_filter = ("status", "mode")
    search_fields = ("title", "company__name", "skills")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "internship", "stage", "test_score", "applied_at")
    list_filter = ("stage",)
    search_fields = ("student__email", "internship__title")


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "scheduled_at", "location")