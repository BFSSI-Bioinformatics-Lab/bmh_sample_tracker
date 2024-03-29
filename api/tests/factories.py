from django.contrib.auth.models import Group
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from api.models import SAMPLE_TYPE_CHOICES, Lab, Project, Sample
from bmh_sample_tracker.users.tests.factories import UserFactory


class LabFactory(DjangoModelFactory):
    lab_name = Faker("company")
    lab_contact = Faker("email")
    lab_notes = Faker("text")

    class Meta:
        model = Lab

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        lab = super()._create(model_class, *args, **kwargs)

        # Create a group associated with this lab
        Group.objects.get_or_create(name=lab.lab_name)

        return lab


class ProjectFactory(DjangoModelFactory):
    project_name = Faker("word")
    project_lead = SubFactory(UserFactory)
    project_description = Faker("paragraph")
    supporting_lab = SubFactory(LabFactory)

    class Meta:
        model = Project


class SampleFactory(DjangoModelFactory):
    sample_id = Faker("uuid4")
    sample_name = Faker("user_name")
    tube_plate_label = Faker("bothify", text="Tube-##??", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    submitting_lab = SubFactory(LabFactory)
    sample_type = Faker("random_element", elements=[choice[0] for choice in SAMPLE_TYPE_CHOICES])
    sample_volume_in_ul = Faker("pyfloat", positive=True)
    requested_services = Faker("paragraph")
    genus = Faker("word")
    species = Faker("word")

    # Optional fields
    well = Faker("bothify", text="?##", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    bmh_project = SubFactory(ProjectFactory)
    submitter_project = Faker("word")
    strain = Faker("word")
    isolate = Faker("word")
    subspecies_subtype_lineage = Faker("sentence")
    approx_genome_size_in_bp = Faker("pyint")
    comments = Faker("paragraph")
    culture_date = Faker("date")
    culture_conditions = Faker("paragraph")
    dna_extraction_date = Faker("date")
    dna_extraction_method = Faker("sentence")
    qubit_concentration_in_ng_ul = Faker("pyfloat", positive=True)

    class Meta:
        model = Sample
