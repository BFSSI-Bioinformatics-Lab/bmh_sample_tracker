from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Aliquot, Batch, Sample
from .serializers import BatchCreationSerializer, SampleSerializer


class SampleAPIView(APIView):
    def get(self, request):
        samples = Sample.objects.all()
        serializer = SampleSerializer(samples, many=True)
        return Response(serializer.data)


class BatchCreationView(APIView):
    def post(self, request, format=None):
        serializer = BatchCreationSerializer(data=request.data)
        if serializer.is_valid():
            samples = serializer.validated_data["samples"]
            volumes = serializer.validated_data["volumes"]

            if len(samples) != len(volumes):
                return Response(
                    {"error": "Number of samples and volumes do not match"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Create the batch
            batch = Batch.objects.create(name="Batch Name")  # Provide appropriate data for the batch

            # Create aliquots with specified volumes
            for sample_id, volume in zip(samples, volumes):
                try:
                    sample = Sample.objects.get(pk=sample_id)
                    aliquot = Aliquot.objects.create(sample=sample, batch=batch)
                    aliquot.volume = volume
                    aliquot.save()
                except Sample.DoesNotExist:
                    return Response(
                        {"error": f"Sample with id {sample_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response({"success": "Batch created successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
