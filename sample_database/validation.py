import pandas as pd
from django.core.exceptions import ValidationError

from api.models import SAMPLE_TYPE_CHOICES, Sample


class DataCleanerValidator:
    REQUIRED_COLUMNS = [
        "sample_name",
        "tube_label",
        "sample_type",
        "sample_volume_in_ul",
        "requested_services",
        "genus",
        "species",
    ]

    STRING_COLUMNS = [
        "sample_name",
        "tube_label",
        "sample_type",
        "requested_services",
        "genus",
        "species",
        "strain",
        "isolate",
        "genus",
        "species",
        "subspecies_subtype_lineage",
        "comments",
        "culture_conditions",
        "dna_extraction_method",
    ]

    def __init__(self, file, bmh_project_name, submitter_project_name, lab_name):
        df = pd.read_excel(
            file,
            converters={
                "culture_date": self._date_converter,
                "dna_extraction_date": self._date_converter,
            },
        )

        n_records = df.shape[0]
        if n_records == 0:
            raise ValidationError("Empty file uploaded. No samples added.")

        self.df = df
        self.bmh_project = bmh_project_name
        self.submitter_project = submitter_project_name
        self.submitting_lab = lab_name

    def validate(self):
        self._validate_required_columns()
        self._validate_data_types()

    def clean(self):
        self._discard_extra_columns()
        self._strip_whitespace()
        self._convert_sample_type()

    def get_dataframe(self):
        final_df = self.df
        final_df["bmh_project"] = self.bmh_project.project_name if self.bmh_project else ""
        final_df["submitter_project"] = self.submitter_project
        final_df["submitting_lab"] = self.submitting_lab.lab_name
        return final_df

    def _validate_required_columns(self):
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
        if missing_columns:
            raise ValidationError(f'Missing required columns: {", ".join(missing_columns)}')

    def _validate_data_types(self):
        # right now this is done at the model level only
        pass

    def _discard_extra_columns(self):
        df = self.df
        model_fields = [f.name for f in Sample._meta.get_fields()]
        extra_columns = [col for col in df.columns if col not in model_fields]

        if extra_columns:
            raise ValidationError(f"Extra columns in data: {extra_columns}")

        self.df = df[[col for col in df.columns if col in model_fields]]

    def _strip_whitespace(self):
        string_columns = [col for col in self.df.columns if self.df[col].dtype == "object"]
        self.df[string_columns] = self.df[string_columns].apply(lambda x: x.str.strip())

    def _date_converter(self, date):
        if not date or date is None or date == "null":
            return ""
        if isinstance(date, str) and len(date) == 10:
            return date  # proper validation will be performed by serializer
        try:
            return date.date().isoformat()
        except AttributeError:
            return date

    def _convert_sample_type(self):
        sample_type_mapping = {value: key for key, value in SAMPLE_TYPE_CHOICES}
        self.df["sample_type"] = self.df["sample_type"].map(sample_type_mapping)
