# Generated by Django 4.1.9 on 2023-05-24 18:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Aliquot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("aliquot_volume_in_ul", models.FloatField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Aliquot",
                "verbose_name_plural": "Aliquots",
            },
        ),
        migrations.CreateModel(
            name="AliquotWorkflowExecution",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[("IN_PROGRESS", "In Progress"), ("COMPLETE", "Complete"), ("FAIL", "Fail")],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("aliquot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.aliquot")),
            ],
            options={
                "verbose_name": "Workflow Execution",
                "verbose_name_plural": "Workflow Executions",
            },
        ),
        migrations.CreateModel(
            name="Batch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("batch_name", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name": "Batch",
                "verbose_name_plural": "Batches",
            },
        ),
        migrations.CreateModel(
            name="Workflow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("workflow_name", models.CharField(max_length=50, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Workflow",
                "verbose_name_plural": "Workflows",
            },
        ),
        migrations.CreateModel(
            name="Result",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "aliquot_workflow_execution",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="api.aliquotworkflowexecution"
                    ),
                ),
            ],
            options={
                "verbose_name": "Result",
                "verbose_name_plural": "Results",
            },
        ),
        migrations.CreateModel(
            name="HistoricalWorkflow",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created", models.DateTimeField(blank=True, editable=False)),
                ("modified", models.DateTimeField(blank=True, editable=False)),
                ("workflow_name", models.CharField(db_index=True, max_length=50)),
                ("description", models.TextField(blank=True, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Workflow",
                "verbose_name_plural": "historical Workflows",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalResult",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created", models.DateTimeField(blank=True, editable=False)),
                ("modified", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "aliquot_workflow_execution",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="api.aliquotworkflowexecution",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Result",
                "verbose_name_plural": "historical Results",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalBatch",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created", models.DateTimeField(blank=True, editable=False)),
                ("modified", models.DateTimeField(blank=True, editable=False)),
                ("batch_name", models.CharField(max_length=100)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Batch",
                "verbose_name_plural": "historical Batches",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalAliquotWorkflowExecution",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created", models.DateTimeField(blank=True, editable=False)),
                ("modified", models.DateTimeField(blank=True, editable=False)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[("IN_PROGRESS", "In Progress"), ("COMPLETE", "Complete"), ("FAIL", "Fail")],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "aliquot",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="api.aliquot",
                    ),
                ),
                (
                    "batch",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="api.batch",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workflow",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="api.workflow",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Workflow Execution",
                "verbose_name_plural": "historical Workflow Executions",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalAliquot",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created", models.DateTimeField(blank=True, editable=False)),
                ("modified", models.DateTimeField(blank=True, editable=False)),
                ("aliquot_volume_in_ul", models.FloatField(blank=True, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "batch",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="api.batch",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sample",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="api.sample",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Aliquot",
                "verbose_name_plural": "historical Aliquots",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name="aliquotworkflowexecution",
            name="batch",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.batch"),
        ),
        migrations.AddField(
            model_name="aliquotworkflowexecution",
            name="workflow",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.workflow"),
        ),
        migrations.AddField(
            model_name="aliquot",
            name="batch",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.batch"),
        ),
        migrations.AddField(
            model_name="aliquot",
            name="sample",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.sample"),
        ),
    ]
