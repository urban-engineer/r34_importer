# Generated by Django 3.1.7 on 2021-02-27 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0002_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tag_notes',
            field=models.TextField(blank=True),
        ),
    ]
