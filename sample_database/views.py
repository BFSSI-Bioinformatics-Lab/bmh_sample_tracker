import json

import numpy as np
import pandas as pd
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from api.models import Aliquot, Batch, Sample, WorkflowExecution
from api.views import SampleUploadView

from .forms import UploadForm
from .validation import DataCleanerValidator


def sample_management_view(request):
    return render(request, "sample_database/sample_management.html")

@method_decorator(ensure_csrf_cookie, name="dispatch")
class SampleListView(ListView):
    model = Sample
    template_name = "sample_database/sample_list.html"
    context_object_name = "samples"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Sample.objects.all()
        else:
            user_labs = self.request.user.groups.all().values_list("id", flat=True)
            return Sample.objects.filter(submitting_lab__in=user_labs)


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

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

    def form_valid(self, form):
        file = form.cleaned_data["excel_file"]
        lab_name = form.cleaned_data["lab"]
        bmh_project_name = form.cleaned_data["bmh_project"]
        submitter_project_name = form.cleaned_data["submitter_project"]

        df = (
            pd.read_excel(
                file,
                dtype={"approx_genome_size_in_bp": "Int64"},
                converters={
                    "culture_date": self._date_converter,
                    "dna_extraction_date": self._date_converter,
                },
            )
            .fillna(np.nan)
            .replace([np.nan], [None])
        )

        cleaner_validator = DataCleanerValidator(df, bmh_project_name, submitter_project_name, lab_name)

        try:
            cleaner_validator.validate()
        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect(reverse("sample_database:upload-form"))

        cleaner_validator.clean()
        df = cleaner_validator.get_dataframe()

        data = df.to_dict(orient="records")
        json_data = json.dumps(data)

        view = SampleUploadView()
        response = view.post(self.request, data=json_data)

        # Handle the API response based on the status code
        if response.status_code == 201:
            messages.success(self.request, "Data uploaded successfully.")
            slack_message = {
                "text": f"New sample data uploaded by {self.request.user.get_username()}."
            }
            try:
                requests.post(settings.SLACK_WEBHOOK_URL, json=slack_message)
                print(f"Atttepting to send Slack notification: '{slack_message}'")
            except requests.RequestException as e:
                # Log the error, but don't disrupt the user experience
                print(f"Failed to send Slack notification: {e}")

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

    def _date_converter(self, date):
        if not date or date is None or date == "null":
            return None
        if isinstance(date, str) and len(date) == 10:
            return date  # proper validation will be performed by serializer
        try:
            return date.date().isoformat()
        except AttributeError:
            return date
