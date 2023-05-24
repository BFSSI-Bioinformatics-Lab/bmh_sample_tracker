import pandas as pd
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from api.models import Lab, Project, Sample


class Command(BaseCommand):
    help = "Populate the Samples table from a spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the spreadsheet file")

    def validate_project_lab(self, row):
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

    def handle(self, *args, **options):
        file_path = options["file_path"]
        df = pd.read_excel(file_path, sheet_name="SSS-Template")

        num_submitted = 0
        for _, row in df.iterrows():
            sample_name = row.get("sample_name")

            existing_sample = Sample.objects.filter(sample_name=sample_name).exists()
            if existing_sample:
                self.stdout.write(self.style.WARNING(f"Skipping duplicate sample: {sample_name}"))
                continue

            try:
                self.validate_project_lab(row)
                # Replace empty strings with None
                row = row.where(pd.notnull(row), None)

                # Parse date fields only if they are not empty
                culture_date = (
                    parse_date(str(row.get("culture_date"))) if pd.notnull(row.get("culture_date")) else None
                )
                dna_extraction_date = (
                    parse_date(str(row.get("dna_extraction_date")))
                    if pd.notnull(row.get("dna_extraction_date"))
                    else None
                )

                sample_volume_in_ul = (
                    float(row.get("sample_volume_in_ul")) if pd.notnull(row.get("sample_volume_in_ul")) else None
                )
                approx_genome_size_in_bp = (
                    float(row.get("approx_genome_size_in_bp"))
                    if pd.notnull(row.get("approx_genome_size_in_bp"))
                    else None
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
                sample.save()
                num_submitted += 1
            except (ValidationError, ObjectDoesNotExist) as e:
                self.stdout.write(self.style.WARNING(f"Skipping row: {row.values} - {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully submitted {num_submitted} samples!"))
