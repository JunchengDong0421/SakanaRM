# Generated by Django 4.2.11 on 2024-05-26 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("core", "0005_rename_description_tag_definition"),
    ]

    operations = [
        migrations.AddField(
            model_name="tag",
            name="adder",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="accounts.sakanauser",
            ),
            preserve_default=False,
        ),
    ]