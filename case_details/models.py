from django.db import models
from django.contrib.auth.models import User


# cc = customer care
class cc_person(models.Model):
    cc_id = models.BigAutoField(primary_key="True", auto_created="True")
    cc_gov_id = models.CharField(max_length=50, unique="True", null="True")
    cc_image = models.ImageField(null="True", upload_to="")
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
    hospital_related_to = models.ForeignKey(
        "Hospital", on_delete=models.CASCADE, null=True
    )
    user_driver = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_driver"
    )

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

    STATUSES = [
        (0, "Open"),
        (1, "Closed"),
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

    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True)
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


# class TeacherData(models.Model):
#     teacher_id = models.BigAutoField(primary_key="True", auto_created="True")
#     tea_reg_id = models.CharField(max_length=50, unique="True", null="True")
#     teacher_image = models.ImageField(null="True", upload_to="")

#     # rating by students to teachers
#     tea_stars = models.FloatField(default=0)
#     tea_stars_voted = models.FloatField(default=0)
#     tea_people_voted = models.IntegerField(default=0)

#     user_teacher = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="user_teacher"
#     )

#     class Meta:
#         db_table = "Teacher"

#     def _str_(self):
#         return self.user_teacher.username


# class CourseData(models.Model):
#     course_id = models.BigAutoField(primary_key="True")
#     course_name = models.CharField(max_length=16, unique="True", null="True")
#     course_image = models.ImageField(null="True", upload_to="")
#     short_description = models.CharField(max_length=200, null="True")
#     description = models.CharField(max_length=5000)

#     # pre-required
#     pre_required = models.CharField(max_length=16, null="True")

#     # Course Agenda
#     agenda_title = models.CharField(max_length=30, null="True")
#     agenda = models.CharField(max_length=3000, null="True")

#     # course pricing
#     price = models.FloatField(default=0)

#     # rating by students
#     stars = models.FloatField(default=0)
#     stars_voted = models.FloatField(default=0)
#     people_voted = models.IntegerField(default=0)

#     class Meta:
#         db_table = "Courses"


# class BatchData(models.Model):
#     batch_id = models.BigAutoField(primary_key="True", auto_created="True")
#     start_date = models.DateField(null="True", blank="True")

#     class Meta:
#         db_table = "Batches"


# class TeacherBatchLinkDate(models.Model):
#     teacher_batch_link_id = models.BigAutoField(primary_key="True", auto_created="True")

#     batch_id = models.ForeignKey(BatchData, null="False", on_delete=models.CASCADE)
#     course_id = models.ForeignKey(CourseData, null="False", on_delete=models.CASCADE)
#     teacher_reg_id = models.ForeignKey(
#         TeacherData, null="True", on_delete=models.CASCADE
#     )
#     no_of_students = models.IntegerField(default=0)

#     applicable = models.BooleanField(default="True")

#     # rating stuff
#     tea_cou_batch_stars = models.FloatField(default=0)
#     tea_cou_batch_stars_voted = models.FloatField(default=0)
#     tea_cou_batch_people_voted = models.IntegerField(default=0)
#     tea_cou_batch_review_text = models.CharField(max_length=2000, null="True")

#     class Meta:
#         db_table = "Teacher-Batch-Link"


# # class RegisteredData(models.Model):
# #     registered_id = models.BigAutoField(
# #         primary_key='True', auto_created='True')
# #     registered_already = models.BooleanField(default=False)

# #     student_id = models.ForeignKey(
# #         StudentData, null='True', on_delete=models.CASCADE)
# #     specified_batch_id = models.ForeignKey(
# #         TeacherBatchLinkDate, null='True', on_delete=models.CASCADE)

# #     # these fields are just for verification
# #     course_id = models.ForeignKey(
# #         CourseData, null='False', on_delete=models.CASCADE)
# #     teacher_id = models.ForeignKey(
# #         TeacherData, null='True', on_delete=models.CASCADE)

# #     # registration approval
# #     # 0 pending,1 Approved, -1 rejected
# #     course_status = models.IntegerField(default=0)
# #     date_apply = models.DateTimeField(null='True', blank='True')
# #     date_acknowledged = models.DateTimeField(null='True', blank='True')

# #     # rating by the student
# #     rating = models.FloatField(default=0)
# #     review_text = models.CharField(max_length=2000, null='True')
# #     rating_given = models.BooleanField(default=0)

# #     # on completion
# #     completed = models.BooleanField(default='False')

# #     # payed
# #     payed = models.BooleanField(default='False')

# #     # pre required course completed
# #     pre_required_completed = models.BooleanField(default='True')

# #     class Meta:
# #         db_table = 'Registered'
