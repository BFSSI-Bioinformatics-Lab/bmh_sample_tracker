from math import isnan

from rest_framework import serializers

from .models import Aliquot, Lab, Project, Sample, Workflow, WorkflowExecution, generate_sample_id


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


# use this to transform project names into project objects if they exist
# this will handle validation on projects but will also allow project names
# to be nonexistent/null
class ProjectNameField(serializers.Field):
    def to_internal_value(self, data):
        if data:
            try:
                project = Project.objects.get(project_name=data)
                return project
            except Project.DoesNotExist:
                raise serializers.ValidationError(f"Project with name '{data}' does not exist.")
        return None

    def to_representation(self, value):
        if value:
            return value.project_name
        return None


class WorkFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ["id", "workflow_name"]


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    workflow = WorkFlowSerializer()

    class Meta:
        model = WorkflowExecution
        fields = "__all__"


class AliquotSerializer(serializers.ModelSerializer):
    workflow_executions = WorkflowExecutionSerializer(source="workflowexecution_set", many=True, read_only=True)

    class Meta:
        model = Aliquot
        fields = "__all__"


class SampleSerializer(serializers.ModelSerializer):
    submitting_lab = serializers.SlugRelatedField(slug_field="lab_name", queryset=Lab.objects.all())
    submitter_project = ProjectNameField(required=False, allow_null=True)

    latest_workflow_execution = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        fields = "__all__"

    def validate(self, attrs):
        submitting_lab = attrs.get("submitting_lab")
        sample_name = attrs.get("sample_name")

        # Check if a sample with the same submitting_lab and sample_name already exists
        if Sample.objects.filter(submitting_lab=submitting_lab, sample_name=sample_name).exists():
            raise serializers.ValidationError(
                f"Sample with the same sample name {sample_name} in this lab already exists. Skipping this sample"
            )

        return attrs

    def create(self, validated_data):
        validated_data["sample_id"] = generate_sample_id()
        return Sample.objects.create(**validated_data)

    def get_latest_workflow_execution(self, obj):
        aliquots = obj.aliquot_set.all()
        if aliquots.exists():
            latest_execution = aliquots.latest("workflowexecution__modified")
            serializer = WorkflowExecutionSerializer(latest_execution.workflowexecution_set.first())
            return serializer.data
        return None

    def to_internal_value(self, data):
        for key, value in data.items():
            if (isinstance(value, float) or isinstance(value, int)) and isnan(value):
                data[key] = None
        return super().to_internal_value(data)
