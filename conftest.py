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
def test_data():
    project = ProjectFactory()
    lab = LabFactory()
    data = [
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 1",
            "submitting_lab": lab.lab_name,
            "submitter_project": project.project_name,
        },
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 2",
            "submitting_lab": lab.lab_name,
            "submitter_project": project.project_name,
        },
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 3",
            "submitting_lab": lab.lab_name,
            "submitter_project": project.project_name,
        },
    ]
    yield json.dumps(data)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_data_invalid_lab():
    data = [
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 1",
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
        {"sample_name": "Sample 1", "submitting_lab": lab.pk, "submitter_project": project.pk},
    ]
    yield json.dumps(data)


@pytest.fixture
def test_data_full():
    project = ProjectFactory()
    lab = LabFactory()
    data = [
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 1",
            "well": "",
            "submitting_lab": lab.lab_name,
            "sample_type": "",
            "sample_volume_in_ul": "",
            "submitter_project": project.project_name,
            "strain": "",
            "isolate": "",
            "genus": "",
            "species": "",
            "subspecies_subtype_lineage": "",
            "approx_genome_size_in_bp": "",
            "comments": "",
            "culture_date": "",
            "culture_conditions": "",
            "dna_extraction_date": "",
            "dna_extraction_method": "",
            "qubit_concentration_in_ng_ul": "",
        },
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 2",
            "well": "",
            "submitting_lab": lab.lab_name,
            "sample_type": "",
            "sample_volume_in_ul": "",
            "submitter_project": project.project_name,
            "strain": "",
            "isolate": "",
            "genus": "",
            "species": "",
            "subspecies_subtype_lineage": "",
            "approx_genome_size_in_bp": "",
            "comments": "",
            "culture_date": "",
            "culture_conditions": "",
            "dna_extraction_date": "",
            "dna_extraction_method": "",
            "qubit_concentration_in_ng_ul": "",
        },
        {
            "sample_id": generate_sample_id(),
            "sample_name": "Sample 3",
            "well": "",
            "submitting_lab": lab.lab_name,
            "sample_type": "",
            "sample_volume_in_ul": "",
            "submitter_project": project.project_name,
            "strain": "",
            "isolate": "",
            "genus": "",
            "species": "",
            "subspecies_subtype_lineage": "",
            "approx_genome_size_in_bp": "",
            "comments": "",
            "culture_date": "",
            "culture_conditions": "",
            "dna_extraction_date": "",
            "dna_extraction_method": "",
            "qubit_concentration_in_ng_ul": "",
        },
    ]
    yield data
