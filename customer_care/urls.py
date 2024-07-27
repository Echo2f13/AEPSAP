from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login, name="care_login"),
    path("signup/", views.signup, name="care_signup"),
    path("dashboard/<int:pk>", views.dashboard, name="care_dashboard"),
    path("case/<int:pk>", views.care_case, name="care_case"),
    path("ambulance/<int:pk>", views.care_ambulance, name="care_ambulance"),
    path("hospital/<int:pk>", views.care_hospital, name="care_hospital"),
    path("profile/<int:pk>", views.profile, name="care_profile"),
    path("change_pass/", views.care_change_pass, name="care_change_pass"),
    path("logout/", views.logout, name="care_logout"),
]
