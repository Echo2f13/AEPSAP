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
from case_details.models import Cc_person
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
                    print("user created")
                    care_data = Cc_person.objects.create(
                        cc_gov_id=gov_id,
                        phone_number=phone,
                        user_cc=user,
                    )
                    care_data.save()
                    print("cc created")
                    print("data received")
                    c_id_data = Cc_person.objects.filter(cc_gov_id=gov_id).first()
                    c_id = c_id_data.cc_id
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
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        incorrect_credentials = 0
        user_data = User.objects.filter(username=username).first()
        c_id_data = Cc_person.objects.filter(user_cc=user_data).first()
        # print(c_id_data)
        # c_id = c_id_data.id

        if c_id_data:
            user = authenticate(request, username=username, password=password)
            print(user)
            if User.objects.filter(username=username).exists():
                user_data = User.objects.filter(username=username).first()
                print("002")
                if (
                    user_data.is_active == True
                    and user_data.is_staff == False
                    and user_data.is_superuser == False
                ):
                    if user:
                        print("003")
                        auth_login(request, user)
                        print("logged in after 003")
                        return redirect("care_profile", pk=c_id_data.user_cc_id)
                        # return render(
                        #     request,
                        #     "customer_care/care.html",
                        #     {
                        #         "user": User.objects.filter(username=username),
                        #         "dri": Driver.objects.filter(user_driver=user_data),
                        #     },
                        # )
                    else:
                        print("004")
                        print("NOT logged in after 004")
                        return render(
                            request,
                            "customer_care\login.html",
                        )
                else:
                    if user:
                        print("005")
                        print("not logged in after 004")
                        return render(
                            request,
                            "customer_care\login.html",
                        )
                    else:
                        print("006")
                        return render(
                            request,
                            "customer_care\login.html",
                        )
            else:
                # incorrect_credentials = 1
                return render(
                    request,
                    "customer_care\login.html",
                )
        else:
            print("passes else last")
            return render(
                request,
                "customer_care\login.html",
            )

    # cou = CourseData.objects.all().values()
    return render(request, "customer_care\login.html")


def profile(request, pk):
    return render(
        request,
        "customer_care/care_profile.html",
        {
            "user": User.objects.filter(id=pk),
            "dri": Cc_person.objects.filter(user_cc=pk),
        },
    )


def logout(request):
    print("logout1")
    auth_logout(request)
    print("logout2")
    return render(request, "driver\login.html")
