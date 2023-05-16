from django.urls import path

from .views import SampleDetailView, SampleListView, workflow_assignment_form_view

urlpatterns = [
    path("", SampleListView.as_view(), name="index"),
    path("workflow_assignment/", workflow_assignment_form_view, name="form"),
    path("<str:sample_id>/", SampleDetailView.as_view(), name="detail"),
]
