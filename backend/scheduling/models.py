from django.db import models

from accounts.models import DoctorProfile


# Create your models here.
class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    day_of_week = models.CharField(choices=[('monday', 'Monday'),
                                            ('tuesday', 'Tuesday'),
                                            ('wednesday', 'Wednesday'),
                                            ('thursday', 'Thursday'),
                                            ('friday', 'Friday'),
                                            ('saturday', 'Saturday'),
                                            ('sunday', 'Sunday'),
                                            ], max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
