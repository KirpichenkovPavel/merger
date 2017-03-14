# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0002_location_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicRank',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('name', models.CharField(verbose_name='название', max_length=500)),
                ('short_name', models.CharField(verbose_name='сокращённое название', max_length=500, null=True)),
                ('full_name', models.CharField(verbose_name='полное название', max_length=500, null=True)),
            ],
            options={
                'verbose_name': 'академическое звание',
                'managed': False,
                'verbose_name_plural': 'академические звания',
                'abstract': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
