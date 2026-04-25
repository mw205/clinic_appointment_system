PATIENT = "Patient"
DOCTOR = "Doctor"
RECEPTIONIST = "Receptionist"
ADMIN = "Admin"


def user_has_group(user, group_name):
    # Check if the user belongs to a group with the specified name
    return bool(
        user and user.is_authenticated 
        and user.groups.filter(name=group_name).exists() 
    )


def user_has_any_group(user, group_names):
    # Check if the user belongs to any of the specified groups
    return bool(
        user and user.is_authenticated 
        and user.groups.filter(name__in=group_names).exists() 
    )


def is_patient(user):
    return user_has_group(user, PATIENT)

def is_doctor(user):
    return user_has_group(user, DOCTOR)

def is_receptionist(user):
    return user_has_group(user, RECEPTIONIST)

def is_admin(user):
    return user_has_group(user, ADMIN)