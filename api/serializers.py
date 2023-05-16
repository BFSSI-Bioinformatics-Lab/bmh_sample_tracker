from rest_framework import serializers

from .models import Lab, Project, Sample


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ["id", "lab_name"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "project_name"]


class SampleSerializer(serializers.ModelSerializer):
    submitting_lab = LabSerializer()
    submitter_project = ProjectSerializer(allow_null=True, required=False)

    class Meta:
        model = Sample
        fields = "__all__"
