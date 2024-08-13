from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from simple_history.models import HistoricalRecords

from bmh_sample_tracker.users.models import User

# Sensible field sizes for CharField columns
LG_CHAR = 250
SM_CHAR = 50
MIN_CHAR = 1

SAMPLE_TYPE_CHOICES = [
    ("CELLS", "Cells (in DNA/RNA shield)"),
    ("DNA", "DNA"),
    ("RNA", "RNA"),
    ("AMPLICON", "Amplicon - details in comments"),
    ("PREPARED_LIBRARY", "Prepared Library - details in comments"),
    ("OTHER", "Other - details in comments"),
]


alphanumeric_underscore_hyphen_regex = r"^[a-zA-Z0-9_-]+$"
alphanumeric_underscore_hyphen_validator = RegexValidator(
    regex=alphanumeric_underscore_hyphen_regex,
    message="Field should only contain alphanumeric characters, underscores, and dashes.",
)
alphabetic_regex = r"^[a-zA-Z]+$"
alphabetic_validator = RegexValidator(
    regex=alphabetic_regex, message="Field should only contain alphabetic characters"
)


def well_validator(value):
    if value is None or value == "":
        return
    well_regex = r"^[A-Z]\d{2}$"
    validator = RegexValidator(
        regex=well_regex,
        message=f"Well should be a capital letter followed by a two-digit number (e.g., A01, B02, etc.) You provided: {value}",  # noqa: E501
    )
    validator(value)


def min_length_validator(value):
    if len(value) < MIN_CHAR:
        raise ValidationError(f"Text should have a minimum length of {MIN_CHAR} characters.")


def generate_sample_id() -> str:
    """
    Method to generate a default sample ID for the Sample model.
    Returns format as LIMS-YYYY-XXXXXX. This method will always
    return the greatest sample pk value in the database + 1.
    """
    last_sample = Sample.objects.all().last()
    id_ = 1
    if last_sample is not None:
        id_ = last_sample.id + 1
    return f"LIMS-{datetime.now().year}-{id_:06}"


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-
    updating ``created`` and ``modified`` fields.
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Lab(TimeStampedModel):
    """
    Model to store labs that submit to the LIMS
    """

    lab_name = models.CharField(max_length=SM_CHAR)  # e.g. Virology, Salmonella
    lab_contact = models.EmailField(max_length=SM_CHAR)
    lab_notes = models.TextField(blank=True, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.lab_name}"

    class Meta:
        verbose_name = "Lab"
        verbose_name_plural = "Labs"


class Project(TimeStampedModel):
    project_name = models.CharField(max_length=SM_CHAR)
    project_lead = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    project_description = models.TextField(blank=True, null=True)
    supporting_lab = models.ForeignKey(Lab, on_delete=models.CASCADE, blank=True, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.project_name} (Lab: {self.supporting_lab})"

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"


class Sample(TimeStampedModel):
    """
    Model to store individual samples
    """

    # required fields
    sample_id = models.CharField(max_length=SM_CHAR, default=generate_sample_id)
    sample_name = models.CharField(
        max_length=SM_CHAR, validators=[min_length_validator, alphanumeric_underscore_hyphen_validator]
    )
    tube_plate_label = models.CharField(max_length=SM_CHAR)  # OR PLATE NAME FOR PLATES
    submitting_lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    sample_type = models.CharField(max_length=SM_CHAR, choices=SAMPLE_TYPE_CHOICES)
    sample_volume_in_ul = models.FloatField()
    requested_services = models.TextField(max_length=LG_CHAR)
    genus = models.CharField(max_length=SM_CHAR, validators=[alphabetic_validator])
    species = models.CharField(max_length=SM_CHAR, validators=[alphabetic_validator])

    # optional fields
    well = models.CharField(max_length=SM_CHAR, blank=True, null=True, validators=[well_validator])
    submitter_project = models.CharField(max_length=SM_CHAR, null=True, blank=True)
    bmh_project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    strain = models.CharField(max_length=SM_CHAR, null=True, blank=True)
    isolate = models.CharField(max_length=SM_CHAR, null=True, blank=True)
    subspecies_subtype_lineage = models.CharField(max_length=LG_CHAR, null=True, blank=True)
    approx_genome_size_in_bp = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    culture_date = models.DateField(blank=True, null=True)
    culture_conditions = models.TextField(blank=True, null=True)
    dna_extraction_date = models.DateField(blank=True, null=True)
    dna_extraction_method = models.TextField(blank=True, null=True)
    qubit_concentration_in_ng_ul = models.FloatField(blank=True, null=True)
    received = models.BooleanField(blank=True, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.sample_id}: {self.sample_name}"

    class Meta:
        verbose_name = "Sample"
        verbose_name_plural = "Samples"


class Batch(TimeStampedModel):
    """
    Model to store a batch of aliquots that are processed together
    """

    batch_name = models.CharField(max_length=100)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id}: {self.batch_name}"

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"


class Aliquot(TimeStampedModel):
    """
    Model to store aliquots taken from a sample.
    """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    aliquot_volume_in_ul = models.FloatField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.aliquot_volume_in_ul} uL aliquot of {self.sample.sample_id}"

    class Meta:
        verbose_name = "Aliquot"
        verbose_name_plural = "Aliquots"


class Workflow(TimeStampedModel):
    """
    Model to store workflows and their relevant data
    """

    workflow_name = models.CharField(max_length=SM_CHAR, unique=True)  # e.g. "DNA extraction"
    description = models.TextField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.workflow_name}"

    class Meta:
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"


class WorkflowExecution(TimeStampedModel):
    """
    Model to store the execution of a workflow on a batch of aliquots and its status
    """

    aliquot = models.ForeignKey(Aliquot, on_delete=models.CASCADE)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=SM_CHAR,
        choices=(
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETE", "Complete"),
            ("FAIL", "Fail"),
        ),
        null=True,
        blank=True,
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id}: {self.workflow}"

    class Meta:
        verbose_name = "Workflow Execution"
        verbose_name_plural = "Workflow Executions"
