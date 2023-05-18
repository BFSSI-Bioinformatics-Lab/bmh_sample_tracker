from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from api.models import Sample


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


def permission_denied_view(request):
    raise PermissionDenied()
