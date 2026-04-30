from django.contrib.auth.models import AnonymousUser, Group
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import PatientProfile, User
from accounts.rbac import (
    ADMIN,
    DOCTOR,
    PATIENT,
    RECEPTIONIST,
    is_admin,
    is_doctor,
    is_patient,
    is_receptionist,
    user_has_any_group,
    user_has_group,
)


class RBACHelpersTests(TestCase):
    def setUp(self):
        self.patient_group, _ = Group.objects.get_or_create(name=PATIENT)
        self.doctor_group, _ = Group.objects.get_or_create(name=DOCTOR)
        self.receptionist_group, _ = Group.objects.get_or_create(name=RECEPTIONIST)
        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN)
        self.user = User.objects.create_user(
            username="patient_user",
            password="StrongPass123!",
            email="patient@example.com",
            phone_number="+201234567890",
        )
        self.user.groups.add(self.patient_group)

    def test_user_has_group_returns_true_for_matching_group(self):
        self.assertTrue(user_has_group(self.user, PATIENT))

    def test_user_has_any_group_returns_true_for_any_match(self):
        self.assertTrue(user_has_any_group(self.user, [DOCTOR, PATIENT]))

    def test_role_helpers_reflect_group_membership(self):
        self.assertTrue(is_patient(self.user))
        self.assertFalse(is_doctor(self.user))
        self.assertFalse(is_receptionist(self.user))
        self.assertFalse(is_admin(self.user))

    def test_anonymous_user_has_no_groups(self):
        anonymous = AnonymousUser()
        self.assertFalse(user_has_group(anonymous, PATIENT))
        self.assertFalse(user_has_any_group(anonymous, [PATIENT, DOCTOR]))


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.patient_group, _ = Group.objects.get_or_create(name=PATIENT)
        self.doctor_group, _ = Group.objects.get_or_create(name=DOCTOR)
        self.receptionist_group, _ = Group.objects.get_or_create(name=RECEPTIONIST)
        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN)
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.me_url = reverse("current-user")
        self.change_password_url = reverse("change-password")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("logout")

    def create_patient_user(self, username="existing_patient", email="existing@example.com"):
        user = User.objects.create_user(
            username=username,
            password="StrongPass123!",
            email=email,
            first_name="Existing",
            last_name="Patient",
            phone_number="+201234567891",
        )
        user.groups.add(self.patient_group)
        PatientProfile.objects.create(
            user=user,
            date_of_birth="1995-01-01",
            blood_type="A+",
            gender="male",
        )
        return user

    def test_register_creates_patient_profile_assigns_group_and_returns_tokens(self):
        payload = {
            "username": "new_patient",
            "email": "new_patient@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "New",
            "last_name": "Patient",
            "phone_number": "+201234567892",
            "date_of_birth": "1998-05-10",
            "blood_type": "O+",
            "gender": "female",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertEqual(response.data["user"]["primary_role"], PATIENT)
        self.assertIn(settings.AUTH_REFRESH_COOKIE_NAME, response.cookies)
        created_user = User.objects.get(username="new_patient")
        self.assertTrue(created_user.groups.filter(name=PATIENT).exists())
        self.assertTrue(PatientProfile.objects.filter(user=created_user).exists())

    def test_register_rejects_duplicate_email(self):
        self.create_patient_user(email="duplicate@example.com")
        payload = {
            "username": "another_patient",
            "email": "duplicate@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "first_name": "Another",
            "last_name": "Patient",
            "phone_number": "+201234567893",
            "date_of_birth": "1999-02-02",
            "blood_type": "B+",
            "gender": "male",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["details"])

    def test_login_returns_tokens_and_group_based_user_summary(self):
        self.create_patient_user(username="login_patient", email="login@example.com")
        payload = {
            "username": "login_patient",
            "password": "StrongPass123!",
        }

        response = self.client.post(self.login_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertEqual(response.data["user"]["primary_role"], PATIENT)
        self.assertEqual(response.data["user"]["groups"], [PATIENT])
        self.assertIn(settings.AUTH_REFRESH_COOKIE_NAME, response.cookies)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user_details(self):
        user = self.create_patient_user(username="me_patient", email="me@example.com")
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["phone_number"], user.phone_number)
        self.assertEqual(response.data["primary_role"], PATIENT)
        self.assertEqual(response.data["groups"], [PATIENT])

    def test_refresh_returns_new_access_token(self):
        user = self.create_patient_user(username="refresh_patient", email="refresh@example.com")
        refresh = RefreshToken.for_user(user)
        self.client.cookies[settings.AUTH_REFRESH_COOKIE_NAME] = str(refresh)

        response = self.client.post(
            self.refresh_url,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_logout_blacklists_refresh_token(self):
        user = self.create_patient_user(username="logout_patient", email="logout@example.com")
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.client.cookies[settings.AUTH_REFRESH_COOKIE_NAME] = str(refresh)

        response = self.client.post(
            self.logout_url,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        second_response = self.client.post(
            self.refresh_url,
            format="json",
        )
        self.assertEqual(second_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_updates_password_and_blacklists_refresh_cookie(self):
        user = self.create_patient_user(username="change_password_user", email="change@example.com")
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.client.cookies[settings.AUTH_REFRESH_COOKIE_NAME] = str(refresh)

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "StrongPass123!",
                "new_password": "NewStrongPass123!",
                "new_password_confirm": "NewStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewStrongPass123!"))

        self.client.credentials()
        refresh_response = self.client.post(self.refresh_url, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_rejects_incorrect_current_password(self):
        user = self.create_patient_user(username="wrong_current_password", email="wrong-current@example.com")
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "WrongPass123!",
                "new_password": "NewStrongPass123!",
                "new_password_confirm": "NewStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("current_password", response.data["details"])
