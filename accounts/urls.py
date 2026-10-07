from django.urls import path

from .views import AccountLogoutView, EmailLoginView, dashboard, register

app_name = "accounts"

urlpatterns = [
    path("", EmailLoginView.as_view(), name="login"),
    path("register/", register, name="register"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
]
