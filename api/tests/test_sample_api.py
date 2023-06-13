import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from api.tests.factories import LabFactory, SampleFactory
from api.views import SampleAPIView
from bmh_sample_tracker.users.tests.factories import UserFactory


@pytest.fixture
def staff_user():
    user = UserFactory(is_staff=True)
    return user


def _test_sample_view_for_user(user, expected_sample_ids, factory, url):
    request = factory.get(url)
    request.user = user
    view = SampleAPIView.as_view()
    response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(expected_sample_ids)
    assert {sample["id"] for sample in response.data} == set(expected_sample_ids)


@pytest.mark.django_db
def test_sample_api_view_only_shows_samples_from_user_labs(api_client, staff_user):
    # Create some test labs
    lab1 = LabFactory()
    lab2 = LabFactory()
    lab3 = LabFactory()

    # Create some test users and assign them to the labs
    user1 = UserFactory()
    group1 = Group.objects.get(name=lab1.lab_name)
    user1.groups.set([group1])

    user2 = UserFactory()
    group2 = Group.objects.get(name=lab2.lab_name)
    user2.groups.set([group2])

    user3 = UserFactory()
    user3.groups.set([group1, group2])

    # Create some test samples and assign them to the labs
    sample1 = SampleFactory(submitting_lab=lab1)
    sample2 = SampleFactory(submitting_lab=lab2)
    sample3 = SampleFactory(submitting_lab=lab3)

    factory = APIRequestFactory()
    url = reverse("api:sample-list")

    _test_sample_view_for_user(user1, [sample1.id], factory, url)
    _test_sample_view_for_user(user2, [sample2.id], factory, url)
    _test_sample_view_for_user(user3, [sample1.id, sample2.id], factory, url)
    _test_sample_view_for_user(staff_user, [sample1.id, sample2.id, sample3.id], factory, url)
