# Generated by Django 4.2.11 on 2024-05-22 08:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_workflow_result"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tag", old_name="description", new_name="definition",
        ),
    ]