# Generated by Django 3.1.7 on 2021-02-27 23:03

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0005_post_imported'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='imported_tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), default=list, size=None),
        ),
    ]