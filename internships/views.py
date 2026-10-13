from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Profile

from .models import Application, Internship

# Pipeline shown on the tracker (everything except Rejected), in order.
PIPELINE = [(v, l) for v, l in Application.Stage.choices if v != Application.Stage.REJECTED]

# Tab key -> (label, stages it includes). None means every stage.
APPLICATION_TABS = [
    ("all", "All", None),
    (
        "active",
        "In progress",
        [
            Application.Stage.APPLIED,
            Application.Stage.TEST_ASSIGNED,
            Application.Stage.TEST_COMPLETED,
            Application.Stage.SHORTLISTED,
            Application.Stage.INTERVIEW,
        ],
    ),
    ("selected", "Selected", [Application.Stage.SELECTED]),
    ("rejected", "Not selected", [Application.Stage.REJECTED]),
]


def _role(user):
    """Same rule the dashboard uses: no profile means admin."""
    profile = Profile.objects.filter(user=user).first()
    role = str(profile.role).lower() if profile else "admin"
    return role, profile


@login_required
def browse(request):
    role, profile = _role(request.user)
    today = timezone.localdate()

    qs = (
        Internship.objects.filter(status=Internship.Status.OPEN, company__is_approved=True)
        .filter(Q(deadline__isnull=True) | Q(deadline__gte=today))
        .select_related("company")
    )

    q = request.GET.get("q", "").strip()
    mode = request.GET.get("mode", "")
    sort = request.GET.get("sort", "newest")

    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(company__name__icontains=q)
            | Q(skills__icontains=q)
            | Q(location__icontains=q)
        )
    if mode in Internship.Mode.values:
        qs = qs.filter(mode=mode)
    else:
        mode = ""

    if sort == "deadline":
        qs = qs.order_by(F("deadline").asc(nulls_last=True), "-created_at")
    else:
        sort = "newest"
        qs = qs.order_by("-created_at")

    paginator = Paginator(qs, 9)
    page = paginator.get_page(request.GET.get("page"))

    applied_ids = set()
    if role == "student":
        applied_ids = set(
            Application.objects.filter(student=request.user).values_list("internship_id", flat=True)
        )

    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request,
        "internships/browse.html",
        {
            "role": role,
            "profile": profile,
            "nav_active": "internships",
            "page": page,
            "cards": [{"obj": i, "applied": i.id in applied_ids} for i in page],
            "total": paginator.count,
            "q": q,
            "mode": mode,
            "sort": sort,
            "modes": Internship.Mode.choices,
            "querystring": params.urlencode(),
        },
    )


@login_required
def detail(request, pk):
    role, profile = _role(request.user)
    internship = get_object_or_404(Internship.objects.select_related("company"), pk=pk)

    # Unapproved companies' listings are visible only to their owner and admins.
    if not internship.company.is_approved and role != "admin" and internship.company.owner != request.user:
        raise Http404

    application = None
    if role == "student":
        application = Application.objects.filter(student=request.user, internship=internship).first()

    return render(
        request,
        "internships/detail.html",
        {
            "role": role,
            "profile": profile,
            "nav_active": "internships",
            "internship": internship,
            "application": application,
        },
    )


@login_required
@require_POST
def apply(request, pk):
    role, _ = _role(request.user)
    internship = get_object_or_404(Internship.objects.select_related("company"), pk=pk)

    if role != "student":
        messages.error(request, "Only student accounts can apply for internships.")
    elif not internship.company.is_approved or not internship.accepts_applications:
        messages.error(request, "This internship is no longer accepting applications.")
    else:
        _, created = Application.objects.get_or_create(
            student=request.user,
            internship=internship,
            defaults={"cover_note": request.POST.get("cover_note", "").strip()[:1000]},
        )
        if created:
            messages.success(request, f"Application sent to {internship.company.name}.")
        else:
            messages.info(request, "You have already applied to this internship.")

    return redirect("internships:detail", pk=pk)


def _journey(stage):
    """[{label, state}] for the tracker, or None if the stage is not on the pipeline."""
    values = [v for v, _ in PIPELINE]
    if stage not in values:
        return None
    idx = values.index(stage)
    return [
        {"label": label, "state": "done" if i < idx else "current" if i == idx else "todo"}
        for i, (_, label) in enumerate(PIPELINE)
    ]


@login_required
def my_applications(request):
    role, _ = _role(request.user)
    if role != "student":
        messages.error(request, "Only student accounts have applications.")
        return redirect("accounts:dashboard")

    base_qs = (
        Application.objects.filter(student=request.user)
        .select_related("internship__company")
        .prefetch_related("interviews")
    )

    keys = {key: stages for key, _, stages in APPLICATION_TABS}
    current = request.GET.get("status", "all")
    if current not in keys:
        current = "all"

    tabs = [
        {
            "key": key,
            "label": label,
            "count": base_qs.count() if stages is None else base_qs.filter(stage__in=stages).count(),
        }
        for key, label, stages in APPLICATION_TABS
    ]

    qs = base_qs if keys[current] is None else base_qs.filter(stage__in=keys[current])

    now = timezone.now()
    items = []
    for a in qs:
        upcoming = [i for i in a.interviews.all() if i.scheduled_at >= now]
        items.append(
            {
                "obj": a,
                "steps": _journey(a.stage),
                "next_interview": upcoming[0] if upcoming else None,
                "can_withdraw": a.stage == Application.Stage.APPLIED,
            }
        )

    return render(
        request,
        "internships/my_applications.html",
        {
            "role": role,
            "nav_active": "applications",
            "items": items,
            "tabs": tabs,
            "current": current,
        },
    )


@login_required
@require_POST
def withdraw(request, pk):
    role, _ = _role(request.user)
    if role != "student":
        messages.error(request, "Only student accounts have applications.")
        return redirect("accounts:dashboard")

    application = get_object_or_404(Application, pk=pk, student=request.user)
    if application.stage != Application.Stage.APPLIED:
        messages.error(request, "You can only withdraw an application that has not been reviewed yet.")
    else:
        title = application.internship.title
        application.delete()
        messages.success(request, f"Withdrew your application to {title}.")
    return redirect("internships:my_applications")