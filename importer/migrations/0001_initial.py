# Generated by Django 3.1.7 on 2021-02-24 21:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.IntegerField()),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), size=None)),
            ],
        ),
    ]