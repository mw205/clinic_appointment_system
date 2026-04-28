from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Set up auth groups and permissions"

    def handle(self, *args, **kwargs):
        group_names = ['Patient', 'Doctor', 'Receptionist', 'Admin']

        for group_name in group_names:
            group, created = Group.objects.get_or_create(name=group_name)

            if group_name == 'Patient':
                perms = Permission.objects.filter(
                    codename__in=['add_appointment', 'view_appointment']
                )
                group.permissions.set(perms)

            elif group_name == 'Doctor':
                perms = Permission.objects.filter(
                    codename__in=['view_appointment', 'change_appointment']
                )
                group.permissions.set(perms)

            elif group_name == 'Receptionist':
                perms = Permission.objects.filter(
                    codename__in=['view_appointment', 'change_appointment']
                )
                group.permissions.set(perms)

            elif group_name == 'Admin':
                perms = Permission.objects.all()
                group.permissions.set(perms)

        self.stdout.write(self.style.SUCCESS("Auth groups created successfully"))
