from django.contrib import admin

from .models import Certification, Project, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "student", "level", "verified_score")
    list_filter = ("level",)
    search_fields = ("name", "student__email")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "created_at")
    search_fields = ("title", "student__email")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "issuer", "year", "student")
    search_fields = ("name", "issuer", "student__email")