from datetime import timedelta

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Avg, Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from internships.models import Application, Company, Internship, Interview

from .forms import EmailAuthenticationForm, RegistrationForm
from .models import Profile


class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    http_method_names = ["post"]
    next_page = reverse_lazy("accounts:login")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("accounts:dashboard")

    return render(request, "accounts/register.html", {"form": form})


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

# Pipeline labels come from the model so the two can never drift apart.
STAGES = [label for value, label in Application.Stage.choices if value != Application.Stage.REJECTED]


def build_journey(current_stage):
    """Turn a stage label into [{label, state}] where state is done / current / todo."""
    if current_stage not in STAGES:
        return None
    idx = STAGES.index(current_stage)
    return [
        {"label": label, "state": "done" if i < idx else "current" if i == idx else "todo"}
        for i, label in enumerate(STAGES)
    ]


def _skill_set(text):
    return {s.strip().lower() for s in str(text or "").split(",") if s.strip()}


def _match_percent(student_skills, internship_skills):
    """Share of the internship's required skills the student has. None if unknown."""
    if not student_skills or not internship_skills:
        return None
    return round(100 * len(student_skills & internship_skills) / len(internship_skills))


def student_context(user, profile):
    applications = Application.objects.filter(student=user).select_related("internship__company")
    now = timezone.now()
    today = timezone.localdate()

    avg_score = applications.aggregate(avg=Avg("test_score"))["avg"]
    upcoming_qs = Interview.objects.filter(
        application__student=user, scheduled_at__gte=now
    ).select_related("application__internship__company")[:4]

    # Journey: the most recent application that is still alive.
    latest = applications.exclude(stage=Application.Stage.REJECTED).first()
    journey = None
    if latest:
        journey = {
            "title": latest.internship.title,
            "company": latest.internship.company.name,
            "steps": build_journey(latest.get_stage_display()),
        }

    # Recommendations: open internships the student hasn't applied to yet.
    # Matching uses Profile.skills (comma-separated) if that field exists.
    student_skills = _skill_set(getattr(profile, "skills", ""))
    applied_ids = applications.values_list("internship_id", flat=True)
    open_internships = (
        Internship.objects.filter(status=Internship.Status.OPEN, company__is_approved=True)
        .exclude(id__in=applied_ids)
        .exclude(deadline__lt=today)
        .select_related("company")[:20]
    )
    recommended = [
        {
            "id": i.id,
            "title": i.title,
            "company": i.company.name,
            "location": i.location or "—",
            "mode": i.get_mode_display(),
            "skills": i.skill_list,
            "match": _match_percent(student_skills, _skill_set(i.skills)),
        }
        for i in open_internships
    ]
    recommended.sort(key=lambda r: (r["match"] is None, -(r["match"] or 0)))

    return {
        "stats": [
            {"label": "Applications", "value": applications.count(), "hint": "Total submitted"},
            {"label": "Problems solved", "value": 0, "hint": "Coming with the coding module"},
            {"label": "Skill score", "value": round(avg_score) if avg_score is not None else 0, "hint": "Average test score"},
            {"label": "Interviews", "value": Interview.objects.filter(application__student=user, scheduled_at__gte=now).count(), "hint": "Upcoming"},
        ],
        "journey": journey,
        "recommended": recommended[:5],
        "upcoming": [
            {
                "day": timezone.localtime(i.scheduled_at).strftime("%d"),
                "month": timezone.localtime(i.scheduled_at).strftime("%b"),
                "title": f"Interview: {i.application.internship.title}",
                "detail": f"{i.application.internship.company.name} · {timezone.localtime(i.scheduled_at).strftime('%I:%M %p')}",
            }
            for i in upcoming_qs
        ],
        "applications": [
            {
                "title": a.internship.title,
                "company": a.internship.company.name,
                "applied_on": a.applied_at,
                "status": a.get_stage_display(),
            }
            for a in applications[:10]
        ],
        "skills": [],  # filled in once the coding-assessment module exists
    }


def company_context(user, profile):
    company = Company.objects.filter(owner=user).first()
    funnel = [{"stage": s, "count": 0} for s in STAGES]
    empty = {
        "stats": [
            {"label": "Active internships", "value": 0, "hint": "Currently open"},
            {"label": "Applicants", "value": 0, "hint": "All listings"},
            {"label": "Tests pending", "value": 0, "hint": "Awaiting review"},
            {"label": "Shortlisted", "value": 0, "hint": "Ready for interview"},
        ],
        "funnel": funnel,
        "internships": [],
        "applicants": [],
    }
    if company is None:
        return empty

    apps = Application.objects.filter(internship__company=company)
    counts = {row["stage"]: row["n"] for row in apps.values("stage").annotate(n=Count("id"))}
    labels = dict(Application.Stage.choices)
    funnel = [
        {"stage": label, "count": counts.get(value, 0)}
        for value, label in Application.Stage.choices
        if value != Application.Stage.REJECTED
    ]

    internships = company.internships.annotate(applicants=Count("applications"))[:8]
    recent = apps.select_related("student", "internship")[:6]

    return {
        "stats": [
            {"label": "Active internships", "value": company.internships.filter(status=Internship.Status.OPEN).count(), "hint": "Currently open"},
            {"label": "Applicants", "value": apps.count(), "hint": "All listings"},
            {"label": "Tests pending", "value": counts.get(Application.Stage.TEST_COMPLETED, 0), "hint": "Awaiting review"},
            {"label": "Shortlisted", "value": counts.get(Application.Stage.SHORTLISTED, 0), "hint": "Ready for interview"},
        ],
        "funnel": funnel,
        "internships": [
            {"title": i.title, "applicants": i.applicants, "deadline": i.deadline, "status": i.get_status_display()}
            for i in internships
        ],
        "applicants": [
            {
                "id": a.id,
                "name": a.student.get_full_name() or a.student.email,
                "role": a.internship.title,
                "score": a.test_score if a.test_score is not None else "—",
                "stage": labels[a.stage],
            }
            for a in recent
        ],
    }


def admin_context(user, profile):
    User = get_user_model()
    week_ago = timezone.now() - timedelta(days=7)
    pending = Company.objects.filter(is_approved=False).select_related("owner")[:6]
    recent_apps = Application.objects.select_related("student", "internship__company")[:8]

    return {
        "stats": [
            {"label": "Users", "value": User.objects.filter(is_staff=False).count(), "hint": "Registered"},
            {"label": "Companies", "value": Company.objects.filter(is_approved=True).count(), "hint": "Approved"},
            {"label": "Internships", "value": Internship.objects.count(), "hint": "Listed"},
            {"label": "Applications", "value": Application.objects.filter(applied_at__gte=week_ago).count(), "hint": "This week"},
        ],
        "pending_companies": [
            {"name": c.name, "email": c.owner.email, "registered_on": c.created_at} for c in pending
        ],
        "problems": [],  # filled in once the question bank exists
        "activity": [
            {
                "text": f"{a.student.get_full_name() or a.student.email} applied to {a.internship.title} at {a.internship.company.name}",
                "when": a.applied_at,
            }
            for a in recent_apps
        ],
    }


@login_required
def dashboard(request):
    profile = Profile.objects.filter(user=request.user).first()
    # Adjust the keys below if your Profile.role values are different.
    role = str(profile.role).lower() if profile else "admin"

    builders = {"student": student_context, "company": company_context, "admin": admin_context}
    ctx = builders.get(role, admin_context)(request.user, profile)
    ctx.update({"role": role, "profile": profile})
    return render(request, "accounts/dashboard.html", ctx)