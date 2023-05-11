from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the database index.")


def list(request):
    return HttpResponse("Hello, world. This is supposed to be a list of all the samples.")


def detail(request, sample_id):
    return HttpResponse("Hello, world. You're on the detail page for sample %s." % sample_id)
