import io

import pandas as pd
import pytest
from django.conf import settings
from django.contrib.messages import get_messages
from django.core.files.base import ContentFile
from django.urls import reverse

from api.models import Sample, generate_sample_id
from api.tests.factories import LabFactory, ProjectFactory


@pytest.mark.django_db
def test_sample_upload_form_view(client, test_user, test_data_full):
    client.login(username=test_user.email, password="test")

    df = pd.DataFrame.from_records(test_data_full)
    n_records = df.shape[0]
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    response = client.post(reverse("sample_database:upload-form"), {"excel_file": excel_file}, format="multipart")

    assert response.status_code == 302, f"Expected 302, got {response.status_code} instead"
    assert Sample.objects.count() == n_records, f"Expected {len(df)}, got {Sample.objects.count()} instead"
    messages = list(get_messages(response.wsgi_request))
    assert any(
        "Data uploaded successfully" in str(message) for message in messages
    ), "Expected success message not found"


@pytest.fixture
def test_data_incomplete_columns():
    project = ProjectFactory()
    lab = LabFactory()
    data = [
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 1",
            "submitting_lab": lab.lab_name,
        },
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 2",
            "submitter_project": project.project_name,
        },
        {
            "sample_id": generate_sample_id(),
        },
    ]
    yield data


@pytest.mark.django_db
def test_sample_upload_form_view_missing_columns(client, test_user, test_data_incomplete_columns):
    client.login(username=test_user.email, password="test")

    df = pd.DataFrame.from_records(test_data_incomplete_columns)
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    response = client.post(reverse("sample_database:upload-form"), {"excel_file": excel_file}, format="multipart")

    assert response.status_code == 302, f"Expected 302, got {response.status_code} instead"
    messages = list(get_messages(response.wsgi_request))
    assert any("Missing required columns:" in str(message) for message in messages), "Expected error message not found"


@pytest.fixture
def test_data_bad_date(test_data_full):
    test_data_full[0]["culture_date"] = "lol"
    return test_data_full


@pytest.mark.django_db
def test_sample_upload_form_view_bad_date(client, test_user, test_data_bad_date):
    client.login(username=test_user.email, password="test")

    df = pd.DataFrame.from_records(test_data_bad_date)
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    response = client.post(reverse("sample_database:upload-form"), {"excel_file": excel_file}, format="multipart")

    assert response.status_code == 302, f"Expected 302, got {response.status_code} instead"
    messages = list(get_messages(response.wsgi_request))
    assert any("Date has wrong format." in str(message) for message in messages), "Expected error message not found"


@pytest.mark.django_db
def test_sample_upload_form_view_requires_login(client, test_data):
    url = reverse("sample_database:upload-form")
    response = client.post(url, data=test_data, content_type="application/json")

    login_url = reverse(settings.LOGIN_URL)

    assert response.status_code == 302
    assert response.url == f"{login_url}?next={url}"


@pytest.mark.django_db
def test_sample_upload_form_view_invalid_file_type(client, test_user, test_data_full):
    client.login(username=test_user.email, password="test")

    df = pd.DataFrame.from_records(test_data_full)

    text_file = io.BytesIO()
    df.to_csv(text_file, index=False)
    text_file.seek(0)

    text_file_content = ContentFile(text_file.read(), name="test.txt")

    response = client.post(
        reverse("sample_database:upload-form"), {"excel_file": text_file_content}, format="multipart"
    )

    assert response.status_code == 302, f"Expected 302, got {response.status_code} instead"
    messages = list(get_messages(response.wsgi_request))
    assert any("Non-excel file uploaded." in str(message) for message in messages), "Expected error message not found"
