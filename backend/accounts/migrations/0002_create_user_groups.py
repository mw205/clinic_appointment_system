from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    roles = ["Patient", "Doctor", "Receptionist", "Admin"]

    for role in roles:
        Group.objects.get_or_create(name=role)


def delete_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    roles = ["Patient", "Doctor", "Receptionist", "Admin"]

    Group.objects.filter(name__in=roles).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ]