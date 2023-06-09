from django.urls import path

from .views import SampleDetailView, SampleListView, SampleUploadFormView

app_name = "sample_database"
urlpatterns = [
    path("", SampleListView.as_view(), name="sample-db"),
    path("upload/", SampleUploadFormView.as_view(), name="upload-form"),
    path("<str:sample_id>/", SampleDetailView.as_view(), name="detail"),
]
