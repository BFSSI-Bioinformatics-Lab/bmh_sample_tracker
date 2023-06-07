from rest_framework import serializers

from .models import Aliquot, Lab, Project, Sample, Workflow, WorkflowExecution


class LabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ["id", "lab_name"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "project_name"]


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
    sample_id = serializers.CharField()
    sample_name = serializers.CharField()
    well = serializers.CharField(required=False, allow_null=True)
    submitting_lab = serializers.PrimaryKeyRelatedField(queryset=Lab.objects.all(), required=False, allow_null=True)
    sample_type = serializers.ChoiceField(choices=Sample.SAMPLE_TYPE_CHOICES, required=False, allow_null=True)
    sample_volume_in_ul = serializers.FloatField(min_value=0.0, required=False, allow_null=True)
    requested_services = serializers.CharField(required=False, allow_null=True)
    submitter_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), required=False, allow_null=True
    )
    strain = serializers.CharField(required=False, allow_null=True)
    isolate = serializers.CharField(required=False, allow_null=True)
    genus = serializers.CharField(required=False, allow_null=True)
    species = serializers.CharField(required=False, allow_null=True)
    subspecies_subtype_lineage = serializers.CharField(required=False, allow_null=True)
    approx_genome_size_in_bp = serializers.IntegerField(required=False, allow_null=True)
    comments = serializers.CharField(required=False, allow_null=True)
    culture_date = serializers.DateField(required=False, allow_null=True)
    culture_conditions = serializers.CharField(required=False, allow_null=True)
    dna_extraction_date = serializers.DateField(required=False, allow_null=True)
    dna_extraction_method = serializers.CharField(required=False, allow_null=True)
    qubit_concentration_in_ng_ul = serializers.FloatField(min_value=0.0, required=False, allow_null=True)

    latest_workflow_execution = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        fields = "__all__"

    def validate(self, attrs):
        submitting_lab = attrs.get("submitting_lab")
        sample_name = attrs.get("sample_name")

        # Check if a sample with the same submitting_lab and sample_name already exists
        if Sample.objects.filter(submitting_lab=submitting_lab, sample_name=sample_name).exists():
            raise serializers.ValidationError("Sample with the same submitting lab and sample name already exists.")

        return attrs

    def create(self, validated_data):
        return Sample.objects.create(**validated_data)

    def get_latest_workflow_execution(self, obj):
        aliquots = obj.aliquot_set.all()
        if aliquots.exists():
            latest_execution = aliquots.latest("workflowexecution__modified")
            serializer = WorkflowExecutionSerializer(latest_execution.workflowexecution_set.first())
            return serializer.data
        return None
