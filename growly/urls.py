from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("internships/", include("internships.urls")),
    path("skill-profile/", include("skillprofile.urls")),
]
