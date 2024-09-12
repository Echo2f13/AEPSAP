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
from case_details.models import Cc_person, Hospital, Driver, Driver, Case, Ambulance
from django.urls import reverse
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
                        request, "customer_care\signup.html", {"message1": message1}
                    )
    except IntegrityError:
        print("pass2")
        return render(
            request,
            "customer_care\signup.html",
        )
    print("pass3")
    return render(request, "customer_care\signup.html")
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
                        return redirect("care_dashboard", pk=c_id_data.user_cc_id)
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
            "care": Cc_person.objects.filter(user_cc=pk),
        },
    )


def dashboard(request, pk):
    return render(
        request,
        "customer_care/dashboard.html",
        {
            "user": User.objects.filter(id=pk),
            "care": Cc_person.objects.filter(user_cc=pk),
        },
    )


def care_case(request, pk):
    return render(
        request,
        "customer_care/care_case.html",
        {
            "user": User.objects.filter(id=request.user.id),
            "care": Cc_person.objects.filter(user_cc=request.user.id),
            "amb": Ambulance.objects.all(),
            "hos": Hospital.objects.all(),
            "dri": Driver.objects.all(),
            "accident_types": Case.ACCIDENT_TYPES,
            "severity_levels": Case.SEVERITY_LEVELS,
            "case": Case.objects.all(),
        },
    )


def add_case(request):
    if request.method == "POST":
        patient_name = request.POST["patient_name"]
        poc = request.POST["poc"]
        accident_type = request.POST["accident_type"]
        patient_severity = request.POST["patient_severity"]
        location = request.POST["location"]
        status = request.POST["status"]
        ambulance_id = request.POST["ambulance"]
        assigned_cc_person_id = request.POST["assigned_cc_person"]
        description = request.POST.get("description", "")
        first_responder_notes = request.POST.get("first_responder_notes", "")

        ambulance = (
            Ambulance.objects.filter(ambulance_id=ambulance_id).first() if ambulance_id else None
        )
        assigned_cc_person = (
            Cc_person.objects.get(cc_id=assigned_cc_person_id)
            if assigned_cc_person_id
            else None
        )
        current_time_date = datetime.now()
        new_case = Case(
            Patient_name=patient_name,
            poc=poc,
            accident_type=accident_type,
            patient_severity=patient_severity,
            location=location,
            time_date=current_time_date,
            status=status,
            ambulance_id=ambulance.ambulance_id,
            assigned_cc_person=assigned_cc_person,
            description=description,
            first_responder_notes=first_responder_notes,
        )
        print(ambulance)
        # ambulance_catch = Ambulance.objects.filter(ambulance_id=ambulance_id)

        driver = Driver.objects.filter(id=ambulance.driver_1.id).first()
        driver.case_status = 0
        driver.save()
        new_case.save()

        return redirect(
            "care_case",
            pk=request.user.id,
        )  # Redirect to a success page or the list of cases
    else:
        return render(
            request,
            "customer_care/care_case.html",
            {
                "user": User.objects.filter(id=request.user.id),
                "care": Cc_person.objects.filter(user_cc=request.user.id),
                "amb": Ambulance.objects.all(),
                "hos": Hospital.objects.all(),
                "dri": Driver.objects.all(),
                "accident_types": Case.ACCIDENT_TYPES,
                "severity_levels": Case.SEVERITY_LEVELS,
                "case": Case.objects.all(),
            },
        )


def care_ambulance(request, pk):
    return render(
        request,
        "customer_care/care_ambulance.html",
        {
            "user": User.objects.filter(id=pk),
            "care": Cc_person.objects.filter(user_cc=pk),
            "amb": Ambulance.objects.all(),
            "hos": Hospital.objects.all(),
            "dri": Driver.objects.all(),
        },
    )


def add_ambulance(request):
    if request.method == "POST":
        ambulance_number = request.POST["ambulance_number"]
        ambulance_size = request.POST["ambulance_size"]
        ambulance_model = request.POST["ambulance_model"]
        hospital = request.POST["hospital"]
        driver_1 = request.POST["driver_1"]
        driver_2 = request.POST["driver_2"]
        bystander_1 = request.POST["bystander_1"]
        bystander_2 = request.POST["bystander_2"]
        bystander_3 = request.POST["bystander_3"]
        bystander_4 = request.POST["bystander_4"]
        ambulance_photo = request.FILES.get("ambulance_photo")

        # Create and save a new ambulance instance
        user_1_id = User.objects.filter(username=driver_1).first()
        user_2_id = User.objects.filter(username=driver_2).first()
        hospital_id = Hospital.objects.filter(name=hospital).first()
        driver_1_id = Driver.objects.filter(user_driver=user_1_id).first()
        driver_2_id = Driver.objects.filter(user_driver=user_2_id).first()
        new_ambulance = Ambulance(
            ambulance_number=ambulance_number,
            ambulance_size=ambulance_size,
            ambulance_model=ambulance_model,
            hospital_id=hospital_id.hospital_id,
            driver_1_id=driver_1_id.id,
            driver_2_id=driver_2_id.id,
            bystander_1=bystander_1,
            bystander_2=bystander_2,
            bystander_3=bystander_3,
            bystander_4=bystander_4,
            ambulance_photo=ambulance_photo,
        )
        new_ambulance.save()

        messages.success(request, "Ambulance added successfully.")
        return redirect(
            "care_ambulance",
            pk=request.user.id,
        )  # Redirect to the list of ambulances or another appropriate page

    return render(
        request,
        "ambulance/add_ambulance.html",  # Path to your HTML template
        {
            "user": User.objects.filter(id=request.user.id).first(),
            "care": Cc_person.objects.filter(user_cc=request.user.id).first(),
            "amb": Ambulance.objects.all(),
            "hos": Hospital.objects.all(),
            "dri": Driver.objects.all(),
        },
    )


def care_hospital(request, pk):
    hospital = Hospital.objects.all()
    return render(
        request,
        "customer_care/care_hospital.html",
        {
            "user": User.objects.filter(id=pk),
            "care": Cc_person.objects.filter(user_cc=pk),
            "hos": hospital,
        },
    )


def add_hospital(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")

        if name and address:
            # Create and save a new hospital instance
            new_hospital = Hospital(name=name, address=address)
            new_hospital.save()

            messages.success(request, "Hospital added successfully.")
            return redirect(
                "care_hospital", pk=request.user.id
            )  # Redirect to a page showing the list of hospitals or other appropriate page
        else:
            messages.error(request, "Please fill in all fields.")

    return render(
        request,
        "customer_care/add_hospital.html",  # Use your template for adding a hospital
        {
            "user": User.objects.filter(id=request.user.id).first(),
            "care": Cc_person.objects.filter(user_cc=request.user.id).first(),
        },
    )


def edit_profile(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        user = User.objects.filter(id=user_id).first()
        pk = user_id
        cc_person = Cc_person.objects.filter(user_cc=user_id).first()
        if "cc_image" in request.FILES:
            cc_person.photo = request.FILES.get("cc_image")

        if "firstName" in request.POST:
            user.first_name = request.POST["firstName"]
        if "lastName" in request.POST:
            user.last_name = request.POST["lastName"]
        if "phone" in request.POST:
            cc_person.phone_number = request.POST["phone"]

        # Save the updates
        user.save()
        cc_person.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("care_profile", pk=pk)  # Redirect to the same page after update

    return redirect("care_profile", pk=pk)


def remove_profile_image(request):
    cc_person = Cc_person.objects.filter(user_cc=request.user).first()
    if cc_person and cc_person.photo:
        cc_person.photo.delete()  # Deletes the file
        cc_person.photo = None
        cc_person.save()
        messages.success(request, "Profile image removed successfully.")
    else:
        messages.error(request, "No profile image to remove.")
    return redirect("care_profile", pk=cc_person.user_cc.id)


def care_change_pass(request):
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
        return redirect("care_profile", pk=pk)
    else:
        return redirect("care_profile", pk=pk)


def logout(request):
    print("logout1")
    auth_logout(request)
    print("logout2")
    return render(request, "customer_care\login.html")
