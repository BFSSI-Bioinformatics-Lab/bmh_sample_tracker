import pandas as pd
from django.core.management.base import BaseCommand

from api.utils import upload_samples


class Command(BaseCommand):
    help = "Populate the Samples table from a spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the spreadsheet file")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        df = pd.read_excel(file_path, sheet_name="SSS-Template")
        result = upload_samples(df)

        # Retrieve the uploaded_count, skipped_count, and messages
        # uploaded_count = result['uploaded_count']
        # skipped_count = result['skipped_count']
        messages = result["messages"]
        for m in messages:
            self.stdout.write(m)
