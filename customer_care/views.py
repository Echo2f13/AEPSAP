from datetime import datetime, timedelta, date
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
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
from case_details.models import cc_person
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


def signup(request):
    try:
        if request.user.is_authenticated:
            return render(request, "customer_care\login.html")
        else:
            if request.method == "POST":
                first_name = request.POST["first_name"]
                last_name = request.POST["last_name"]
                username = request.POST["username"]
                email = request.POST["email"]
                phone = request.POST["phone"]
                password = request.POST["password"]
                gov_id = request.POST["cc_gov_id"]
                # image = request.FILES['image']
                # print('image=', image)
                message1 = 0  # this will be popped when repeated email is used
                # this will be popped when user created and asked to verify email (student_login page)
                message2 = 0
                exists = User.objects.filter(email=email)
                print("user data=", exists)
                if not exists:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_active=is_active_verify,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    user.save()
                    care_data = cc_person.objects.create(
                        cc_gov_id=gov_id,
                        phone_number=phone,
                    )
                    care_data.save()
                    print("data received")
                    c_id_data = cc_person.objects.filter(cc_gov_id=gov_id).first()
                    c_id = c_id_data.id
                    print(c_id)
                    user_email = User.objects.get(email=email)
                    print(user_email)
                    refresh = RefreshToken.for_user(user_email).access_token
                    print(refresh)
                    refresh.set_exp(lifetime=timedelta(days=36500))
                    current_site = get_current_site(request).domain
                    relativeLink = reverse("email_verify")
                    print(relativeLink)
                    Email = email
                    absUrl = (
                        "http://"
                        + current_site
                        + relativeLink
                        + "?token="
                        + str(refresh)
                    )
                    Subject = " Hello " + "Verification pending"
                    Message = "Click below link to activate your account \n " + absUrl
                    send_mail(Subject, Message, EMAIL_HOST_USER, [Email])
                    print("pass1")
                    print(absUrl)
                    message2 = 1
                    return render(
                        request, "customer_care\login.html", {"message2": message2}
                    )
                else:
                    message1 = 1
                    return render(
                        request, "customer_care/signup.html", {"message1": message1}
                    )
    except IntegrityError:
        print("pass2")
        return render(
            request,
            "customer_care/signup.html",
        )
    print("pass3")
    return render(request, "customer_care/signup.html")
    # return render(request, "driver/signup.html")


def login(request):
    return render(request, "customer_care\login.html")
