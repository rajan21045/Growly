from django import forms
from django.utils import timezone

from .models import Application, Company, Internship, Interview


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "location", "website", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Acme Technologies"}),
            "location": forms.TextInput(attrs={"placeholder": "City, Country"}),
            "website": forms.URLInput(attrs={"placeholder": "https://..."}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "What does your company do?"}),
        }


class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ["title", "description", "location", "mode", "skills", "deadline"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Frontend Developer Intern"}),
            "description": forms.Textarea(attrs={"rows": 7, "placeholder": "What will the intern work on? What are you looking for?"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Kathmandu or Remote"}),
            "skills": forms.TextInput(attrs={"placeholder": "PHP, MySQL, JavaScript"}),
            "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        unchanged = self.instance.pk and deadline == self.instance.deadline
        if deadline and deadline < timezone.localdate() and not unchanged:
            raise forms.ValidationError("The deadline can't be in the past.")
        return deadline


class ApplicationUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["stage", "test_score"]
        labels = {"stage": "Stage", "test_score": "Test score (0-100)"}
        widgets = {"test_score": forms.NumberInput(attrs={"min": 0, "max": 100, "placeholder": "Leave empty if none"})}

    def clean_test_score(self):
        score = self.cleaned_data.get("test_score")
        if score is not None and not 0 <= score <= 100:
            raise forms.ValidationError("Enter a score between 0 and 100.")
        return score


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ["scheduled_at", "location", "notes"]
        labels = {"scheduled_at": "Date and time", "location": "Location or meeting link"}
        widgets = {
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "location": forms.TextInput(attrs={"placeholder": "Office address or video link"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Anything the candidate should prepare?"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scheduled_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"]

    def clean_scheduled_at(self):
        when = self.cleaned_data["scheduled_at"]
        if when < timezone.now():
            raise forms.ValidationError("Pick a time in the future.")
        return when