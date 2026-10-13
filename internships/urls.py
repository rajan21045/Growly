from django.urls import path

from . import views

app_name = "internships"

urlpatterns = [
    path("", views.browse, name="browse"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/apply/", views.apply, name="apply"),
]