from django.http import HttpResponse
from django.template import loader

from .models import Sample


def index(request):
    latest_samples = Sample.objects.order_by("-created")[:5]
    template = loader.get_template("database/index.html")
    context = {
        "latest_samples": latest_samples,
    }
    return HttpResponse(template.render(context, request))


def detail(request, sample_id):
    return HttpResponse("Hello, world. You're on the detail page for sample %s." % sample_id)
