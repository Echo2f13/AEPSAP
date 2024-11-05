from datetime import datetime, timedelta, date
from django.db import IntegrityError
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import socket
from django.contrib.sites.shortcuts import get_current_site

import jwt
from rest_framework import views
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib import messages

from django.contrib.auth.hashers import make_password, check_password

from sas import settings
from case_details.models import Driver, Case, Cc_person, Hospital
from case_details.models import User
from django.core.mail import send_mail
from sas.settings import EMAIL_HOST_USER
from django.urls import reverse


from django.shortcuts import redirect, render


is_active_verify = False


def case_id(request):
    if request.method == "POST":
        case_unique_id = request.POST["case_unique_id"]
        return redirect("case_page", pk=case_unique_id)
    return render(
        request,
        "case/case_id.html",
    )


def case_page(request, pk):
    case_data = Case.objects.filter(case_id=pk).first()
    location = case_data.location
    amb_location = case_data.ambulance.driver_1.current_location
    if location:
        location_split = location.split(",")
        location_lat = location_split[0]
        location_lng = location_split[1]
        amb_location_split = amb_location.split(",")
        amb_location_lat = amb_location_split[0]
        amb_location_lng = amb_location_split[1]
    else:
        location_lat = location_lng = None
    return render(
        request,
        "case/case.html",
        {
            "case": Case.objects.filter(case_id=pk).first(),
            "google_maps_api_key": "user you map API key here",
            "location_lat": location_lat,
            "location_lng": location_lng,
            "amb_location_lat": amb_location_lat,
            "amb_location_lng": amb_location_lng,
        },
    )


from django.http import JsonResponse


def update_ambulance_location(request, pk):
    case = Case.objects.filter(ambulance__id=pk).first()
    location = (
        case.ambulance.driver.current_location
        if case and case.ambulance.driver.is_tracking
        else "0,0"
    )
    return JsonResponse({"location": location})
