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
    prescription_items = PrescriptionItemModelSerializer(many=True, read_only=True)
    requested_tests = RequestedTestModelSerializer(many=True, read_only=True)
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
        read_only_fields = ["id", "is_completed", "created_at", "updated_at"]


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