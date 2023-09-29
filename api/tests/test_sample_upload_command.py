from io import BytesIO
from tempfile import NamedTemporaryFile

import pandas as pd
import pytest
from django.core.management import call_command
from factories import LabFactory, ProjectFactory

from api.models import Sample


@pytest.fixture
def excel_data():
    lab = LabFactory()
    project = ProjectFactory()
    # Create a dataframe with the required fields.
    data = {
        "sample_name": ["Sample1", "Sample2"],
        "well": ["A01", "A02"],
        "tube_plate_label": ["S1", "S2"],
        "sample_type": ["Cells (in DNA/RNA shield)", "Cells (in DNA/RNA shield)"],
        "submitting_lab": [lab.lab_name, lab.lab_name],
        "sample_volume_in_ul": [10, 20],
        "bmh_project": [project.project_name, project.project_name],
        "requested_services": ["Illumina WGS", "Illumina WGS"],
        "strain": ["Strain1", "Strain2"],
        "isolate": ["Isolate1", "Isolate2"],
        "genus": ["Escherichia", "Escherichia"],
        "species": ["coli", "coli"],
        "subspecies_subtype_lineage": ["Lineage1", "Lineage2"],
        "approx_genome_size_in_bp": [1000, 2000],
        "culture_date": pd.to_datetime(["2021-01-01", "2021-01-02"]),
        "culture_conditions": ["", None],
        "dna_extraction_date": pd.to_datetime(["2021-01-03", "2021-01-04"]),
        "dna_extraction_method": ["Method1", "Method2"],
        "qubit_concentration_in_ng_ul": [1.0, 2.0],
    }
    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="SSS-Template", index=False)
    excel_data = output.getvalue()
    output.close()
    yield excel_data


@pytest.mark.django_db
def test_upload_command(excel_data):
    with NamedTemporaryFile(suffix=".xlsx") as temp_file:
        temp_file.write(excel_data)
        temp_file.flush()

        call_command("upload_samples", temp_file.name)

        samples = Sample.objects.all()
        assert len(samples) == 2
        assert samples[0].sample_name == "Sample1"
        assert samples[1].sample_name == "Sample2"
