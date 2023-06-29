import json

import magic
import pandas as pd
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from api.models import Aliquot, Batch, Sample, WorkflowExecution
from api.views import SampleUploadView

from .forms import UploadForm


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SampleListView(LoginRequiredMixin, TemplateView):
    template_name = "sample_database/index.html"
    login_url = "/accounts/login/"


class SampleDetailView(LoginRequiredMixin, DetailView):
    model = Sample
    template_name = "sample_database/sample_detail.html"
    login_url = "/accounts/login/"

    def get_object(self):
        sample_id = self.kwargs["sample_id"]
        return get_object_or_404(Sample, sample_id=sample_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample = self.object
        aliquots = Aliquot.objects.filter(sample=sample)
        batches = Batch.objects.filter(aliquot__in=aliquots)
        executions = WorkflowExecution.objects.filter(aliquot__in=aliquots)
        context["aliquots"] = aliquots
        context["batches"] = batches
        context["executions"] = executions
        return context


class SampleUploadFormView(LoginRequiredMixin, FormView):
    login_url = "/accounts/login/"
    template_name = "sample_database/upload.html"
    form_class = UploadForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def date_converter(self, date):
        if not date or date is None or date == "null":
            return ""  # return empty string for empty, None, or null values
        if isinstance(date, str) and len(date) == 10:
            return (
                date  # return ISO format date as is. Note that proper validation will be performed by the serializer
            )
        try:
            return date.date().isoformat()  # convert date to ISO format
        except AttributeError:  # handles non-datetime values
            return date  # return input as is for other cases

    def form_valid(self, form):
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{field}: {error}")
            return redirect(reverse("sample_database:upload-form"))

        file = form.cleaned_data["excel_file"]
        file_type = magic.from_buffer(file.read(), mime=True)
        if (
            file_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):  # MIME type for .xlsx files
            messages.error(self.request, "Non-excel file uploaded. Currently, only excel (.xlsx) files are supported.")
            return redirect(reverse("sample_database:upload-form"))
        file.seek(0)

        lab_name = form.cleaned_data["lab"]
        bmh_project_name = form.cleaned_data["bmh_project"]
        submitter_project_name = form.cleaned_data["submitter_project"]

        df = pd.read_excel(
            file,
            converters={
                "culture_date": self.date_converter,
                "dna_extraction_date": self.date_converter,
            },
        )

        df["bmh_project"] = bmh_project_name
        df["submitter_project"] = submitter_project_name
        df["submitting_lab"] = lab_name

        model_fields = [f.name for f in Sample._meta.get_fields()]
        required_columns = [
            "sample_name",
            "tube_label",
            "submitting_lab",
            "sample_type",
            "sample_volume_in_ul",
            "requested_services",
            "genus",
            "species",
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            messages.error(self.request, f'Missing required columns: {", ".join(missing_columns)}')
            return redirect(reverse("sample_database:upload-form"))

        n_records = df.shape[0]
        if n_records == 0:
            messages.error(self.request, "Empty file uploaded. No samples added.")
            return redirect(reverse("sample_database:upload-form"))

        # keep only the columns that exist in the Sample model
        df = df[[col for col in df.columns if col in model_fields]]

        data = df.to_dict(orient="records")
        json_data = json.dumps(data)

        view = SampleUploadView()
        response = view.post(self.request, data=json_data)

        # Handle the API response based on the status code
        if response.status_code == 201:
            messages.success(self.request, "Data uploaded successfully.")
            return redirect(reverse("sample_database:sample-db"))
        elif response.status_code == 400:
            errors = response.data["errors"]
            if isinstance(errors, list):
                # If errors is a list of dictionaries
                for error_dict in errors:
                    for field, error_messages in error_dict.items():
                        for error_message in error_messages:
                            messages.error(self.request, f"Error in field {field}: {error_message}")
                            return redirect(reverse("sample_database:upload-form"))
            else:
                # If errors is a dictionary
                for field, error_messages in errors.items():
                    for error_message in error_messages:
                        messages.error(self.request, f"Error in field {field}: {error_message}")
                        return redirect(reverse("sample_database:upload-form"))
        elif response.status_code == 500:
            error_message = response.data["errors"]
            messages.error(self.request, f"Internal server error: {error_message}")
            return redirect(reverse("sample_database:upload-form"))
            # TODO: log this error somewhere
        else:
            # Handle other status codes if necessary
            pass

        # Redirect the user back to the form
        return redirect(reverse("sample_database:upload-form"))
