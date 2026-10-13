from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile

from .forms import CertificationForm, ProjectForm, SkillForm

# kind -> (form class, related name on the user, max items, label)
KINDS = {
    "skill": (SkillForm, "skills", 30, "skill"),
    "project": (ProjectForm, "projects", 10, "project"),
    "certification": (CertificationForm, "certifications", 10, "certification"),
}


def student_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or str(profile.role).lower() != "student":
            messages.error(request, "The skill profile is only available to student accounts.")
            return redirect("accounts:dashboard")
        return view(request, *args, **kwargs)

    return login_required(wrapper)


def _render(request, **forms):
    user = request.user
    skills = sorted(
        user.skills.all(),
        key=lambda s: (not s.is_verified, -(s.verified_score or 0), -s.level, s.name.lower()),
    )
    projects = list(user.projects.all())
    certifications = list(user.certifications.all())
    verified = [s for s in skills if s.is_verified]

    checklist = [
        {"label": "Add at least 3 skills", "done": len(skills) >= 3},
        {"label": "Add a project", "done": bool(projects)},
        {"label": "Add a certification", "done": bool(certifications)},
        {"label": "Get a skill verified by an assessment", "done": bool(verified)},
    ]
    done = sum(item["done"] for item in checklist)

    return render(
        request,
        "skillprofile/profile.html",
        {
            "role": "student",
            "nav_active": "skills",
            "skills": skills,
            "projects": projects,
            "certifications": certifications,
            "verified_count": len(verified),
            "checklist": checklist,
            "strength": round(100 * done / len(checklist)),
            "skill_form": forms.get("skill_form") or SkillForm(student=user),
            "project_form": forms.get("project_form") or ProjectForm(),
            "certification_form": forms.get("certification_form") or CertificationForm(),
        },
    )


@student_required
def skill_profile(request):
    return _render(request)


@student_required
@require_POST
def add_item(request, kind):
    if kind not in KINDS:
        raise Http404
    form_class, related, limit, label = KINDS[kind]

    if getattr(request.user, related).count() >= limit:
        messages.error(request, f"You can add up to {limit} {related}. Remove one first.")
        return redirect("skillprofile:profile")

    form_kwargs = {"student": request.user} if kind == "skill" else {}
    form = form_class(request.POST, **form_kwargs)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.student = request.user
        obj.save()
        messages.success(request, f"Added {label}: {form.cleaned_data.get('name') or form.cleaned_data.get('title')}.")
        return redirect("skillprofile:profile")

    return _render(request, **{f"{kind}_form": form})


@student_required
@require_POST
def delete_item(request, kind, pk):
    if kind not in KINDS:
        raise Http404
    _, related, _, label = KINDS[kind]
    obj = get_object_or_404(getattr(request.user, related), pk=pk)
    obj.delete()
    messages.success(request, f"Removed {label}.")
    return redirect("skillprofile:profile")