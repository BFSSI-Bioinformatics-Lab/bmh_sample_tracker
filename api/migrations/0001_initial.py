# Generated by Django 4.1.9 on 2023-05-15 18:48

import api.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('lab_name', models.CharField(max_length=50)),
                ('lab_contact', models.EmailField(max_length=50)),
                ('lab_notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Lab',
                'verbose_name_plural': 'Labs',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('project_name', models.CharField(max_length=50)),
                ('project_description', models.TextField(blank=True, null=True)),
                ('project_lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('supporting_lab', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.lab')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('sample_id', models.CharField(default=api.models.generate_sample_id, max_length=50)),
                ('sample_name', models.CharField(max_length=50)),
                ('well', models.CharField(blank=True, max_length=50, null=True)),
                ('sample_type', models.CharField(blank=True, choices=[('CELLS', 'Cells (in DNA/RNA shield)'), ('DNA', 'DNA'), ('AMPLICON', 'Amplicon'), ('OTHER', 'Other')], max_length=50, null=True)),
                ('sample_volume_in_ul', models.FloatField(blank=True, null=True)),
                ('requested_services', models.TextField(blank=True, null=True)),
                ('strain', models.CharField(blank=True, max_length=50, null=True)),
                ('isolate', models.CharField(blank=True, max_length=50, null=True)),
                ('genus', models.CharField(blank=True, max_length=50, null=True)),
                ('species', models.CharField(blank=True, max_length=50, null=True)),
                ('subspecies_subtype_lineage', models.CharField(blank=True, max_length=50, null=True)),
                ('approx_genome_size_in_bp', models.IntegerField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('culture_date', models.DateField(blank=True, null=True)),
                ('culture_conditions', models.TextField(blank=True, null=True)),
                ('dna_extraction_date', models.DateField(blank=True, null=True)),
                ('dna_extraction_method', models.CharField(blank=True, max_length=50, null=True)),
                ('qubit_concentration_in_ng_ul', models.FloatField(blank=True, null=True)),
                ('submitter_project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.project')),
                ('submitting_lab', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.lab')),
            ],
            options={
                'verbose_name': 'Sample',
                'verbose_name_plural': 'Samples',
            },
        ),
        migrations.CreateModel(
            name='HistoricalSample',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('sample_id', models.CharField(default=api.models.generate_sample_id, max_length=50)),
                ('sample_name', models.CharField(max_length=50)),
                ('well', models.CharField(blank=True, max_length=50, null=True)),
                ('sample_type', models.CharField(blank=True, choices=[('CELLS', 'Cells (in DNA/RNA shield)'), ('DNA', 'DNA'), ('AMPLICON', 'Amplicon'), ('OTHER', 'Other')], max_length=50, null=True)),
                ('sample_volume_in_ul', models.FloatField(blank=True, null=True)),
                ('requested_services', models.TextField(blank=True, null=True)),
                ('strain', models.CharField(blank=True, max_length=50, null=True)),
                ('isolate', models.CharField(blank=True, max_length=50, null=True)),
                ('genus', models.CharField(blank=True, max_length=50, null=True)),
                ('species', models.CharField(blank=True, max_length=50, null=True)),
                ('subspecies_subtype_lineage', models.CharField(blank=True, max_length=50, null=True)),
                ('approx_genome_size_in_bp', models.IntegerField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('culture_date', models.DateField(blank=True, null=True)),
                ('culture_conditions', models.TextField(blank=True, null=True)),
                ('dna_extraction_date', models.DateField(blank=True, null=True)),
                ('dna_extraction_method', models.CharField(blank=True, max_length=50, null=True)),
                ('qubit_concentration_in_ng_ul', models.FloatField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('submitter_project', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='api.project')),
                ('submitting_lab', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='api.lab')),
            ],
            options={
                'verbose_name': 'historical Sample',
                'verbose_name_plural': 'historical Samples',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProject',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('project_name', models.CharField(max_length=50)),
                ('project_description', models.TextField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('project_lead', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('supporting_lab', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='api.lab')),
            ],
            options={
                'verbose_name': 'historical Project',
                'verbose_name_plural': 'historical Projects',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalLab',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False)),
                ('lab_name', models.CharField(max_length=50)),
                ('lab_contact', models.EmailField(max_length=50)),
                ('lab_notes', models.TextField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Lab',
                'verbose_name_plural': 'historical Labs',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]