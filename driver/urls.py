from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.signup, name="driver_signup"),
    path("email_verify/", views.VerifyEmail.as_view(), name="email_verify"),
    path("login/", views.login, name="driver_login"),
    # path("profile", views.profile, name="driver_profile"),
    path("profile/<int:pk>", views.profile, name="driver_profile"),
    path("logout/", views.logout, name="driver_logout"),
]
