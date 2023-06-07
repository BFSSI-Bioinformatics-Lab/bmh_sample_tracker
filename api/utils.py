import pandas as pd
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.dateparse import parse_date

from api.models import Lab, Project, Sample


def validate_project_lab(row):
    sample_name = row.get("sample_name")

    # Check for required elements
    if not sample_name:
        raise ValidationError("Missing required elements")

    lab_name = row.get("submitting_lab")
    project_name = row.get("submitter_project")

    try:
        Lab.objects.get(lab_name=lab_name)
    except Lab.DoesNotExist:
        raise ValidationError("Invalid submitting_lab")

    try:
        Project.objects.get(project_name=project_name)
    except Project.DoesNotExist:
        raise ValidationError("Invalid submitter_project")


def check_for_existing_sample(sample_name):
    existing_sample = Sample.objects.filter(sample_name=sample_name).exists()
    if existing_sample:
        return True
    return False


def validated_sample(row):
    # assume row is a pd series
    sample_name = row.get("sample_name")
    if check_for_existing_sample(sample_name):
        return {
            "success": False,
            "message": f"Skipping duplicate sample: {sample_name}",
        }

    try:
        validate_project_lab(row)
        # Replace empty strings with None
        row = {k: v if v is not None else None for k, v in row.items()}

        # Parse date fields only if they are not empty
        culture_date = parse_date(str(row.get("culture_date"))) if pd.notnull(row.get("culture_date")) else None
        dna_extraction_date = (
            parse_date(str(row.get("dna_extraction_date"))) if pd.notnull(row.get("dna_extraction_date")) else None
        )

        sample_volume_in_ul = (
            float(row.get("sample_volume_in_ul")) if pd.notnull(row.get("sample_volume_in_ul")) else None
        )
        approx_genome_size_in_bp = (
            float(row.get("approx_genome_size_in_bp")) if pd.notnull(row.get("approx_genome_size_in_bp")) else None
        )
        qubit_concentration_in_ng_ul = (
            float(row.get("qubit_concentration_in_ng_ul"))
            if pd.notnull(row.get("qubit_concentration_in_ng_ul"))
            else None
        )

        sample = Sample(
            sample_name=sample_name,
            well=row.get("well"),
            submitting_lab=Lab.objects.get(lab_name=row.get("submitting_lab")),
            sample_type=row.get("sample_type"),
            sample_volume_in_ul=sample_volume_in_ul,
            requested_services=row.get("requested_services"),
            submitter_project=Project.objects.get(project_name=row.get("submitter_project")),
            strain=row.get("strain"),
            isolate=str(row.get("isolate")),  # convert to string if not
            genus=row.get("genus"),
            species=row.get("species"),
            subspecies_subtype_lineage=row.get("subspecies_subtype_lineage"),
            approx_genome_size_in_bp=approx_genome_size_in_bp,
            comments=row.get("comments"),
            culture_date=culture_date,
            culture_conditions=row.get("culture_conditions"),
            dna_extraction_date=dna_extraction_date,
            dna_extraction_method=row.get("dna_extraction_method"),
            qubit_concentration_in_ng_ul=qubit_concentration_in_ng_ul,
        )

        sample.full_clean()  # Perform full model validation
        return {"success": True, "sample": sample}
    except (ValidationError, ObjectDoesNotExist) as e:
        return {
            "success": False,
            "message": f"Skipping row: {row.values} - {str(e)}",
        }


def upload_samples(df):
    uploaded_count = 0
    skipped_count = 0
    messages = []
    samples = []

    for _, row in df.iterrows():
        validated = validated_sample(row)
        if validated["success"]:
            sample = validated["sample"]
            sample.save()
            uploaded_count += 1
            samples.append(sample)
        else:
            skipped_count += 1
            messages.append(validated["message"])

    return {
        "uploaded_count": uploaded_count,
        "skipped_count": skipped_count,
        "messages": messages,
        "samples": samples,
    }
