from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login, name="care_login"),
    path("signup/", views.signup, name="care_signup"),
    path("profile/<int:pk>", views.profile, name="care_profile"),
    path("logout/", views.logout, name="care_logout"),
]
