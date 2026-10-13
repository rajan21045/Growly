from django.conf import settings
from django.db import models
from django.utils import timezone


class Company(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company"
    )
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Internship(models.Model):
    class Mode(models.TextChoices):
        ONSITE = "onsite", "On-site"
        REMOTE = "remote", "Remote"
        HYBRID = "hybrid", "Hybrid"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="internships")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.ONSITE)
    skills = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated, e.g. PHP, MySQL, JavaScript"
    )
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} · {self.company.name}"

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    @property
    def accepts_applications(self):
        if self.status != self.Status.OPEN:
            return False
        return self.deadline is None or self.deadline >= timezone.localdate()


class Application(models.Model):
    class Stage(models.TextChoices):
        APPLIED = "applied", "Applied"
        TEST_ASSIGNED = "test_assigned", "Test Assigned"
        TEST_COMPLETED = "test_completed", "Test Completed"
        SHORTLISTED = "shortlisted", "Shortlisted"
        INTERVIEW = "interview", "Interview"
        SELECTED = "selected", "Selected"
        REJECTED = "rejected", "Rejected"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="applications")
    cover_note = models.TextField(blank=True)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.APPLIED)
    test_score = models.PositiveSmallIntegerField(null=True, blank=True, help_text="0-100")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "internship"], name="unique_application")
        ]

    def __str__(self):
        return f"{self.student} → {self.internship}"


class Interview(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews")
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, help_text="Address or meeting link")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"Interview for {self.application} on {self.scheduled_at:%Y-%m-%d %H:%M}"