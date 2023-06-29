from django import forms

from api.models import Lab, Project


class UploadForm(forms.Form):
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

        if bmh_project and submitter_project:
            raise forms.ValidationError("Please select only one of Existing Project and New Project.")

        if bmh_project is None and submitter_project is None:
            raise forms.ValidationError("Both Existing Project and New Project cannot be empty.")

        return cleaned_data
