import json

import pytest
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

from api.models import Sample
from api.views import SampleUploadView

pytestmark = pytest.mark.django_db


def test_sample_upload_requires_login(client, test_data):
    url = reverse("api:sample-upload")
    response = client.post(url, data=test_data, content_type="application/json")

    login_url = reverse(settings.LOGIN_URL)

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == f"{login_url}?next=/api/upload/"


def test_sample_upload(client, test_data, user_factory):
    url = reverse("api:sample-upload")
    factory = APIRequestFactory()
    user = user_factory()
    request = factory.post(url, data=test_data, format="json")
    request.user = user
    view = SampleUploadView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"success": True, "message": "Sample uploaded successfully."}

    # Assert that the samples are saved to the database
    assert Sample.objects.count() == 3

    # Assert the values of the saved samples
    sample1 = Sample.objects.get(sample_name="Sample 1")
    assert sample1.submitting_lab.lab_name == json.loads(test_data)[0]["submitting_lab"]


def test_sample_upload_invalid_lab(client, test_data_invalid_lab, user_factory):
    url = reverse("api:sample-upload")
    factory = APIRequestFactory()
    user = user_factory()
    request = factory.post(url, data=test_data_invalid_lab, format="json")
    request.user = user
    view = SampleUploadView.as_view()
    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not response.data["success"]
    response_errors = response.data["errors"]
    assert any(
        "Object with lab_name=9999999999 does not exist." in str(error)
        for field_errors in response_errors
        for errors in field_errors.values()
        for error in errors
    )
