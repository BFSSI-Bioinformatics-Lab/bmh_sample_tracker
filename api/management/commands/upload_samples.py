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
        unique_lab_names = list(set(lab_name_list))
        lab_queryset = Lab.objects.filter(lab_name__in=unique_lab_names)
        lab_mapping = {lab.lab_name: lab.pk for lab in lab_queryset}
        df["submitting_lab"] = [lab_mapping[lab_name] for lab_name in lab_name_list]
        df["submitting_lab"] = df["submitting_lab"].astype(int)

        # convert project name to pk
        project_name_list = df["submitter_project"].tolist()
        unique_project_names = list(set(project_name_list))
        project_queryset = Project.objects.filter(project_name__in=unique_project_names)
        project_mapping = {project.project_name: project.pk for project in project_queryset}
        df["submitter_project"] = [project_mapping[project_name] for project_name in project_name_list]
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

        for obj in serializer.initial_data:
            individual_serializer = SampleSerializer(data=obj)
            if individual_serializer.is_valid():
                individual_instance = individual_serializer.save()
                print(f"Sample {individual_instance.sample_name} successfully.")
            else:
                errors = individual_serializer.errors
                print(errors)
