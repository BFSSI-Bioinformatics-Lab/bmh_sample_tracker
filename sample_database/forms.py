import magic
from django import forms

from api.models import Lab, Project


class UploadForm(forms.Form):
    MAX_FILE_SIZE_MB = 10

    lab = forms.ModelChoiceField(queryset=Lab.objects.none(), to_field_name="lab_name")
    bmh_project = forms.ModelChoiceField(
        queryset=Project.objects.none(), to_field_name="project_name", required=False, label="Existing Project"
    )
    submitter_project = forms.CharField(max_length=250, required=False, label="New Project")
    excel_file = forms.FileField(label="Excel File")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_staff:
                self.fields["bmh_project"].queryset = Project.objects.all()
                self.fields["lab"].queryset = Lab.objects.all()
            else:
                user_group_names = user.groups.values_list("name", flat=True)
                self.fields["bmh_project"].queryset = Project.objects.filter(
                    supporting_lab__lab_name__in=user_group_names
                )
                self.fields["lab"].queryset = Lab.objects.filter(lab_name__in=user_group_names)

    def clean(self):
        cleaned_data = super().clean()
        bmh_project = cleaned_data.get("bmh_project")
        submitter_project = cleaned_data.get("submitter_project")
        submitting_lab = cleaned_data.get("lab")

        if bmh_project and submitter_project:
            raise forms.ValidationError("Please select only one of Existing Project and New Project.")

        if bmh_project is None and submitter_project is None:
            raise forms.ValidationError("Both Existing Project and New Project cannot be empty.")

        if bmh_project is not None:
            if bmh_project.supporting_lab.lab_name != submitting_lab.lab_name:
                raise forms.ValidationError("Selected project should be associated with the selected lab")

        file = cleaned_data.get("excel_file")

        if not file:
            raise forms.ValidationError("Empty file uploaded. Please upload a valid Excel file.")

        max_file_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        if file.size > max_file_size_bytes:
            raise forms.ValidationError(f"File size exceeds the maximum limit of {self.MAX_FILE_SIZE_MB} MB.")

        file_type = magic.from_buffer(file.read(), mime=True)
        if (
            file_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):  # MIME type for .xlsx files
            raise forms.ValidationError("Non-excel file uploaded. Currently, only excel (.xlsx) files are supported.")
        file.seek(0)

        return cleaned_data
