from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Setup roles and permissions"

    def handle(self, *args, **kwargs):
        roles = ['Patient', 'Doctor', 'Receptionist', 'Admin']

        for role in roles:
            group, created = Group.objects.get_or_create(name=role)

            if role == 'Patient':
                perms = Permission.objects.filter(
                    codename__in=['add_appointment', 'view_appointment']
                )
                group.permissions.set(perms)

            elif role == 'Doctor':
                perms = Permission.objects.filter(
                    codename__in=['view_appointment', 'change_appointment']
                )
                group.permissions.set(perms)

            elif role == 'Receptionist':
                perms = Permission.objects.filter(
                    codename__in=['view_appointment', 'change_appointment']
                )
                group.permissions.set(perms)

            elif role == 'Admin':
                perms = Permission.objects.all()
                group.permissions.set(perms)

        self.stdout.write(self.style.SUCCESS("Roles created successfully"))