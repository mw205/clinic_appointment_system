from rest_framework import serializers
from consultations.models import ConsultationRecord, PrescriptionItem, RequestedTest

class PrescriptionItemModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = ["id", "drug", "dose", "duration", "instructions"]

class RequestedTestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedTest
        fields = ["id", "test_name", "notes"]

class ConsultationRecordModelSerializer(serializers.ModelSerializer):
    prescription_items = PrescriptionItemModelSerializer(many=True, required=False)
    requested_tests = RequestedTestModelSerializer(many=True, required=False)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = ConsultationRecord
        fields = [
            "id",
            "appointment",
            "doctor",
            "diagnosis",
            "notes",
            "is_completed",
            "completed_at",
            "prescription_items",
            "requested_tests",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "doctor", "is_completed", "created_at", "updated_at"]

    def validate_appointment(self, appointment):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            doctor_profile = getattr(request.user, "doctorprofile", None)
            if doctor_profile and appointment.doctor_id != doctor_profile.id:
                raise serializers.ValidationError("You can only write consultations for your own appointments.")
        return appointment

    def create(self, validated_data):
        prescription_items = validated_data.pop("prescription_items", [])
        requested_tests = validated_data.pop("requested_tests", [])
        consultation = ConsultationRecord.objects.create(**validated_data)
        PrescriptionItem.objects.bulk_create(
            [PrescriptionItem(consultation=consultation, **item) for item in prescription_items]
        )
        RequestedTest.objects.bulk_create(
            [RequestedTest(consultation=consultation, **item) for item in requested_tests]
        )
        return consultation

    def update(self, instance, validated_data):
        prescription_items = validated_data.pop("prescription_items", None)
        requested_tests = validated_data.pop("requested_tests", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if prescription_items is not None:
            instance.prescription_items.all().delete()
            PrescriptionItem.objects.bulk_create(
                [PrescriptionItem(consultation=instance, **item) for item in prescription_items]
            )

        if requested_tests is not None:
            instance.requested_tests.all().delete()
            RequestedTest.objects.bulk_create(
                [RequestedTest(consultation=instance, **item) for item in requested_tests]
            )

        return instance


class ConsultationSummaryModelSerializer(serializers.ModelSerializer):
    prescription_items = PrescriptionItemModelSerializer(many=True, read_only=True)
    requested_tests = RequestedTestModelSerializer(many=True, read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = ConsultationRecord
        fields = [
            "id",
            "appointment",
            "diagnosis",
            "is_completed",
            "prescription_items",
            "requested_tests",
        ]
        read_only_fields = [
            "id",
            "appointment",
            "diagnosis",
            "is_completed",
            "prescription_items",
            "requested_tests",
        ]
