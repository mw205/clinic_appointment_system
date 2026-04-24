from datetime import date

from rest_framework import serializers
from django.contrib.auth import authenticate

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



class UserSummarySerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "primary_role",
            "groups"
        ]

    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))
    
    def get_primary_role(self, obj):
        groups = list(obj.groups.values_list('name', flat=True))
        return groups[0] if groups else None
        

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        request = self.context.get('request')
        user = authenticate(request=request, username=username, password=password)

        if not user:
            raise serializers.ValidationError(
                'Invalid username or password.')
        
        if not user.is_active:
            raise serializers.ValidationError(
                'User account is inactive.')
        
        attrs['user'] = user
        return attrs