from rest_framework.exceptions import APIException


class BookingBadRequestError(APIException):
    status_code = 400
    default_code = "bad_request"
    default_message = "Invalid booking request."

    def __init__(self, message=None, error="BAD_REQUEST"):
        super().__init__(
            {
                "error": error,
                "message": message or self.default_message,
            }
        )

    @classmethod
    def from_django_validation_error(cls, exc):
        message_dict = getattr(exc, "message_dict", None)
        if message_dict:
            first_value = next(iter(message_dict.values()))
            if isinstance(first_value, list):
                return cls(message=str(first_value[0] if first_value else ""))
            return cls(message=str(first_value))

        messages = getattr(exc, "messages", None)
        if messages:
            return cls(message=str(messages[0]))

        return cls()


class BookingConflictError(BookingBadRequestError):
    status_code = 409
    default_code = "conflict"
    default_message = "Booking conflict detected."

    def __init__(self, message=None):
        super().__init__(message=message or self.default_message, error="CONFLICT")


class SlotUnavailableError(BookingConflictError):
    default_message = "Requested slot is no longer available."


class DoctorBookedError(BookingConflictError):
    default_message = "Doctor already booked for this slot."


class PatientOverlapError(BookingConflictError):
    default_message = "Patient already has an overlapping appointment."


class BufferTimeViolationError(BookingConflictError):
    default_message = "Doctor buffer time is not respected for this slot."
