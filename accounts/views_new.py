from django.contrib.auth.decorators import login_required
from django.shortcuts import render

STAGES = ["Applied", "Test Assigned", "Test Completed", "Shortlisted", "Interview", "Selected"]


def build_journey(current_stage):
    """Turn a stage name into [{label, state}] where state is done / current / todo."""
    if current_stage not in STAGES:
        return None
    idx = STAGES.index(current_stage)
    steps = []
    for i, label in enumerate(STAGES):
        state = "done" if i < idx else "current" if i == idx else "todo"
        steps.append({"label": label, "state": state})
    return steps


def student_context(user):
    # TODO: replace the empty values with real queries, e.g.
    #   applications = Application.objects.filter(student=user).select_related("internship__company")
    return {
        "stats": [
            {"label": "Applications", "value": 0, "hint": "Total submitted"},
            {"label": "Problems solved", "value": 0, "hint": "Across all difficulties"},
            {"label": "Skill score", "value": 0, "hint": "Out of 100"},
            {"label": "Interviews", "value": 0, "hint": "Upcoming"},
        ],
        # {"title": "Frontend Intern", "company": "Acme", "steps": build_journey("Test Completed")}
        "journey": None,
        # {"title", "company", "location", "mode", "match", "skills": ["PHP", "MySQL"]}
        "recommended": [],
        # {"day": "16", "month": "Oct", "title": "Timed coding test", "detail": "Acme · 60 min"}
        "upcoming": [],
        # {"title", "company", "applied_on", "status"}  (status = one of STAGES or "Rejected")
        "applications": [],
        # {"name": "JavaScript", "score": 82, "verified": True}
        "skills": [],
    }


def company_context(user):
    return {
        "stats": [
            {"label": "Active internships", "value": 0, "hint": "Currently open"},
            {"label": "Applicants", "value": 0, "hint": "All listings"},
            {"label": "Tests pending", "value": 0, "hint": "Awaiting review"},
            {"label": "Shortlisted", "value": 0, "hint": "Ready for interview"},
        ],
        # {"stage": "Applied", "count": 12}  -> one per entry in STAGES
        "funnel": [{"stage": s, "count": 0} for s in STAGES],
        # {"title", "applicants", "deadline", "status"}
        "internships": [],
        # {"name", "role", "score", "stage"}
        "applicants": [],
    }


def admin_context(user):
    return {
        "stats": [
            {"label": "Students", "value": 0, "hint": "Registered"},
            {"label": "Companies", "value": 0, "hint": "Approved"},
            {"label": "Internships", "value": 0, "hint": "Listed"},
            {"label": "Submissions", "value": 0, "hint": "This week"},
        ],
        # {"name", "email", "registered_on"}
        "pending_companies": [],
        # {"title", "difficulty", "tag", "submissions"}
        "problems": [],
        # {"text", "when"}
        "activity": [],
    }


@login_required
def dashboard(request):
    profile = getattr(request.user, "profile", None)
    role = profile.role if profile else "admin"  # adjust to your role values

    builders = {"student": student_context, "company": company_context, "admin": admin_context}
    ctx = builders.get(role, admin_context)(request.user)
    ctx.update({"role": role, "profile": profile})
    return render(request, "accounts/dashboard.html", ctx)