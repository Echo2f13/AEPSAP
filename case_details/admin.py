from django.contrib import admin
from .models import Driver, Case, Cc_person, Ambulance, Hospital
from import_export.admin import ImportExportModelAdmin

admin.site.register(Cc_person)
admin.site.register(Driver)
admin.site.register(Case)
admin.site.register(Ambulance)
admin.site.register(Hospital)
