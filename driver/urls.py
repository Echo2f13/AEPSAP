from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.signup, name="driver_signup"),
    path("email_verify/", views.VerifyEmail.as_view(), name="email_verify"),
    path("login/", views.login, name="driver_login"),
    path("dashboard/<int:pk>", views.dashboard, name="driver_dashboard"),
    path("case/<int:pk>", views.case, name="driver_case"),
    path("h_and_a/<int:pk>", views.h_and_a, name="driver_h_and_a"),
    path("profile/<int:pk>", views.profile, name="driver_profile"),
    path("edit_profile", views.edit_profile, name="edit_profile_driver"),
    path(
        "remove_profile_image_driver",
        views.remove_profile_image_driver,
        name="remove_profile_image_driver",
    ),
    path("change_pass", views.driver_change_pass, name="driver_change_pass"),
    path("logout/", views.logout, name="driver_logout"),

    path('toggle_tracking/', views.toggle_tracking, name='toggle_tracking'),
    path('update_location/', views.update_location, name='update_location'),
    path('driver/update_location/', views.update_location, name='driver_location_endpoint'),
]
