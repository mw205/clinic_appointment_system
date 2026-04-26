from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    role_choices = [
        ("patient", "Patient"),
        ("doctor", "Doctor"),
        ("receptionist", "Receptionist"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=role_choices, default="patient")
    phone_number = models.CharField(max_length=15)


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=3)
    gender = models.CharField(
        max_length=10,
        choices=(
            ("male", "Male"),
            ("female", "Female"),
        ),
        default="male",
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.id})"


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.id})"
