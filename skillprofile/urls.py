from django.urls import path

from . import views

app_name = "skillprofile"

urlpatterns = [
    path("", views.skill_profile, name="profile"),
    path("add/<slug:kind>/", views.add_item, name="add"),
    path("delete/<slug:kind>/<int:pk>/", views.delete_item, name="delete"),
]