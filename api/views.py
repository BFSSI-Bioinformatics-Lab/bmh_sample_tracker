from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lab, Sample
from .serializers import SampleSerializer


class SampleList(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer


class SampleAPIView(APIView):
    def get(self, request):
        samples = Sample.objects.all()
        serializer = SampleSerializer(samples, many=True)
        return Response(serializer.data)


def get_lab_data(request):
    try:
        lab_data = Lab.objects.all()
        data = [{"id": item.id, "lab_name": item.lab_name} for item in lab_data]
        return JsonResponse(data, safe=False)
    except Lab.DoesNotExist:
        return JsonResponse({"error": "Foreign data does not exist."})
