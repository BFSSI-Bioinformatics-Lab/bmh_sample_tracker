import json

import pandas as pd
from django.core.management.base import BaseCommand

from api.models import SAMPLE_TYPE_CHOICES, Lab, Project
from api.serializers import SampleSerializer


class Command(BaseCommand):
    help = "Populate the Samples table from a spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the spreadsheet file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        df = pd.read_excel(file_path, sheet_name="SSS-Template")

        # convert lab name to pk
        lab_name_list = df["submitting_lab"].tolist()
        lab_primary_key_list = Lab.objects.filter(lab_name__in=lab_name_list).values_list("pk", flat=True)
        lab_mapping = dict(zip(lab_name_list, lab_primary_key_list))
        df["submitting_lab"] = df["submitting_lab"].map(lab_mapping)
        df["submitting_lab"] = df["submitting_lab"].astype(int)

        # convert project name to pk
        project_name_list = df["submitter_project"].tolist()
        project_primary_key_list = Project.objects.filter(project_name__in=project_name_list).values_list(
            "pk", flat=True
        )
        project_mapping = dict(zip(project_name_list, project_primary_key_list))
        df["submitter_project"] = df["submitter_project"].map(project_mapping)
        df["submitter_project"] = df["submitter_project"].astype(int)

        # convert sample type to value
        sample_type_mapping = {value: key for key, value in SAMPLE_TYPE_CHOICES}
        # Assume 'df' is your pandas DataFrame with the 'sample_type' column
        df["sample_type"] = df["sample_type"].map(sample_type_mapping)

        # convert dates
        df["culture_date"] = df["culture_date"].dt.date
        df["dna_extraction_date"] = pd.to_datetime(df["culture_date"], errors="coerce")
        df["dna_extraction_date"] = df["dna_extraction_date"].dt.date

        data = df.to_dict(orient="records")
        serializer = SampleSerializer(data=data, many=True)

        if serializer.is_valid():
            sample_instance = serializer.save()
            if isinstance(sample_instance, list):
                n_samples = len(sample_instance)
            else:
                n_samples = 1
            print(f"{n_samples} Samples saved successfully.")
        else:
            errors = serializer.errors
            error_messages = "\n".join(json.dumps(err) for err in errors)
            print("Data validation failed. Errors:\n", error_messages)
