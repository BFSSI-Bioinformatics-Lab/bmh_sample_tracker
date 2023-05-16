from rest_framework import serializers

from .models import Lab, Sample


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ["id", "lab_name"]


class SampleSerializer(serializers.ModelSerializer):
    submitting_lab = LabSerializer()

    class Meta:
        model = Sample
        fields = "__all__"
