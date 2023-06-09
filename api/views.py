import json

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Sample
from .serializers import SampleSerializer

# TODO: are the login urls required?


class SampleAPIView(LoginRequiredMixin, APIView):
    login_url = "/accounts/login/"

    def get(self, request):
        if request.user.is_superuser or request.user.is_staff:
            samples = Sample.objects.all()
        else:
            user_labs = request.user.groups.all().values_list("id", flat=True)  # Retrieve user's lab group ids
            samples = Sample.objects.filter(submitting_lab__in=user_labs)

        serializer = SampleSerializer(samples, many=True)

        return Response(serializer.data)


class SampleUploadView(LoginRequiredMixin, APIView):
    login_url = "/accounts/login/"

    def post(self, request, data=None):
        data = data if data else request.data
        serializer = SampleSerializer(data=json.loads(data), many=True)

        if serializer.is_valid():
            sample_instances = serializer.save()  # could be one or more samples

            if isinstance(sample_instances, list):
                for sample_instance in sample_instances:
                    sample_instance.save()
            else:
                sample_instances.save()

            response_data = {
                "success": True,
                "message": "Sample uploaded successfully.",
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {"success": False, "errors": serializer.errors}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
