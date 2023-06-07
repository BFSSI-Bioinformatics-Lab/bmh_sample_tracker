from django.urls import include, path
from rest_framework import routers

from .views import SampleAPIView, SampleUploadView

router = routers.DefaultRouter()

app_name = "api"

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("sample/", SampleAPIView.as_view()),
    path("upload/", SampleUploadView.as_view(), name="sample-upload"),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
