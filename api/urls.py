from django.urls import include, path
from rest_framework import routers

from .views import SampleList, get_lab_data

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("sample/", SampleList.as_view(actions={"post": "list", "get": "list"})),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("get_lab_data/", get_lab_data, name="get_foreign_data"),
]
