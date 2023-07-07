from io import BytesIO

import pandas as pd
import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

from api.models import Lab
from api.tests.factories import LabFactory, ProjectFactory
from bmh_sample_tracker.users.tests.factories import UserFactory
from sample_database.forms import UploadForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_with_group():
    lab1 = LabFactory()
    lab2 = LabFactory()

    user = UserFactory()
    group1 = Group.objects.get(name=lab1.lab_name)
    group2 = Group.objects.get(name=lab2.lab_name)
    user.groups.set([group1, group2])

    return user


@pytest.fixture
def mock_excel_file():
    data = {"Col1": range(1, 11), "Col2": range(11, 21)}
    df = pd.DataFrame(data)
    excel_file_io = BytesIO()
    with pd.ExcelWriter(excel_file_io, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)

    excel_file = InMemoryUploadedFile(
        excel_file_io,
        None,
        "test_file.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        excel_file_io.getbuffer().nbytes,
        None,
    )
    return excel_file


@pytest.fixture
def large_mock_excel_file():
    data = {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    df = pd.DataFrame(data)
    file_buffer = BytesIO()
    with pd.ExcelWriter(file_buffer, engine="openpyxl", mode="xlsx") as writer:
        df.to_excel(writer)

    file_buffer.seek(0)
    large_file_content = file_buffer.read() * 1024 * 1024  # make file larger than 10 MB
    file = SimpleUploadedFile("test.xlsx", large_file_content)
    return file


def test_upload_form_both_projects_empty(user_with_group, mock_excel_file):
    lab = Lab.objects.get(lab_name=user_with_group.groups.first().name)
    form_data = {
        "lab": lab,
        "bmh_project": "",
        "submitter_project": "",
    }
    form_files = {"excel_file": mock_excel_file}
    form = UploadForm(data=form_data, files=form_files, user=user_with_group)
    assert not form.is_valid()
    assert "Both Existing Project and New Project cannot be empty." in form.non_field_errors()


def test_upload_form_both_projects_provided(user_with_group, mock_excel_file):
    lab = Lab.objects.get(lab_name=user_with_group.groups.first().name)
    project = ProjectFactory(supporting_lab=lab)
    form_data = {
        "lab": lab,
        "bmh_project": project,
        "submitter_project": "New Project",
    }
    form_files = {"excel_file": mock_excel_file}
    form = UploadForm(data=form_data, files=form_files, user=user_with_group)
    assert not form.is_valid()
    assert "Please select only one of Existing Project and New Project." in form.non_field_errors()


def test_upload_form_project_lab_not_match(user_with_group, mock_excel_file):
    lab1 = Lab.objects.get(lab_name=user_with_group.groups.first().name)
    lab2 = Lab.objects.get(lab_name=user_with_group.groups.last().name)
    project = ProjectFactory(supporting_lab=lab1)
    form_data = {
        "lab": lab2,
        "bmh_project": project,
        "submitter_project": "",
    }
    form_files = {"excel_file": mock_excel_file}
    form = UploadForm(data=form_data, files=form_files, user=user_with_group)
    assert not form.is_valid()
    assert "Selected project should be associated with the selected lab" in form.non_field_errors()


def test_upload_form_large_file(user_with_group, large_mock_excel_file):
    lab = Lab.objects.get(lab_name=user_with_group.groups.first().name)
    project = ProjectFactory(supporting_lab=lab)
    form_data = {
        "lab": lab,
        "bmh_project": project,
        "submitter_project": "",
    }
    form_files = {"excel_file": large_mock_excel_file}
    form = UploadForm(data=form_data, files=form_files, user=user_with_group)
    assert not form.is_valid()
    assert f"File size exceeds the maximum limit of {UploadForm.MAX_FILE_SIZE_MB} MB." in form.errors["excel_file"]
