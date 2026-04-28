from django.contrib import admin
from .models import ConsultationRecord, PrescriptionItem, RequestedTest
admin.site.register([ConsultationRecord, PrescriptionItem, RequestedTest])
