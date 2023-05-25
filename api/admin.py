from django.contrib import admin

from .models import Aliquot, Batch, Lab, Project, Sample, Workflow

admin.site.register(Lab)
admin.site.register(Project)
admin.site.register(Sample)
admin.site.register(Batch)
admin.site.register(Aliquot)
admin.site.register(Workflow)
