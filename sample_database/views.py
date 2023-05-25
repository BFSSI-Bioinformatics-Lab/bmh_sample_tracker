from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from api.models import Aliquot, Batch, Sample, WorkflowExecution


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SampleListView(TemplateView, LoginRequiredMixin):
    template_name = "sample_database/index.html"
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"


class SampleDetailView(DetailView, LoginRequiredMixin):
    model = Sample
    template_name = "sample_database/sample_detail.html"
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

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
