from rest_framework import viewsets

from .models import Sample
from .serializers import SampleSerializer


class SampleList(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
