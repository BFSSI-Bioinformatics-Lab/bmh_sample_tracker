from django.urls import path

from .views import SampleDetailView, SampleListView, permission_denied_view, workflow_assignment_form_view

urlpatterns = [
    path("", SampleListView.as_view(), name="index"),
    path("workflow_assignment/", workflow_assignment_form_view, name="form"),
    path("permission-denied/", permission_denied_view, name="permission-denied"),
    path("<str:sample_id>/", SampleDetailView.as_view(), name="detail"),
]
