import pandas as pd
from django.core.management.base import BaseCommand

from api.models import SAMPLE_TYPE_CHOICES
from api.serializers import SampleSerializer


class Command(BaseCommand):
    help = "Populate the Samples table from a spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the spreadsheet file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        df = pd.read_excel(file_path, sheet_name="SSS-Template")

        # convert sample type to value
        sample_type_mapping = {value: key for key, value in SAMPLE_TYPE_CHOICES}
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
                print(f"Sample {individual_instance.sample_name} uploaded successfully.")
            else:
                errors = individual_serializer.errors
                print(f"Serializer errors: {errors}")
