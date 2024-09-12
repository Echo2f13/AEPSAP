from django.db import models
from django.contrib.auth.models import User

STATUSES = [
    (0, "Open"),
    (1, "Closed"),
]


# cc = customer care
class Cc_person(models.Model):
    cc_id = models.BigAutoField(primary_key="True", auto_created="True")
    cc_gov_id = models.CharField(max_length=50, unique=True, null=False)
    phone_number = models.CharField(max_length=15, unique=True, null=False)
    photo = models.ImageField(null=True, upload_to="cc_photos/")

    user_cc = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_cc")

    class Meta:
        db_table = "Customer Care Person"

    def _str_(self):
        return self.user.username


class Driver(models.Model):
    license_number = models.CharField(max_length=50, unique=True, null=False)
    # phone_number = models.CharField(max_length=15, unique=True, null=False)
    driver_photo = models.ImageField(null=True, upload_to="driver_photos/")
    user_driver = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_driver"
    )
    case_status = models.IntegerField(choices=STATUSES, default=0)
    current_location = models.CharField(max_length=255, null=True, blank=True)
    is_tracking = models.BooleanField(default=False)
    amb_con = models.BooleanField(default=0);

    class Meta:
        db_table = "Driver"

    def __str__(self):
        return self.user_driver.username


class Ambulance(models.Model):
    AMBULANCE_SIZES = [
        ("B", "Big"),
        ("M", "Medium"),
    ]

    ambulance_id = models.BigAutoField(primary_key=True, auto_created=True)
    ambulance_number = models.CharField(max_length=20, unique=True, null=False)
    ambulance_size = models.CharField(max_length=1, choices=AMBULANCE_SIZES, null=False)
    ambulance_model = models.CharField(max_length=50, null=False)
    ambulance_photo = models.ImageField(null=True, upload_to="ambulance_photos/")
    hospital = models.ForeignKey("Hospital", on_delete=models.CASCADE)
    driver_1 = models.ForeignKey(
        "Driver", related_name="primary_driver", on_delete=models.CASCADE
    )
    driver_1_con = models.BooleanField(default=1);
    driver_2 = models.ForeignKey(
        "Driver", related_name="secondary_driver", on_delete=models.SET_NULL, null=True
    )
    bystander_1 = models.CharField(max_length=50, null="False")
    bystander_2 = models.CharField(max_length=50, null="False")
    bystander_3 = models.CharField(max_length=50, null="True")
    bystander_4 = models.CharField(max_length=50, null="True")

    class Meta:
        db_table = "Ambulance"

    def __str__(self):
        return self.ambulance_number


class Hospital(models.Model):
    hospital_id = models.BigAutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=200, unique=True, null=False)
    address = models.CharField(max_length=1500, null=True)

    class Meta:
        db_table = "Hospital"

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth.models import User
import datetime


class Case(models.Model):
    ACCIDENT_TYPES = [
        ("VEH", "Vehicle Collision"),
        ("FAL", "Fall"),
        ("BUR", "Burn"),
        ("CUT", "Laceration"),
        ("OTH", "Other"),
    ]

    SEVERITY_LEVELS = [
        ("CRT", "Critical"),
        ("SR", "Serious"),
        ("MD", "Mild"),
        ("MIN", "Minor"),
    ]

    case_id = models.BigAutoField(primary_key=True, auto_created=True)
    Patient_name = models.CharField(max_length=35)
    # poc = point of contact
    poc = models.CharField(max_length=35)
    accident_type = models.CharField(
        max_length=3, choices=ACCIDENT_TYPES, default="OTH"
    )
    patient_severity = models.CharField(
        max_length=3, choices=SEVERITY_LEVELS, default="MIN"
    )
    location = models.CharField(max_length=255)
    time_date = models.DateTimeField(default=datetime.datetime.now)
    status = models.IntegerField(choices=STATUSES, default=0)

    ambulance = models.ForeignKey("Ambulance", on_delete=models.SET_NULL, null=True)
    assigned_cc_person = models.ForeignKey(
        "cc_person", on_delete=models.SET_NULL, null=True
    )

    # Additional details
    description = models.TextField(null=True, blank=True)
    first_responder_notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "Case"

    def __str__(self):
        return f"Case {self.case_id}"
