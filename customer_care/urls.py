from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login, name="care_login"),
    path("signup/", views.signup, name="care_signup"),
    path("dashboard/<int:pk>", views.dashboard, name="care_dashboard"),
    path("case/<int:pk>", views.care_case, name="care_case"),
    path("ambulance/<int:pk>", views.care_ambulance, name="care_ambulance"),
    path('add-ambulance/', views.add_ambulance, name='add_ambulance'),
    path("hospital/<int:pk>", views.care_hospital, name="care_hospital"),
    path("add-hospital/", views.add_hospital, name="add_hospital"),
    path("profile/<int:pk>", views.profile, name="care_profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path(
        "remove-profile-image/", views.remove_profile_image, name="remove_profile_image"
    ),
    path("change_pass/", views.care_change_pass, name="care_change_pass"),
    path("logout/", views.logout, name="care_logout"),
]
