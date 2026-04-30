from datetime import date
import re

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.models import Group
from django.db import transaction


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
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_blood_type(self, value):
        if value not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            raise serializers.ValidationError("Invalid blood type.")
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
            raise serializers.ValidationError("Specialization cannot be empty.")
        return value


class UserSummarySerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "primary_role",
            "groups",
            "profile_id",
        ]

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_primary_role(self, obj):
        groups = list(obj.groups.values_list("name", flat=True))
        return groups[0] if groups else None

    def get_profile_id(self, obj):
        patient_profile = getattr(obj, "patientprofile", None)
        if patient_profile is not None:
            return patient_profile.id

        doctor_profile = getattr(obj, "doctorprofile", None)
        if doctor_profile is not None:
            return doctor_profile.id

        return None


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        request = self.context.get("request")
        user = authenticate(request=request, username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive.")

        attrs["user"] = user
        return attrs


class CurrentUserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "primary_role",
            "groups",
            "profile_id",
        ]

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_primary_role(self, obj):
        groups = list(obj.groups.values_list("name", flat=True))
        return groups[0] if groups else None

    def get_profile_id(self, obj):
        patient_profile = getattr(obj, "patientprofile", None)
        if patient_profile is not None:
            return patient_profile.id

        doctor_profile = getattr(obj, "doctorprofile", None)
        if doctor_profile is not None:
            return doctor_profile.id

        return None


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.refresh_token).blacklist()

        except TokenError:
            raise serializers.ValidationError("Invalid or expired token.")


class PatientRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()

    # PatientProfile fields
    date_of_birth = serializers.DateField()
    blood_type = serializers.ChoiceField(
        choices=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    )
    gender = serializers.ChoiceField(
        choices=[
            ("male", "Male"),
            ("female", "Female"),
        ]
    )

    # Field-level validation
    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("This field cannot be empty.")
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("This field cannot be empty.")
        return value.strip()

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_phone_number(self, value):
        value = value.strip()

        # check format
        if not re.fullmatch(r"^\+?\d+$", value):
            raise serializers.ValidationError(
                "Phone number must contain only digits and optional leading '+'."
            )

        digits_only = value.lstrip("+")

        # validate digit length only
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise serializers.ValidationError(
                "Phone number must be between 10 and 15 digits."
            )

        return value

    # Object-level validation
    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Password confirmation does not match password."}
            )

        user = User(
            username=attrs.get("username"),
            email=attrs.get("email"),
            first_name=attrs.get("first_name"),
            last_name=attrs.get("last_name"),
        )

        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user_data = {
            "username": validated_data.pop("username"),
            "email": validated_data.pop("email"),
            "password": validated_data.pop("password"),
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "phone_number": validated_data.pop("phone_number"),
        }

        profile_data = validated_data

        with transaction.atomic():
            user = User.objects.create_user(**user_data)

            try:
                patient_group = Group.objects.get(name="Patient")
            except Group.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "detail": "Patient group does not exist. Please contact administrator."
                    }
                )

            user.groups.add(patient_group)

            PatientProfile.objects.create(user=user, **profile_data)

        return user


class CurrentUserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("This field cannot be empty.")
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("This field cannot be empty.")
        return value.strip()

    def validate_email(self, value):
        value = value.strip().lower()

        request = self.context.get("request")
        user = request.user if request else None

        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_phone_number(self, value):
        value = value.strip()

        request = self.context.get("request")
        user = request.user if request else None

        # check format
        if not re.fullmatch(r"^\+?\d+$", value):
            raise serializers.ValidationError(
                "Phone number must contain only digits and optional leading '+'."
            )

        digits_only = value.lstrip("+")

        # validate digit length only
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise serializers.ValidationError(
                "Phone number must be between 10 and 15 digits."
            )

        normalized_phone = "+" + digits_only if value.startswith("+") else digits_only

        if (
            User.objects.filter(phone_number=normalized_phone)
            .exclude(id=user.id)
            .exists()
        ):
            raise serializers.ValidationError("Phone number is already registered.")

        return normalized_phone

    def update(self, instance, validated_data):

        if not validated_data:
            raise serializers.ValidationError("No data provided for update.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save(update_fields=list(validated_data.keys()))
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.instance
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if not user.check_password(current_password):
            raise serializers.ValidationError(
                {"current_password": "Current password is incorrect."}
            )

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {
                    "new_password_confirm": "Password confirmation does not match password."
                }
            )

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs

    def save(self, **kwargs):
        user = self.instance
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class CurrentPatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "date_of_birth",
            "blood_type",
            "gender",
        ]


class CurrentPatientProfileUpdateSerializer(serializers.Serializer):
    date_of_birth = serializers.DateField(required=False)
    blood_type = serializers.ChoiceField(
        choices=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], required=False
    )
    gender = serializers.ChoiceField(
        choices=[
            ("male", "Male"),
            ("female", "Female"),
        ],
        required=False,
    )

    def validate_date_of_birth(self, value):

        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")

        return value

    def update(self, instance, validated_data):

        if not validated_data:
            raise serializers.ValidationError("No data provided for update.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save(update_fields=list(validated_data.keys()))
        return instance


class CurrentDoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "specialization",
        ]


class CurrentDoctorProfileUpdateSerializer(serializers.Serializer):
    specialization = serializers.CharField(required=False)

    def validate_specialization(self, value):
        if value.strip() == "":
            raise serializers.ValidationError("Specialization cannot be empty.")
        return value.strip()

    def update(self, instance, validated_data):

        if not validated_data:
            raise serializers.ValidationError("No data provided for update.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save(update_fields=list(validated_data.keys()))
        return instance


class StaffUserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "primary_role",
            "groups",
            "profile_id",
        ]

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_primary_role(self, obj):
        groups = list(obj.groups.values_list("name", flat=True))

        role_priority = ["Admin", "Receptionist", "Doctor", "Patient"]

        for role in role_priority:
            if role in groups:
                return role

        return None

    def get_profile_id(self, obj):
        patient_profile = getattr(obj, "patientprofile", None)
        if patient_profile is not None:
            return patient_profile.id

        doctor_profile = getattr(obj, "doctorprofile", None)
        if doctor_profile is not None:
            return doctor_profile.id

        return None


class StaffUserUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    groups = serializers.ListField(child=serializers.CharField(), required=False)

    def validate_groups(self, value):

        if value == []:
            raise serializers.ValidationError(
                "User must have at least one assigned group."
            )

        unique_names = list(set(value))
        groups = list(Group.objects.filter(name__in=unique_names))

        if len(groups) != len(unique_names):
            existing_names = {g.name for g in groups}
            invalid = set(unique_names) - existing_names
            raise serializers.ValidationError(f"Invalid groups: {', '.join(invalid)}")

        return groups

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("No data provided for update.")
        return attrs

    def update(self, instance, validated_data):
        update_fields = []

        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]
            update_fields.append("is_active")

        if "groups" in validated_data:
            instance.groups.set(validated_data["groups"])

        if update_fields:
            instance.save(update_fields=update_fields)

        return instance
