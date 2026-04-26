from django.contrib import admin

from .models import DoctorSchedule, ScheduleException

# Register your models here.
admin.site.register([DoctorSchedule, ScheduleException])
