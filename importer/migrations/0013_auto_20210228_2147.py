# Generated by Django 3.1.7 on 2021-03-01 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0012_tag_import_timestamp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['tag_category', 'tag_name']},
        ),
        migrations.AlterField(
            model_name='post',
            name='file_url',
            field=models.CharField(default=None, max_length=256),
        ),
        migrations.AlterField(
            model_name='post',
            name='preview_url',
            field=models.CharField(default=None, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='sample_url',
            field=models.CharField(default=None, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='source_url',
            field=models.CharField(default=None, max_length=256),
        ),
    ]
