from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Sample
from .serializers import SampleSerializer


class SampleAPIView(APIView, LoginRequiredMixin):
    def get(self, request):
        samples = Sample.objects.all()
        serializer = SampleSerializer(samples, many=True)
        return Response(serializer.data)


# class SampleAPIView(APIView, LoginRequiredMixin):
#     def get(self, request):
#         print("##############################")
#         print(request.user.groups)
#         print("##############################")
#         user_labs = request.user.groups.values_list('name', flat=True)  # Retrieve user's lab group names
#         samples = Sample.objects.filter(lab__name__in=user_labs)
#         serializer = SampleSerializer(samples, many=True)
#         return Response(serializer.data)
