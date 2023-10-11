import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from api.models import generate_sample_id
from api.tests.factories import LabFactory, ProjectFactory, SampleFactory
from bmh_sample_tracker.users.tests.factories import UserFactory


@pytest.fixture
def test_lab():
    lab = LabFactory()
    yield lab
    lab.delete()


@pytest.fixture
def test_project():
    project = ProjectFactory()
    yield project
    project.delete()


@pytest.fixture
def test_sample():
    sample = SampleFactory()
    yield sample
    sample.lab.delete()
    sample.project.delete()
    sample.delete()


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def test_user():
    User = get_user_model()
    return User.objects.create_user(email="test@example.com", password="test")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_data_invalid_lab():
    data = [
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample_1",
            "submitting_lab": 9999999999,
            "submitter_project": 9999999999999,
        },
    ]
    yield json.dumps(data)


@pytest.fixture
def test_data_missing_sample_id():
    project = ProjectFactory()
    lab = LabFactory()
    data = [
        {"sample_name": "Sample_1", "submitting_lab": lab.pk, "submitter_project": project.pk},
    ]
    yield json.dumps(data)


@pytest.fixture
def test_data_full():
    project = ProjectFactory()
    lab = LabFactory()
    data = [
        {
            "sample_name": "Sample_1",
            "tube_plate_label": "Tube1",
            "submitting_lab": lab.lab_name,
            "sample_type": "DNA",
            "sample_volume_in_ul": 25.0,
            "requested_services": "Sequencing",
            "genus": "GenusA",
            "species": "SpeciesA",
            "submitter_project": "proj1",
            "bmh_project": project.project_name,
        },
        {
            "sample_name": "Sample_2",
            "tube_plate_label": "Tube2",
            "submitting_lab": lab.lab_name,
            "sample_type": "CELLS",
            "sample_volume_in_ul": 35.0,
            "requested_services": "Sequencing",
            "genus": "GenusB",
            "species": "SpeciesB",
            "submitter_project": "proj2",
            "bmh_project": project.project_name,
        },
        {
            "sample_name": "Sample_3",
            "tube_plate_label": "Tube3",
            "submitting_lab": lab.lab_name,
            "sample_type": "AMPLICON",
            "sample_volume_in_ul": 45.0,
            "requested_services": "Sequencing",
            "genus": "GenusC",
            "species": "SpeciesC",
            "submitter_project": "proj3",
            "bmh_project": project.project_name,
        },
    ]
    yield data


@pytest.fixture
def test_excel_full():
    project = ProjectFactory()
    lab = LabFactory()
    data = [
        {
            "sample_name": "Sample_1",
            "tube_plate_label": "Tube1",
            "submitting_lab": lab.lab_name,
            "sample_type": "DNA",
            "sample_volume_in_ul": 25.0,
            "requested_services": "Sequencing",
            "genus": "GenusA",
            "species": "SpeciesA",
            "submitter_project": "proj1",
            "bmh_project": project.project_name,
        },
        {
            "sample_name": "Sample_2",
            "tube_plate_label": "Tube2",
            "submitting_lab": lab.lab_name,
            "sample_type": "CELLS",
            "sample_volume_in_ul": 35.0,
            "requested_services": "Sequencing",
            "genus": "GenusB",
            "species": "SpeciesB",
            "submitter_project": "proj2",
            "bmh_project": project.project_name,
        },
        {
            "sample_name": "Sample_3",
            "tube_plate_label": "Tube3",
            "submitting_lab": lab.lab_name,
            "sample_type": "AMPLICON",
            "sample_volume_in_ul": 45.0,
            "requested_services": "Sequencing",
            "genus": "GenusC",
            "species": "SpeciesC",
            "submitter_project": "proj3",
            "bmh_project": project.project_name,
        },
    ]
    yield data
