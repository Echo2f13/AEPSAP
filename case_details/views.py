from datetime import datetime, timedelta, date
from django.db import IntegrityError
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import socket
from django.contrib.sites.shortcuts import get_current_site

# from .models import User
import jwt
from rest_framework import views
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib import messages

from django.contrib.auth.hashers import make_password, check_password

from sas import settings
from case_details.models import Driver, Driver, Case, Cc_person, Hospital
from case_details.models import User
from django.core.mail import send_mail
from sas.settings import EMAIL_HOST_USER
from django.urls import reverse

# Fileresponse, io and report_lab for PDF generation
import io
from django.http import HttpResponse, FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import Image
import pandas as pd
import smtplib


from django.template import loader
from django.shortcuts import redirect, render

from datetime import datetime, timedelta

# to create xl sheet
import xlsxwriter


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
    if location:
        location_split = location.split(',')
        location_lat = location_split[0]
        location_lng = location_split[1]
    else:
        location_lat = location_lng = None
    return render(
        request,
        "case/case.html",
        {
            "case": Case.objects.filter(case_id=pk).first(),
            "google_maps_api_key": "AIzaSyCfs2EPBwjylYC_6twmdwnIFXUlc5LkaH0",
            "location_lat" : location_lat,
            "location_lng" : location_lng,

        },
    )

from django.http import JsonResponse

def update_ambulance_location(request, pk):
    case = Case.objects.filter(ambulance__id=pk).first()
    location = case.ambulance.driver.current_location if case and case.ambulance.driver.is_tracking else "0,0"
    return JsonResponse({'location': location})


