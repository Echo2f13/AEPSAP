from django.urls import path
from . import views


urlpatterns = [
    path("case_id/", views.case_id, name="case_id"),
    path("case_id/<int:pk>", views.case_page, name="case_page"),
    path('update_ambulance_location/<int:pk>/', views.update_ambulance_location, name='update_ambulance_location'),
]
