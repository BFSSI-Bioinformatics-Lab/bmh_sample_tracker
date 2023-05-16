from django.urls import include, path
from rest_framework import routers

from .views import SampleAPIView

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("sample/", SampleAPIView.as_view()),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
