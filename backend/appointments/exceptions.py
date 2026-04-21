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
        if hasattr(exc, "message_dict") and exc.message_dict:
            first_key = next(iter(exc.message_dict))
            value = exc.message_dict[first_key]
            if isinstance(value, list) and value:
                return cls(message=str(value[0]))
            return cls(message=str(value))

        if hasattr(exc, "messages") and exc.messages:
            return cls(message=str(exc.messages[0]))

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
