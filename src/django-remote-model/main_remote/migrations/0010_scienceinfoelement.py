# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0009_auto_20150928_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScienceInfoElement',
            fields=[
                ('identifier', models.CharField(primary_key=True, serialize=False, max_length=255)),
                ('h_index', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
