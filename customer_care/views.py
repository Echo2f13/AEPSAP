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

from django.template import loader
from django.shortcuts import redirect, render


is_active_verify = False


def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        gov_id = request.POST.get("cc_gov_id")

        try:
            # Check if user with email already exists
            if not User.objects.filter(email=email).exists():
                # Create inactive user account
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=True,  # Account inactive until verified
                    first_name=first_name,
                    last_name=last_name,
                )
                user.save()

                # Save additional Customer Care data
                care_data = Cc_person.objects.create(
                    cc_gov_id=gov_id,
                    phone_number=phone,
                    user_cc=user,
                )
                care_data.save()
                # Redirect to login page with success message
                return redirect('care_login')
            else:
                # If email exists, return error message
                message1 = "A user with this email already exists."
                return render(request, "customer_care/signup.html", {"message1": message1})

        except IntegrityError:
            # Handle database-related errors
            message1 = "There was an error processing your request. Please try again."
            return render(request, "customer_care/signup.html", {"message1": message1})

    # Render the signup form if not a POST request
    return render(request, "customer_care/signup.html")

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

# URL for the API
API_URL = "http://192.168.143.39:3000/emergencyProtocol"

def care_case(request, pk):
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json() 
        print("successfully displayed the data") # JSON data from the response
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        data = []  
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
            'emg_data': data,
        },
    )


def decline_api_emg(request, id):
    print("id :", id)
    api_url = f"{API_URL}/{id}"
    print("api url is:",api_url)

    try:
        response = requests.delete(api_url)
        if response.status_code == 200:
            messages.success(request, "Case declined successfully.")
        else:
            messages.error(request, "Failed to decline the case.")
    
    except requests.RequestException as e:
        messages.error(request, f"Error: {e}")

    return redirect(
            "care_case",
            pk=request.user.id,
        )  


def accept_api_emg(request, id):
    person_id = int(id)  
    full_api_url = f"{API_URL}/{id}"  
    try:
        response = requests.get(full_api_url)
        response.raise_for_status()  
        emg_data = response.json()   
        print("Fetched emergency data:", emg_data)
        messages.info(request, f"Fetched data for ID: {id}")
        
        request.session['emg_data'] = emg_data

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error fetching data: {str(e)}")
        return redirect(
                "care_case",
                pk=request.user.id,
            )  
    return redirect(
            "care_case",
            pk=request.user.id,
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
        )  
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

        user_1_id = User.objects.filter(username=driver_1).first()
        user_2_id = User.objects.filter(username=driver_2).first()
        hospital_id = Hospital.objects.filter(name=hospital).first()
        driver_1_id = Driver.objects.filter(user_driver=user_1_id).first()
        driver_2_id = Driver.objects.filter(user_driver=user_2_id).first()
        # con = 1;
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
            # driver_1_con = True;
        )
        new_ambulance.save()
        # driver_1_id_con = Driver(amb_con = 1)
        # driver_1_id_con.save() 

        messages.success(request, "Ambulance added successfully.")
        return redirect(
            "care_ambulance",
            pk=request.user.id,
        )  

    return render(
        request,
        "ambulance/add_ambulance.html",  
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


import requests
from django.shortcuts import render

