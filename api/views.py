from django.http import JsonResponse
from rest_framework import viewsets

from .models import Lab, Sample
from .serializers import SampleSerializer


class SampleList(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer


def get_lab_data(request):
    try:
        lab_data = Lab.objects.all()
        data = [{"id": item.id, "lab_name": item.lab_name} for item in lab_data]
        return JsonResponse(data, safe=False)
    except Lab.DoesNotExist:
        return JsonResponse({"error": "Foreign data does not exist."})
