from django.contrib import admin

from .models import Lab, Project, Sample, Workflow, WorkflowBatch

admin.site.register(Lab)
admin.site.register(Project)
admin.site.register(Sample)
admin.site.register(Workflow)
admin.site.register(WorkflowBatch)
