from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile

from .forms import ApplicationUpdateForm, CompanyForm, InternshipForm, InterviewForm
from .models import Application, Company, Internship, Interview
from .views import _journey

# Scheduling an interview moves an application in one of these stages to "Interview".
BEFORE_INTERVIEW = [
    Application.Stage.APPLIED,
    Application.Stage.TEST_ASSIGNED,
    Application.Stage.TEST_COMPLETED,
    Application.Stage.SHORTLISTED,
]


def company_view(view=None, *, need_company=True):
    """Company accounts only. The view receives the Company as its second argument.

    With need_company=False (the profile page) the company may be None.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            profile = Profile.objects.filter(user=request.user).first()
            if not profile or str(profile.role).lower() != "company":
                messages.error(request, "This page is only available to company accounts.")
                return redirect("accounts:dashboard")

            company = Company.objects.filter(owner=request.user).first()
            if company is None and need_company:
                messages.info(request, "Set up your company profile to get started.")
                return redirect("internships:company_profile")
            return func(request, company, *args, **kwargs)

        return login_required(wrapper)

    return decorator(view) if view else decorator


def _ctx(company, nav_active, **extra):
    return {"role": "company", "nav_active": nav_active, "company": company, **extra}


# ---------------------------------------------------------------------------
# Company profile
# ---------------------------------------------------------------------------


@company_view(need_company=False)
def company_profile(request, company):
    form = CompanyForm(request.POST or None, instance=company)
    if request.method == "POST" and form.is_valid():
        created = company is None
        obj = form.save(commit=False)
        obj.owner = request.user
        obj.save()
        if created:
            messages.success(request, "Company profile created. An admin must approve it before your internships go live.")
            return redirect("internships:manage_internships")
        messages.success(request, "Company profile saved.")
        return redirect("internships:company_profile")

    return render(request, "internships/company/profile.html", _ctx(company, "company_profile", form=form))


# ---------------------------------------------------------------------------
# Internships
# ---------------------------------------------------------------------------


@company_view
def manage_internships(request, company):
    internships = company.internships.annotate(applicant_count=Count("applications"))
    return render(
        request,
        "internships/company/internships.html",
        _ctx(company, "manage", internships=internships),
    )


@company_view
def internship_create(request, company):
    form = InternshipForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.company = company
        obj.save()
        messages.success(request, f"Posted: {obj.title}.")
        return redirect("internships:manage_internships")

    return render(
        request,
        "internships/company/internship_form.html",
        _ctx(company, "manage", form=form, editing=False),
    )


@company_view
def internship_edit(request, company, pk):
    internship = get_object_or_404(Internship, pk=pk, company=company)
    form = InternshipForm(request.POST or None, instance=internship)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Internship updated.")
        return redirect("internships:manage_internships")

    return render(
        request,
        "internships/company/internship_form.html",
        _ctx(company, "manage", form=form, editing=True, internship=internship),
    )


@require_POST
@company_view
def internship_toggle(request, company, pk):
    internship = get_object_or_404(Internship, pk=pk, company=company)
    if internship.status == Internship.Status.OPEN:
        internship.status = Internship.Status.CLOSED
        messages.success(request, f"Closed: {internship.title}. Students can no longer apply.")
    else:
        internship.status = Internship.Status.OPEN
        messages.success(request, f"Reopened: {internship.title}.")
    internship.save(update_fields=["status"])
    return redirect("internships:manage_internships")


# ---------------------------------------------------------------------------
# Applicants
# ---------------------------------------------------------------------------


@company_view
def applicants(request, company):
    qs = Application.objects.filter(internship__company=company).select_related("student", "internship")

    internship_id = request.GET.get("internship", "")
    stage = request.GET.get("stage", "")
    q = request.GET.get("q", "").strip()

    if internship_id.isdigit():
        qs = qs.filter(internship_id=int(internship_id))
    else:
        internship_id = ""

    if stage in Application.Stage.values:
        qs = qs.filter(stage=stage)
    else:
        stage = ""

    if q:
        qs = qs.filter(
            Q(student__first_name__icontains=q)
            | Q(student__last_name__icontains=q)
            | Q(student__email__icontains=q)
        )

    paginator = Paginator(qs.order_by("-applied_at"), 12)
    page = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request,
        "internships/company/applicants.html",
        _ctx(
            company,
            "applicants",
            page=page,
            total=paginator.count,
            q=q,
            stage=stage,
            internship_id=internship_id,
            stages=Application.Stage.choices,
            internship_options=company.internships.all(),
            querystring=params.urlencode(),
        ),
    )


def _detail_response(request, company, application, update_form=None, interview_form=None):
    student = application.student
    # Read the stage from the database: a failed form submit may have changed the in-memory copy.
    stage = Application.objects.filter(pk=application.pk).values_list("stage", flat=True).first()

    return render(
        request,
        "internships/company/applicant_detail.html",
        _ctx(
            company,
            "applicants",
            application=application,
            student=student,
            stage_label=dict(Application.Stage.choices)[stage],
            steps=_journey(stage),
            skills=student.skills.all(),
            projects=student.projects.all(),
            certifications=student.certifications.all(),
            interviews=application.interviews.all(),
            update_form=update_form or ApplicationUpdateForm(instance=application),
            interview_form=interview_form or InterviewForm(),
        ),
    )


@company_view
def applicant_detail(request, company, pk):
    application = get_object_or_404(
        Application.objects.select_related("student", "internship"), pk=pk, internship__company=company
    )

    if request.method == "POST":
        form = ApplicationUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated.")
            return redirect("internships:applicant_detail", pk=pk)
        return _detail_response(request, company, application, update_form=form)

    return _detail_response(request, company, application)


@require_POST
@company_view
def schedule_interview(request, company, pk):
    application = get_object_or_404(
        Application.objects.select_related("student", "internship"), pk=pk, internship__company=company
    )

    form = InterviewForm(request.POST)
    if form.is_valid():
        interview = form.save(commit=False)
        interview.application = application
        interview.save()
        if application.stage in BEFORE_INTERVIEW:
            application.stage = Application.Stage.INTERVIEW
            application.save(update_fields=["stage", "updated_at"])
        messages.success(request, "Interview scheduled.")
        return redirect("internships:applicant_detail", pk=pk)

    return _detail_response(request, company, application, interview_form=form)


@require_POST
@company_view
def cancel_interview(request, company, pk):
    interview = get_object_or_404(Interview, pk=pk, application__internship__company=company)
    application_pk = interview.application_id
    interview.delete()
    messages.success(request, "Interview cancelled.")
    return redirect("internships:applicant_detail", pk=application_pk)