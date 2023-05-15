from django.urls import path

from .views import SampleDetailView, SampleListView

urlpatterns = [
    path("", SampleListView.as_view(), name="index"),
    path("<str:sample_id>/", SampleDetailView.as_view(), name="detail"),
]
