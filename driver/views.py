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
from case_details.models import Driver, Driver, Case, Cc_person, Hospital, Ambulance
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
            return render(request, "driver\login.html")
        else:
            if request.method == "POST":
                first_name = request.POST["first_name"]
                last_name = request.POST["last_name"]
                email = request.POST["email"]
                # phone number is username
                phone = request.POST["phone"]
                license_number = request.POST["license_number"]
                # license_number = request.POST["licence"]
                password = request.POST["password"]
                # image = request.FILES['image']
                # print('image=', image)
                message1 = 0  # this will be popped when repeated email is used
                # this will be popped when user created and asked to verify email (student_login page)
                message2 = 0
                exists = User.objects.filter(email=email)
                print("user data=", exists)
                if not exists:
                    user = User.objects.create_user(
                        username=phone,
                        email=email,
                        password=password,
                        is_active=is_active_verify,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    user.save()
                    driver_data = Driver.objects.create(
                        user_driver=user, license_number=license_number
                    )
                    driver_data.save()
                    print("data received")
                    d_id_data = Driver.objects.filter(
                        license_number=license_number
                    ).first()
                    d_id = d_id_data.id
                    print(d_id)
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
                    return render(request, "driver\login.html", {"message2": message2})
                else:
                    message1 = 1
                    return render(request, "driver/signup.html", {"message1": message1})
    except IntegrityError:
        print("pass2")
        return render(
            request,
            "driver/signup.html",
        )
    print("pass3")
    return render(request, "driver/signup.html")
    # return render(request, "driver/signup.html")


class VerifyEmail(views.APIView):
    def get(self, request):
        token = request.GET.get("token")
        print("token=", token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print(payload)

            user = User.objects.get(id=payload["user_id"])
            print(user)
            if not user.is_active:
                user.is_active = True
                user.save()

            return render(request, "email_verify.html")
        except jwt.ExpiredSignatureError as identifier:
            return render(request, "email_verify.html")


def login(request):
    if request.method == "POST":
        phone = request.POST["phone"]
        password = request.POST["password"]
        incorrect_credentials = 0
        user_data = User.objects.filter(username=phone).first()
        driver_data = Driver.objects.filter(user_driver=user_data).first()

        if driver_data:
            user = authenticate(request, username=phone, password=password)
            print(user)
            if User.objects.filter(username=phone).exists():
                user_data = User.objects.filter(username=phone).first()
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
                        return redirect("driver_dashboard", pk=user.id)
                        # return render(
                        #     request,
                        #     "driver/user_profile.html",
                        #     {
                        #         "user": User.objects.filter(username=phone),
                        #         "dri": Driver.objects.filter(user_driver=user_data),
                        #     },
                        # )
                    else:
                        print("004")
                        print("NOT logged in after 004")
                        return render(
                            request,
                            "driver\login.html",
                        )
                else:
                    if user:
                        print("005")
                        print("not logged in after 004")
                        return render(
                            request,
                            "driver\login.html",
                        )
                    else:
                        print("006")
                        return render(
                            request,
                            "driver\login.html",
                        )
            else:
                # incorrect_credentials = 1
                return render(
                    request,
                    "driver\login.html",
                )
        else:
            print("passes else last")
            return render(
                request,
                "driver\login.html",
            )

    # cou = CourseData.objects.all().values()
    return render(request, "driver\login.html")


def dashboard(request, pk):
    return render(
        request,
        "driver/dashboard.html",
        {
            "user": User.objects.filter(id=pk),
            "dri": Driver.objects.filter(user_driver=pk),
        },
    )


def case(request, pk):
    return render(
        request,
        "driver/driver_case.html",
        {
            "user": User.objects.filter(id=pk),
            "dri": Driver.objects.filter(user_driver=pk),
            "care": Cc_person.objects.all(),
            "case": Case.objects.all(),
            "hos": Hospital.objects.all(),
            "amb": Driver.objects.all(),
        },
    )


def h_and_a(request, pk):
    driver = Driver.objects.filter(user_driver=pk).first()
    return render(
        request,
        "driver/driver_h_and_a.html",
        {
            "user": User.objects.filter(id=pk),
            "dri": Driver.objects.filter(user_driver=pk),
            "amb": Ambulance.objects.filter(driver_1=driver.id).first(),
            "hos": Hospital.objects.all(),
        },
    )


def profile(request, pk):
    return render(
        request,
        "driver/driver_profile.html",
        {
            "user": User.objects.filter(id=pk),
            "dri": Driver.objects.filter(user_driver=pk),
        },
    )


def edit_profile(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        user = User.objects.filter(id=user_id).first()
        pk = user_id
        driver = Driver.objects.filter(user_driver=user_id).first()
        if "dri_image" in request.FILES:
            driver.driver_photo = request.FILES.get("dri_image")

        if "firstName" in request.POST:
            user.first_name = request.POST["firstName"]
        if "lastName" in request.POST:
            user.last_name = request.POST["lastName"]
        if "phone" in request.POST:
            user.username = request.POST["phone"]

        # Save the updates
        user.save()
        driver.save()

        messages.success(request, "Profile updated successfully.")
        return redirect(
            "driver_profile", pk=pk
        )  # Redirect to the same page after update

    return redirect("driver_profile", pk=pk)


def remove_profile_image_driver(request):
    driver = Driver.objects.filter(user_driver=request.user.id).first()
    if driver and driver.driver_photo:
        driver.driver_photo.delete()  # Deletes the file
        driver.driver_photo = None
        driver.save()
        messages.success(request, "Profile image removed successfully.")
    else:
        messages.error(request, "No profile image to remove.")
    return redirect("driver_profile", pk=request.user.id)


def driver_change_pass(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        user = User.objects.filter(id=user_id).first()
        pk = user_id
        if "submit" in request.POST:
            password = request.POST["password"]
            check_current_password = check_password(password, user.password)
            if check_current_password:
                newpassword = request.POST["newpassword"]
                renewpassword = request.POST["renewpassword"]
                if newpassword == renewpassword:
                    user.set_password(newpassword)
                    user.save()
                    messages.success(request, "Password successfully changed")
                else:
                    messages.error(request, "New passwords don't match")
            else:
                messages.error(request, "Old password you entered is wrong")
        return redirect("driver_profile", pk=pk)
    else:
        return redirect("driver_profile", pk=pk)


def logout(request):
    print("logout1")
    auth_logout(request)
    print("logout2")
    return render(request, "driver\login.html")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
@ensure_csrf_cookie
@csrf_exempt
def toggle_tracking(request):
    if request.method == "POST":
        driver = Driver.objects.get(user_driver=request.user.id)
        is_tracking = request.POST.get("is_tracking") == "on"
        driver.is_tracking = is_tracking
        driver.case_status = request.POST["casestatus"]
        driver.save()
        return redirect("driver_case", pk=request.user.id)
    return JsonResponse({"status": "failed"})


import json


@csrf_exempt
def update_location(request):
    if request.method == "POST":
        driver = Driver.objects.get(user_driver=request.user.id)
        data = json.loads(request.body)
        driver.current_location = data.get("location")
        driver.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"})


def get_driver_location(request):
    case = Case.objects.filter(ambulance__id=pk).first()
    driver = Driver.objects.get(user_driver=request.user.id)
    return JsonResponse(
        {
            "latitude": driver.current_location.latitude,
            "longitude": driver.current_location.longitude,
        }
    )
