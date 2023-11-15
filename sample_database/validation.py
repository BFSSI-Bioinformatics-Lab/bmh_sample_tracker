from django.core.exceptions import ValidationError

from api.models import SAMPLE_TYPE_CHOICES, Sample


class DataCleanerValidator:
    REQUIRED_COLUMNS = [
        "sample_name",
        "sample_type",
        "tube_plate_label",
        "sample_volume_in_ul",
        "requested_services",
        "genus",
        "species",
    ]

    STRING_COLUMNS = [
        "sample_name",
        "well",
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

    def __init__(self, df, bmh_project_name, submitter_project_name, lab_name):
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
        self._no_extra_columns()

    def clean(self):
        self._strip_whitespace()
        self._convert_sample_type()
        self._remove_test_data()

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

    def _no_extra_columns(self):
        df = self.df
        model_fields = [f.name for f in Sample._meta.get_fields()]
        extra_columns = [col for col in df.columns if col not in model_fields]

        if extra_columns:
            raise ValidationError(f"Extra columns in data: {extra_columns}")

    def _strip_whitespace(self):
        for col in self.STRING_COLUMNS:
            if col in self.df:
                processed_values = []
                for item in self.df[col]:
                    if item is not None and str(item).strip() != "":
                        processed_values.append(str(item).strip())
                    else:
                        processed_values.append(item)
                self.df[col] = processed_values

    def _convert_sample_type(self):
        sample_type_mapping = {value: key for key, value in SAMPLE_TYPE_CHOICES}
        self.df["sample_type"] = self.df["sample_type"].map(sample_type_mapping)

    def _remove_test_data(self):
        if "test_donotuse" in self.df["sample_name"].values:
            df = self.df
            df = df[df["sample_name"] != "test_donotuse"]
            self.df = df
