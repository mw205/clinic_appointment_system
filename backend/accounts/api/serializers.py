from datetime import date

from rest_framework import serializers

from accounts.models import DoctorProfile, PatientProfile, User


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone_number",
        ]


class PatientProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "user",
            "date_of_birth",
            "blood_type",
            "gender",
        ]

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future.")
        return value

    def validate_blood_type(self, value):
        if value not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            raise serializers.ValidationError(
                "Invalid blood type.")
        return value


class DoctorProfileModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "user",
            "specialization",
        ]

    def validate_specialization(self, value):
        if value.strip() == "":
            raise serializers.ValidationError(
                "Specialization cannot be empty.")
        return value
