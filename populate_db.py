# This is a script for testing purposes that populates the database with sample labs, projects, and workflows
# It could be used to set up the production DB but would need additional fields to be populated

import pandas as pd
from django.contrib.auth.models import Group

from api.models import Lab, Project, Workflow

excelfile = "lims_test_sample_sheet.xlsx"

# labs
lab_df = pd.read_excel(excelfile, sheet_name="submitting_lab_List")
for _, row in lab_df.iterrows():
    lab_name = row["submitting_lab"]
    lab_contact = row["lab_contact"]

    lab_object, created = Lab.objects.get_or_create(
        lab_name=lab_name,
        lab_contact=lab_contact,
    )
    # Create a group assoicated with that lab
    group_object, created = Group.objects.get_or_create(
        name=lab_name,
    )


# projects
project_df = pd.read_excel(excelfile, sheet_name="ProjectID_List")

for _, row in project_df.iterrows():
    lab_name = row["Lab"]
    supporting_lab, _ = Lab.objects.get_or_create(lab_name=lab_name)
    project_name = row["ProjectIDs in Portal"]
    project_object, created = Project.objects.get_or_create(
        project_name=project_name,
        supporting_lab=supporting_lab,
    )


# workflows
wf_df = pd.read_excel(excelfile, sheet_name="requested_services_list")

wf_list = wf_df["requested_services"]

for wf in wf_list:
    wf_object, created = Workflow.objects.get_or_create(
        workflow_name=wf,
    )
