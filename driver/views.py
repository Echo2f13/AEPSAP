from datetime import datetime, timedelta, date
from django.db import IntegrityError
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import socket
from django.contrib.sites.shortcuts import get_current_site
from jwt.exceptions import InvalidTokenError
import json

import jwt
from rest_framework import views


from django.contrib import messages

from django.contrib.auth.hashers import make_password, check_password

from sas import settings
from case_details.models import Driver, Driver, Case, Cc_person, Hospital, Ambulance
from case_details.models import User
from django.core.mail import send_mail
from sas.settings import EMAIL_HOST_USER
from django.urls import reverse


from django.template import loader
from django.shortcuts import redirect, render

is_active_verify = False


from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta


def signup(request):
    try:
        if request.user.is_authenticated:
            return render(request, "driver/login.html")
        else:
            if request.method == "POST":
                first_name = request.POST["first_name"]
                last_name = request.POST["last_name"]
                email = request.POST["email"]
                phone = request.POST["phone"]
                license_number = request.POST["license_number"]
                password = request.POST["password"]
                message1 = 0
                message2 = 0

                exists = User.objects.filter(email=email)
                print("user data=", exists)
                if not exists:
                    user = User.objects.create_user(
                        username=phone,
                        email=email,
                        password=password,
                        is_active=False,  # account is inactive until verified
                        first_name=first_name,
                        last_name=last_name,
                    )
                    user.save()

                    driver_data = Driver.objects.create(
                        user_driver=user, license_number=license_number
                    )
                    driver_data.save()
                    print("data received")

                    user_email = User.objects.get(email=email)
                    print(user_email)

                    # Generate refresh token for the user
                    refresh = RefreshToken.for_user(user_email)
                    refresh.set_exp(lifetime=timedelta(days=36500))

                    current_site = get_current_site(request).domain
                    relativeLink = reverse("email_verify")
                    print(relativeLink)

                    absUrl = (
                        "http://"
                        + current_site
                        + relativeLink
                        + "?token="
                        + str(refresh.access_token)  # Make sure to use access token
                    )
                    Subject = "Hello " + "Verification pending"
                    Message = "Click the link to activate your account: \n" + absUrl
                    send_mail(Subject, Message, EMAIL_HOST_USER, [email])

                    print("pass1")
                    print(absUrl)
                    message2 = 1
                    return render(request, "driver/login.html", {"message2": message2})
                else:
                    message1 = 1
                    return render(request, "driver/signup.html", {"message1": message1})
    except IntegrityError:
        print("pass2")
        return render(request, "driver/signup.html")

    print("pass3")
    return render(request, "driver/signup.html")


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
    try:
        # Get the driver associated with the user
        driver = Driver.objects.get(user_driver=pk)

        # Find the first case where the driver is the primary driver
        case_data = Case.objects.filter(ambulance__driver_1=driver).first()

        if case_data:
            # Extract the location and ambulance's current location
            location = case_data.location
            amb_location = case_data.ambulance.driver_1.current_location
            
            # Handle the splitting of the location if it exists
            if location:
                location_lat, location_lng = map(str.strip, location.split(","))
            else:
                location_lat = location_lng = None

            if amb_location:
                amb_location_lat, amb_location_lng = map(str.strip, amb_location.split(","))
            else:
                amb_location_lat = amb_location_lng = None
        else:
            location_lat = location_lng = amb_location_lat = amb_location_lng = None

        # Prepare context for the template
        context = {
            "user": User.objects.filter(id=pk),
            "dri": Driver.objects.filter(user_driver=pk),
            "care": Cc_person.objects.all(),
            "case": Case.objects.all(),
            "hos": Hospital.objects.all(),
            "case_in": case_data,
            "google_maps_api_key": "AIzaSyCfs2EPBwjylYC_6twmdwnIFXUlc5LkaH0",
            "location_lat": location_lat,
            "location_lng": location_lng,
            "amb_location_lat": amb_location_lat,
            "amb_location_lng": amb_location_lng,
        }
    except Driver.DoesNotExist:
        # Handle the case where the driver is not found
        context = {
            "error": "Driver not found",
        }

    return render(request, "driver/driver_case.html", context)

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


# @login_required
# @ensure_csrf_cookie
# @csrf_exempt
# def toggle_tracking(request):
#     if request.method == "POST":
#         driver = Driver.objects.get(user_driver=request.user.id)
#         is_tracking = request.POST.get("is_tracking") == "on"
#         driver.is_tracking = is_tracking
#         driver.case_status = request.POST["case_status"]
#         driver.save()
#         return redirect("driver_case", pk=request.user.id)
#     return JsonResponse({"status": "failed"})
from django.shortcuts import render, redirect, get_object_or_404

@login_required
@ensure_csrf_cookie
@csrf_exempt
def toggle_tracking(request):
    if request.method == "POST":
        try:
            driver = get_object_or_404(Driver, user_driver=request.user.id)
            ambulance = Ambulance.objects.filter(driver_1 = driver).first()
            case_id = Case.objects.filter(ambulance_id = ambulance.ambulance_id).first()
            
            is_tracking = request.POST.get("is_tracking") == "on"
            driver.is_tracking = is_tracking
            
            case_status = request.POST.get("case_status", None)
            if case_status is not None:
                driver.case_status = int(case_status)
                case_id.status = int(case_status)
            else:
                return JsonResponse({"status": "failed", "error": "Invalid case status"})

            driver.save()
            case_id.save()

            return redirect("driver_case", pk=request.user.id)

        except Driver.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "Driver not found"}, status=404)
        except ValueError:
            return JsonResponse({"status": "failed", "error": "Invalid data"}, status=400)
    
    return JsonResponse({"status": "failed", "error": "Invalid request method"}, status=405)



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
