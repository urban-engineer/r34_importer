# Generated by Django 3.1.7 on 2021-02-27 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0003_auto_20210226_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='file_url',
            field=models.URLField(default=None),
        ),
        migrations.AddField(
            model_name='post',
            name='md5_hash',
            field=models.CharField(default='zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', max_length=32),
        ),
        migrations.AddField(
            model_name='post',
            name='sample_height',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='post',
            name='sample_url',
            field=models.URLField(default=None),
        ),
        migrations.AddField(
            model_name='post',
            name='sample_width',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='post',
            name='source_url',
            field=models.URLField(default=None),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_id',
            field=models.IntegerField(default=-1),
        ),
    ]
