# Generated by Django 3.1.7 on 2021-02-28 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0009_auto_20210227_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='sample_url',
            field=models.URLField(default=None, null=True),
        ),
    ]
