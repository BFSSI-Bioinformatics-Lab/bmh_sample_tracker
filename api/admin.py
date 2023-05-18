from django.contrib import admin

from .models import Aliquot, AliquotWorkflowExecution, Batch, Lab, Project, Sample, Workflow

admin.site.register(Lab)
admin.site.register(Project)
admin.site.register(Sample)
admin.site.register(Workflow)
admin.site.register(Batch)
admin.site.register(Aliquot)
admin.site.register(AliquotWorkflowExecution)
