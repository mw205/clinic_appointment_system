from rest_framework import serializers

class AppointmentStatusCountModelSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()

class PeakHoursModelSerializer(serializers.Serializer):
    hour = serializers.IntegerField()
    count = serializers.IntegerField()

class AnalyticsSummaryModelSerializer(serializers.Serializer):
    total_appointments = serializers.IntegerField()
    total_consultations = serializers.IntegerField()
    no_show_rate = serializers.FloatField()
    appointment_status_counts = AppointmentStatusCountModelSerializer(many=True)
    peak_hours = PeakHoursModelSerializer(many=True)