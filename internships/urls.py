from django.urls import path

from . import company_views, views

app_name = "internships"

urlpatterns = [
    # Students
    path("", views.browse, name="browse"),
    path("applications/", views.my_applications, name="my_applications"),
    path("applications/<int:pk>/withdraw/", views.withdraw, name="withdraw"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/apply/", views.apply, name="apply"),
    # Companies
    path("company/profile/", company_views.company_profile, name="company_profile"),
    path("company/internships/", company_views.manage_internships, name="manage_internships"),
    path("company/internships/new/", company_views.internship_create, name="internship_create"),
    path("company/internships/<int:pk>/edit/", company_views.internship_edit, name="internship_edit"),
    path("company/internships/<int:pk>/toggle/", company_views.internship_toggle, name="internship_toggle"),
    path("company/applicants/", company_views.applicants, name="applicants"),
    path("company/applicants/<int:pk>/", company_views.applicant_detail, name="applicant_detail"),
    path("company/applicants/<int:pk>/interview/", company_views.schedule_interview, name="schedule_interview"),
    path("company/interviews/<int:pk>/cancel/", company_views.cancel_interview, name="cancel_interview"),
]