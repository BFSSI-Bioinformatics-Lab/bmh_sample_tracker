from rest_framework import serializers

from .models import (
    LG_CHAR,
    SM_CHAR,
    Aliquot,
    Lab,
    Project,
    Sample,
    Workflow,
    WorkflowExecution,
    generate_sample_id,
    well_validator,
)


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

    # allow nulls where appropriate
    well = serializers.CharField(max_length=SM_CHAR, validators=[well_validator])
    submitter_project = serializers.CharField(max_length=SM_CHAR, required=False, allow_null=True, allow_blank=True)
    strain = serializers.CharField(max_length=SM_CHAR, required=False, allow_null=True, allow_blank=True)
    isolate = serializers.CharField(max_length=SM_CHAR, required=False, allow_null=True, allow_blank=True)
    subspecies_subtype_lineage = serializers.CharField(
        max_length=LG_CHAR, required=False, allow_null=True, allow_blank=True
    )
    approx_genome_size_in_bp = serializers.IntegerField(required=False, allow_null=True)
    comments = serializers.CharField(
        allow_blank=True, required=False, allow_null=True, style={"base_template": "textarea.html"}
    )
    culture_date = serializers.DateField(required=False, allow_null=True)
    culture_conditions = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, style={"base_template": "textarea.html"}
    )
    dna_extraction_date = serializers.DateField(required=False, allow_null=True)
    dna_extraction_method = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, style={"base_template": "textarea.html"}
    )
    qubit_concentration_in_ng_ul = serializers.FloatField(required=False, allow_null=True)

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
