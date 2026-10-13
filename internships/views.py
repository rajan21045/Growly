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