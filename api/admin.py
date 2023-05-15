from django.contrib import admin

from .models import Lab, Project, Sample

admin.site.register(Lab)
admin.site.register(Project)
admin.site.register(Sample)
