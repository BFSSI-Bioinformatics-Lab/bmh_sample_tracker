import pandas as pd
import pytest
from django.core.exceptions import ValidationError
from factory import Faker

from api.models import Sample
from api.tests.factories import LabFactory, ProjectFactory, SampleFactory
from api.utils import check_for_existing_sample, upload_samples, validate_project_lab, validated_sample

pytestmark = pytest.mark.django_db


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
def test_sample_data(test_project, test_lab):
    data = {
        "sample_name": [Faker("word"), Faker("word"), Faker("word")],
        "submitting_lab": [test_lab.lab_name, test_lab.lab_name, test_lab.lab_name],
        "submitter_project": [test_project.project_name, test_project.project_name, test_project.project_name],
    }
    yield pd.DataFrame(data)


def test_validate_project_lab_with_existing_lab_and_project(test_lab, test_project):
    try:
        validate_project_lab(
            {
                "sample_name": Faker("word"),
                "submitting_lab": test_lab.lab_name,
                "submitter_project": test_project.project_name,
            }
        )
    except ValidationError:
        pytest.fail("validate_project_lab should not raise a ValidationError for existing Lab and Project")


def test_validate_project_lab_with_nonexistent_lab(test_project):
    with pytest.raises(ValidationError) as e:
        sample_to_validate = {
            "sample_name": Faker("word"),
            "submitting_lab": Faker("word"),
            "submitter_project": test_project.project_name,
        }
        validate_project_lab(sample_to_validate)

    assert str(e.value) == "['Invalid submitting_lab']"


def test_validate_project_lab_with_nonexistent_project(test_lab):
    with pytest.raises(ValidationError) as e:
        sample_to_validate = {
            "sample_name": Faker("word"),
            "submitting_lab": test_lab.lab_name,
            "submitter_project": Faker("word"),
        }
        validate_project_lab(sample_to_validate)

    assert str(e.value) == "['Invalid submitter_project']"


def test_check_for_existing_sample_existing():
    sample = SampleFactory()
    assert check_for_existing_sample(sample.sample_name) is True
    sample.delete()


def test_check_for_existing_sample_not_existing():
    sample_name = Faker("word")

    assert check_for_existing_sample(sample_name) is False


def test_validated_sample_valid():
    lab = LabFactory()
    project = ProjectFactory()
    row = pd.Series(
        {
            "sample_name": "Sample 1",
            "submitting_lab": lab.lab_name,
            "submitter_project": project.project_name,
        }
    )

    result = validated_sample(row)
    assert result["success"] is True
    assert isinstance(result["sample"], Sample)
    lab.delete()
    project.delete()


def test_validated_sample_invalid():
    row = pd.Series(
        {
            "sample_name": "",
            "submitting_lab": "Lab1",
            "submitter_project": "Project1",
            # Add more columns and data as needed
        }
    )

    result = validated_sample(row)
    assert result["success"] is False
    assert "Skipping row" in result["message"]


def test_upload_samples(test_sample_data):
    result = upload_samples(test_sample_data)

    print(result)

    assert result["uploaded_count"] == 3
    assert result["skipped_count"] == 0
    assert len(result["messages"]) == 0
    for sample in result["samples"]:
        sample.delete()


def test_upload_samples_with_duplicates(test_sample_data):
    # Create a duplicate sample in the database
    duplicate_sample = Sample.objects.create(sample_name=test_sample_data["sample_name"][1])
    duplicate_sample.save()

    result = upload_samples(test_sample_data)

    assert result["uploaded_count"] == 2
    assert result["skipped_count"] == 1
    assert len(result["messages"]) == 1
    duplicate_sample.delete()
    for sample in result["samples"]:
        sample.delete()
