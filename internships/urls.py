from django.urls import path

from . import views

app_name = "internships"

urlpatterns = [
    path("", views.browse, name="browse"),
    path("applications/", views.my_applications, name="my_applications"),
    path("applications/<int:pk>/withdraw/", views.withdraw, name="withdraw"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/apply/", views.apply, name="apply"),
]