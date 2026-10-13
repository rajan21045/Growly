from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Lower


class Skill(models.Model):
    class Level(models.IntegerChoices):
        BEGINNER = 1, "Beginner"
        INTERMEDIATE = 2, "Intermediate"
        ADVANCED = 3, "Advanced"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=60)
    level = models.PositiveSmallIntegerField(choices=Level.choices, default=Level.BEGINNER)
    verified_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(100)],
        help_text="0-100. Filled in by coding assessments once that module exists.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(Lower("name"), "student", name="unique_skill_per_student")
        ]

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    @property
    def is_verified(self):
        return self.verified_score is not None


class Project(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    tech = models.CharField(max_length=200, blank=True, help_text="Comma-separated, e.g. PHP, MySQL")
    url = models.URLField(blank=True, verbose_name="Link")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def tech_list(self):
        return [t.strip() for t in self.tech.split(",") if t.strip()]


class Certification(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=120)
    year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1990), MaxValueValidator(2100)])
    url = models.URLField(blank=True, verbose_name="Credential link")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "name"]

    def __str__(self):
        return f"{self.name} · {self.issuer}"