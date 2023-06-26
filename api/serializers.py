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
    bmh_project = serializers.SlugRelatedField(
        slug_field="project_name", queryset=Project.objects.all(), allow_null=True
    )

    culture_date = serializers.DateField(allow_null=True, required=False)
    dna_extraction_date = serializers.DateField(allow_null=True, required=False)

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
                f"Sample with the same sample name '{sample_name}' already exists for lab '{submitting_lab}'."
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
