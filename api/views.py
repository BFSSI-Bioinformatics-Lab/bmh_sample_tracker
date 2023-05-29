from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Sample
from .serializers import SampleSerializer


class SampleAPIView(LoginRequiredMixin, APIView):
    def get(self, request):
        user_labs = request.user.groups.all().values_list("id", flat=True)  # Retrieve user's lab group names
        samples = Sample.objects.filter(submitting_lab__in=user_labs)
        serializer = SampleSerializer(samples, many=True)
        return Response(serializer.data)
