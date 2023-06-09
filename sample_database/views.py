import json

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

from api.models import SAMPLE_TYPE_CHOICES, Aliquot, Batch, Sample, WorkflowExecution
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
    # success_url = reverse_lazy('success')

    def form_valid(self, form):
        file = form.cleaned_data["excel_file"]
        df = pd.read_excel(file)

        # convert sample type to value
        sample_type_mapping = {value: key for key, value in SAMPLE_TYPE_CHOICES}
        df["sample_type"] = df["sample_type"].map(sample_type_mapping)

        # convert the dates to strings
        df["culture_date"] = df["culture_date"].apply(lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else x)
        df["dna_extraction_date"] = df["dna_extraction_date"].apply(
            lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else x
        )

        data = df.to_dict(orient="records")
        json_data = json.dumps(data)

        view = SampleUploadView()
        response = view.post(self.request, data=json_data)

        # Handle the API response based on the status code
        if response.status_code == 201:
            messages.success(self.request, "Data uploaded successfully.")
            print(self.request, "Data uploaded successfully.")
        elif response.status_code == 400:
            errors = response.data["errors"]
            if isinstance(errors, list):
                # If errors is a list of dictionaries
                for error_dict in errors:
                    for field, error_messages in error_dict.items():
                        for error_message in error_messages:
                            messages.error(self.request, f"Error in field {field}: {error_message}")
            else:
                # If errors is a dictionary
                for field, error_messages in errors.items():
                    for error_message in error_messages:
                        messages.error(self.request, f"Error in field {field}: {error_message}")
        elif response.status_code == 500:
            error_message = response.data["errors"]
            messages.error(self.request, f"Internal server error: {error_message}")
        else:
            # Handle other status codes if necessary
            pass

        # Redirect the user back to the form
        return redirect(reverse("sample_database:upload-form"))
