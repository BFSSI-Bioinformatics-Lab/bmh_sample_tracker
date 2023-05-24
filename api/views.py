from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Sample
from .serializers import SampleSerializer


class SampleAPIView(APIView):
    def get(self, request):
        samples = Sample.objects.all()
        serializer = SampleSerializer(samples, many=True)
        return Response(serializer.data)
