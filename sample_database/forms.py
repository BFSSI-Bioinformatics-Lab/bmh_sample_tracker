from django.forms import ModelForm

from api.models import WorkflowBatch


class WorkflowAssignmentForm(ModelForm):
    class Meta:
        model = WorkflowBatch
        fields = ["workflow", "sample", "status"]
