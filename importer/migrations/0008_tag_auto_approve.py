# Generated by Django 3.1.7 on 2021-02-27 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0007_post_creation_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='auto_approve',
            field=models.BooleanField(default=False),
        ),
    ]
