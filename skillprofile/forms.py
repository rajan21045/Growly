from django import forms

from .models import Certification, Project, Skill


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "level"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "e.g. Python, PHP, MySQL"})}

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if self.student and Skill.objects.filter(student=self.student, name__iexact=name).exists():
            raise forms.ValidationError("You have already added this skill.")
        return name


class ProjectForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3, "maxlength": 500, "placeholder": "What does it do? What was your part?"}),
    )

    class Meta:
        model = Project
        fields = ["title", "description", "tech", "url"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. WhisperWall"}),
            "tech": forms.TextInput(attrs={"placeholder": "PHP, MySQL, JavaScript"}),
            "url": forms.URLInput(attrs={"placeholder": "https://github.com/..."}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["name", "issuer", "year", "url"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Responsive Web Design"}),
            "issuer": forms.TextInput(attrs={"placeholder": "e.g. freeCodeCamp"}),
            "year": forms.NumberInput(attrs={"min": 1990, "max": 2100, "placeholder": "2026"}),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }