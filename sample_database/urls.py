from django.urls import path

from .views import CreateBatchView, SampleDetailView, SampleListView, permission_denied_view

urlpatterns = [
    path("", SampleListView.as_view(), name="index"),
    path("create_batch/", CreateBatchView.as_view(), name="batch_create"),
    path("permission-denied/", permission_denied_view, name="permission-denied"),
    path("<str:sample_id>/", SampleDetailView.as_view(), name="detail"),
]
